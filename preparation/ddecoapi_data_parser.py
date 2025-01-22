"""
ddecoapidataparser script to request data from the DD-ECO-API
"""

"""
File: ddecoapidataparser.py
Author: Wouter Abels (wouter.abels@rws.nl)
# Creation date: 16-06-21
Last modification: 20-02-2022
Python ver: 3.12.1
"""
import logging

import numpy as np
import pandas as pd
import requests

from preparation.utility import stop_script


logger = logging.getLogger(__name__)


class dataparser:
    """
    Class to handle all related to the dd-eco-api request.
    """

    __slots__ = (
        "aquadesk_url",
        "api_key",
        "query_url",
        "query_filter",
        "skip_properties",
        "page_number",
        "page_size",
    )

    def __init__(
        self,
        aquadesk_url: str = None,
        api_key: str = None,
        query_url: str = None,
        query_filter: str = None,
        skip_properties: str = None,
        page_number: int = 1,
        page_size: int = 10000,
    ):
        """Constructs all the necessary attributes for the dataparser object.

        Args:
            aquadesk_url (str, required): Standard API url for querying
            api_key: (str, optional): API key required for Aquadesk measurements, not required for taxa-info.
            query_url (str, required): API endpoint for query
            query_filter (str, optional): Filtering within API. Defaults to None.
            skip_properties (str, optional): Properties to skip in response. Defaults to None.
            page_number (int, optional): Starting page number. Defaults to 1.
            page_size (int, optional): Default max page size. Defaults to 10000.
        """
        self.aquadesk_url = aquadesk_url
        self.api_key = api_key
        self.query_url = query_url
        self.query_filter = query_filter
        self.skip_properties = skip_properties
        self.page_number = page_number
        self.page_size = page_size

    def http_error_check(self, e: requests.status_codes) -> bool:
        """Function to check HTTP error from API

        Args:
            e (requests.status_codes, optional): HTTP error from API. Defaults to None

        Returns:
            bool: True for break in while loop.
        """
        if e.response.status_codes == 403:
            logger.error("Invalid api key")
            stop_script()
            # return True
        else:
            logger.error(f"Error: {e.reason}")
            stop_script()
            # return True

    def url_builder(self) -> str:
        """Builds query url for every page with defined endpoint, filters and skip properties

        Returns:
            str: base
        """

        base = f"{self.aquadesk_url + self.query_url}?page={self.page_number}&pagesize={self.page_size}"
        if self.query_filter is not None:
            base = f"{base}&filter={self.query_filter}"
        if self.skip_properties is not None:
            base = f"{base}&skipproperties={self.skip_properties}"
        base = base.replace(" ", "%20")
        return base

    def check_ending(self, response: list) -> bool:
        """Check if ending of the response pages is reached (Response size smaller than max page size)

        Args:
            response (list,optional: Response list from query. Defaults to None.
        Returns:
            bool: length of response against pagesize
        """

        paging = response["paging"]
        page = int(paging["self"].split("page=")[1].split("&")[0])
        pagesize = int(paging["self"].split("pagesize=")[1].split("&")[0])
        objectcount = int(paging["totalObjectCount"])

        logger.debug(f"Page: {page}")
        remaining = objectcount - (pagesize * page)

        if remaining > 0:
            logger.debug(f"Download remaining: {remaining} rows")
        else:
            logger.info(f"Download complete: {objectcount} rows")

        if page * pagesize < objectcount:
            return False
        else:
            return True

    def return_query(self) -> list:
        """Returns query from api, for testing and discovery purposes, Returns json result.

        Returns:
            list: query result
        """
        request_url = self.url_builder()

        try:
            request = requests.get(
                request_url,
                headers={"Accept": "application/json", "x-api-key": self.api_key},
                timeout=120,
            ).json()
            return request["result"]
        except requests.HTTPError as e:
            self.http_error_check(e)

    def parse_data_dump(self, parse_watertypes=False):
        """Parse through all pages and send to path file location as csv.

        Args:
            parse_watertypes (list, optional): Used to parse watertypes column into split columns. Defaults to False.

        Returns:
            _type_: _description_
        """

        json_request_list = []
        while True:
            request_url = self.url_builder()

            try:
                request = requests.get(
                    request_url,
                    headers={"Accept": "application/json", "x-api-key": self.api_key},
                    timeout=120,
                ).json()

                response = request["result"]
                json_request_list.extend(response)

                if self.check_ending(request):
                    return self.return_dataframe(json_request_list, parse_watertypes)

                self.page_number += 1

            except requests.HTTPError as e:
                if self.http_error_check(e):
                    print(e)
                    break

    def return_dataframe(
        self, json_object: list, parse_watertypes: bool
    ) -> pd.DataFrame:
        """Returns dataframe and parses watertypes column if it is in the set.

        Args:
            json_object (list): Json object from aquadesk API
            parse_watertypes (bool): Selected watertypes

        Returns:
            pd.DataFrame: Pandas Dataframe of query
        """
        df = pd.json_normalize(json_object)
        if ("watertypes" in df.columns) & (parse_watertypes is True):
            watertypes_nan_dict = {
                "classificationsystem": np.nan,
                "watertypecode": np.nan,
            }
            return pd.concat(
                [
                    df.drop("watertypes", axis=1),
                    pd.json_normalize(
                        df["watertypes"].apply(
                            lambda x: x[0]
                            if isinstance(x, list)
                            else watertypes_nan_dict
                        )
                    ),
                ],
                axis=1,
            )
        else:
            return df
