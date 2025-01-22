"""Handles the queries for Aquadesk in the yaml."""

"""
# File: benthos_data_helpers.py
# Author(s): M. Japink (m.japink@waardenburg.eco) & J. Haringa (j.haringa@waardenburg.eco)
# Creation date: 21-01-2023
# Last modification: 20-02-2024
# Python v3.12.1
"""

import ast
import logging
import os


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))

from preparation import read_system_config


# Initializing logger object to write custom logs
logger = logging.getLogger(__name__)


def split_query_filter_to_dictionary():
    """Splits the Aquadesk yaml query filter to a dictionary of filters.

    Returns:
        dict: dictionary with columnmn names as keys and filter values as string or list.
    """

    # read measuremenst.query_filter from aquadesk.yaml
    query_filter = read_system_config.read_yaml_configuration(
        "measurements.query_filter", "aquadesk.yaml"
    )

    # clean the yaml string to an dictionary with the query filters items.
    query_filter = query_filter.split(";")
    query_filter = [x.strip() for x in query_filter]
    query_filter.pop()
    query_filter = [x.split(":") for x in query_filter]
    dict_query_filter = dict(map(lambda x: x[::2], query_filter))
    dict_query_filter = {k.split("_")[0]: v for k, v in dict_query_filter.items()}

    for key, value in dict_query_filter.items():
        try:
            # Use the ast.literal_eval function to safely evaluate the string as a Python literal
            dict_query_filter[key] = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            # If there's an error in evaluating, just leave the value as is
            pass
        # Check if the value is a list, and convert it if it's not
    for key, value in dict_query_filter.items():
        try:
            # Use the ast.literal_eval function to safely evaluate the string as a Python literal
            if not isinstance(value, list):
                value = [value]
                dict_query_filter[key] = value
        except (ValueError, SyntaxError):
            # If there's an error in evaluating, just leave the value as is
            pass
    return dict_query_filter


def rename_query_filter_columns(dict_query_filter: dict) -> dict:
    """Renames the Aquadesk query_filter column names from api_names to script names.

    Args:
        query_filter_dict (dict): the query_filter string from the yaml file.

    Returns:
        pd.DataFrame: the updated DataFrame.
    """

    # set column_mapping to dictionary
    df_req_columns = read_system_config.read_column_mapping()
    df_req_columns = df_req_columns.drop(columns=["not_null"])
    dict_req_columns = dict(
        zip(df_req_columns["api_name"], df_req_columns["script_name"])
    )
    # match query_filter_dict keys to req_columns api_name and convert to script_name

    # Create a new dictionary with renamed keys
    dict_query_filter_renamed = {
        dict_req_columns.get(key, key): value
        for key, value in dict_query_filter.items()
    }
    return dict_query_filter_renamed
