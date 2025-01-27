"""Script to import the aquadesk data."""

"""
# File: aquadesk.py
# Author(s): M. Japink (m.japink@waardenburg.eco) & J. Haringa (j.haringa@waardenburg.eco) & W. Abels (wouter.abels@rws.nl)
# Creation date: 21-01-2023
# Last modification: 27-01-2025
# Python v3.12.1
"""

import json
import logging
import os
import typing

import numpy as np
import pandas as pd


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))

from preparation import ddecoapi_data_parser
from preparation import log_decorator
from preparation import read_system_config
from preparation import utility


# Initializing logger object to write custom logs
logger = logging.getLogger(__name__)


@log_decorator.log_factory(__name__)
def build_request() -> typing.Any:
    """Reads all the configurations for the dataparser ddecoapi.

    Returns:
        DataParser: the api code for the request.
    """

    config_yaml = "aquadesk.yaml"

    aquadesk_url = read_system_config.read_yaml_configuration(
        "aquadesk_url", config_yaml
    )
    api_key = read_system_config.read_yaml_configuration("api_key", config_yaml)
    query_url = read_system_config.read_yaml_configuration(
        "measurements.query_url", config_yaml
    )

    skip_properties = read_system_config.read_skipped_columns()
    page_size = read_system_config.read_yaml_configuration(
        "measurements.page_size", config_yaml
    )

    logger.debug(skip_properties)
    logger.debug(query_url)

    logger.debug(page_size)
    logger.debug(api_key)
    logger.debug(aquadesk_url)

    ddecoapi = ddecoapi_data_parser.dataparser(
        aquadesk_url=aquadesk_url,
        api_key=api_key,
        query_url=query_url,
        skip_properties=skip_properties,
        page_size=page_size,
    )

    return ddecoapi


@log_decorator.log_factory(__name__)
def aquadesk_download(projects: list[str], locations: list[str]) -> bool:
    """Downloads the Aquadesk data based on the user configured settings and exports result to csv.

    Args:
        projects (list[str]): list of project codes
        locations (list[str]): list of measurementobject codes

    Returns:
        bool: True if succesful, False if not

    """
    config_yaml = "aquadesk.yaml"
    query_filter = read_system_config.read_yaml_configuration(
        "measurements.query_filter", config_yaml
    )

    print("Aquadesk download")
    print("Aantal locaties voor Aquadesk download: " + str(len(locations)))
    aquadesk_result = pd.DataFrame([])
    chunk_size = 20

    for i in range(0, len(locations), chunk_size):
        try:
            request = build_request()
        except Exception:
            logger.error(
                "Er treed een fout op bij het opbouwen van het API request. \
                    Controleer de configuratiebestaden op format-/typefouten."
            )
            logger.debug("Error Message with %s", "arguments", exc_info=True)
            exit()

        chunk = locations[i : i + chunk_size]
        locations_filter = (
            "measurementobject:in:" + json.dumps(chunk, separators=(",", ":")) + ";"
        )
        try:
            request.query_filter = query_filter + locations_filter
            # aquadesk_result =+ request.parse_data_dump()
            part = request.parse_data_dump()

            aquadesk_result = pd.concat([aquadesk_result, part])
        except Exception:
            logger.error(
                f"Vermoedelijk zit er een voor de Aquadesk-api onbekende locatiecode in {locations}"
            )
            logger.debug("Error Message with %s", "arguments", exc_info=True)

    data_path = read_system_config.read_yaml_configuration(
        "data_path", "global_variables.yaml"
    )
    aquadesk_result = clean_aquadesk_data(projects, aquadesk_result)

    # rename columns
    column_mapping = read_system_config.read_column_mapping()
    aquadesk_result = aquadesk_result.rename(
        columns=dict(zip(column_mapping.api_name, column_mapping.script_name))
    )

    print(f"Download {len(aquadesk_result)} records: gereed")

    remove_file(os.path.join(data_path, "aquadesk_download.xlsx"))
    if len(aquadesk_result) > 0:
        try:
            aquadesk_result.to_excel(
                os.path.join(data_path, "aquadesk_download.xlsx"), index=False
            )
            logger.info("Aquadesk data succesvol gedownload.")
            return True
        except Exception:
            logger.error("Vermoedelijk staat de eerder gedownloade excelfile nog open.")
            logger.debug("Error Message with %s", "arguments", exc_info=True)
            return False
    else:
        logger.error("Geen data gedownload van Aquadesk.")
        utility.stop_script()
        return False


@log_decorator.log_factory(__name__)
def clean_aquadesk_data(projects, aquadesk: pd.DataFrame) -> pd.DataFrame:
    """Cleans the Aquadesk data (e.g. devices and ecotopes).

    Args:
        aquadesk (pd.DataFrame): the downloaded Aquadesk data.

    Returns:
        pd.DataFrame: the cleaned Aquadesk data.
    """
    # merge classified_value and sampling devices
    if "classifiedvalue" in aquadesk:
        aquadesk["samplingdevices"] = np.where(
            (aquadesk["classifiedvalue"].notna())
            & (aquadesk["samplingdevices"].isna()),
            aquadesk["classifiedvalue"],
            aquadesk["samplingdevices"],
        )
    else:
        logger.info(
            "'classifiedvalue' niet in de gedownloade aquadesk kolommen (omdat leeg)."
        )

    # transform the format of the ecotopes column
    if "ecotopes" in aquadesk:
        aquadesk = aquadesk.explode("ecotopes")
        aquadesk["ecotopes"] = aquadesk["ecotopes"].apply(
            lambda ecotopes: f"{ecotopes['system']}={ecotopes['code']}"
            if isinstance(ecotopes, dict)
            else pd.NA
        )
    else:
        aquadesk["ecotopes"] = pd.NA

    # retrieve sampling device
    if "samplingdevices" in aquadesk:
        aquadesk = aquadesk.explode("samplingdevices")  # unlist
        aquadesk["samplingdevices"] = aquadesk["samplingdevices"].str.extract(
            r"=(.*?)="
        )
    else:
        aquadesk["samplingdevices"] = pd.NA

    # unlist
    if "analysiscontext" in aquadesk:
        aquadesk = aquadesk.explode("analysiscontext")
    else:
        aquadesk["analysiscontext"] = pd.NA
        logger.warning("Geen analysiscontext in de Aquadesk download.")

    if "projects" in aquadesk:
        aquadesk = aquadesk.explode("projects")
        df = pd.DataFrame()
        for project in projects:
            if aquadesk["projects"].str.contains(project).any():
                dataperproject = aquadesk[aquadesk['projects'].str.contains(project)]
                aquadesk = pd.concat([df,dataperproject])
    else:
        aquadesk["projects"] = pd.NA
        logger.error("Geen projects in de Aquadesk download.")
        utility.stop_script()

    return aquadesk


@log_decorator.log_factory(__name__)
def remove_file(filename: str) -> None:
    """Removes a file.

    Args:
        filename (str): the name of the file to be removed.
    """
    try:
        if os.path.exists(filename):
            os.remove(filename)
    except Exception:
        logger.error(f"Kan het bestand niet verwijderen: {filename}.")
        logger.debug("Error Message with %s", "arguments", exc_info=True)
