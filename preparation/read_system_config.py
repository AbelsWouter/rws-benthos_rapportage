"""Script to read the system configurations files."""

"""
# File: read_system_config.py
# Author(s): M. Japink (m.japink@waardenburg.eco) & J. Haringa (j.haringa@waardenburg.eco)
# Creation date: 21-01-2023
# Last modification: 20-02-2024
# Python v3.12.1
"""


import logging
import os
from typing import Any
from typing import List

import pandas as pd
from yaml import parser
from yaml import safe_load

from preparation import log_decorator
from preparation import utility


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))


logger = logging.getLogger(__name__)


def read_yaml_configuration(param_name: str, config_file: str) -> Any:
    """Reads a parameter setting from a yaml file

    Args:
        param_name (): parameter name
        config_file_path (str): path to the yaml file

    Returns:
        str: parameter value
    """
    filepath = os.path.join("./configs", config_file)
    if os.path.splitext(filepath)[-1].lower() != ".yaml":
        filepath = filepath + ".yaml"
        logging.warning("Please use the yaml extension in your code for readability!")

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            config = safe_load(file)
            param_hierarchy = param_name.split(".")
            param_value = config
            for param in param_hierarchy:
                if param_value is not None:
                    param_value = param_value.get(param)
    except FileNotFoundError as e:
        logger.error(f"Bestand {filepath} niet gevonden found.")
        logger.debug(f"{e} with %s", "arguments", exc_info=True)
        utility.stop_script()
    except parser.ParserError as e:
        logger.error(f"Error bestand lezen {filepath}.")
        logger.debug(f"{e} with %s", "arguments", exc_info=True)
        utility.stop_script()

    return param_value


def read_csv_file(filename: str) -> pd.DataFrame:
    """Reads the whole configuration file.

    Args:
        filename (str): The filename of the configuration file.

    Returns:
        pd.DataFrame: Dataframe with all configuration information
    """
    df = pd.DataFrame()
    try:
        df = pd.read_csv(filename, sep=";")
    except FileNotFoundError:
        logger.error(f"Bestand {filename} niet gevonden.")
        utility.stop_script()
    except IOError:
        logger.error(f"Error lezen bestand {filename}.")
        utility.stop_script()

    return df


@log_decorator.log_factory(__name__)
def read_meetobject_codes(waterbodies: list[str], projects: list[str]) -> Any:
    """Select the Meetobject_Code (measurementobject) for the waterbody from the waterbody.csv file.

    Args:
        waterbodies (list[str]): The waterbodies selected by the user.
        projects (list[str]): The projects selected by the user.

    Returns:
        list: A list of Measurement object codes.
    """
    df = read_locations_config(waterbodies, projects)
    meetobject_codes = df["Meetobject_Code"].values.tolist()
    meetobject_codes = [*set(meetobject_codes)]

    return meetobject_codes


@log_decorator.log_factory(__name__)
def read_locations_config(waterbodies: list[str], projects: list[str]) -> pd.DataFrame:
    """Select the rows for which the location is defined in the config locations.csv.

    Args:
        waterbodies (list[str]): The waterbodies selected by the user.
        projects (list[str]): The projects selected by the user.

    Returns:
        pd.DataFrame: The content of location.csv for the selected waterbodies.
    """
    df = read_csv_file(
        read_yaml_configuration("config_locations", "global_variables.yaml")
    )

    check = df[df["Waterlichaam"].isin(waterbodies)]
    if len(check) == 0:
        logger.error(f"Er zijn geen locaties bekend voor {waterbodies}.")
        utility.stop_script()

    check = df[df["Project_Code"].isin(projects)]
    if len(check) == 0:
        logger.error(f"Er zijn geen locaties bekend voor {projects}.")
        utility.stop_script()

    df_locations = df[
        (df["Waterlichaam"].isin(waterbodies)) & (df["Project_Code"].isin(projects))
    ]
    if len(df_locations) == 0:
        logger.error(
            f"Er zijn geen locaties bekend voor de combinatie {waterbodies} en {projects}."
        )
        utility.stop_script()
    else:
        logger.info(
            f"De door de gebruiker opgegeven waterlichamen zijn: {df_locations['Waterlichaam'].unique()}"
        )
        logger.info(
            f"De door de gebruiker opgegeven projecten die ook in het waterlichaam zitten zijn:"
            f"{df_locations['Project_Code'].unique()}"
        )
    return df_locations


@log_decorator.log_factory(__name__)
def read_waterbodies_config(waterbodies: list[str]) -> pd.DataFrame:
    """Select the rows for which the waterbodies are defined in the config waterbody.csv.

    Args:
        waterbodies (list[str]): The waterbodies selected by the user.

            Returns:
        pd.DataFrame: Dataframe of the waterbody.csv data for the selected waterbody.
    """
    df = read_csv_file(
        read_yaml_configuration("config_waterbodies", "global_variables.yaml")
    )

    select_waterbody_df = df[df["Waterlichaam"].isin(waterbodies)]
    return select_waterbody_df


@log_decorator.log_factory(__name__)
def read_bisi_config() -> pd.DataFrame:
    """Reads the configuration file for filling the BISI table.

    Returns:
        pd.DataFrame: Dataframe with the BISI configuration data.
    """
    df = read_csv_file(read_yaml_configuration("config_bisi", "global_variables.yaml"))
    return df


@log_decorator.log_factory(__name__)
def read_groups_config(trend_group: list[str]) -> pd.DataFrame:
    """Reads the configuration with groups information.

    Args:
        trend_group (str): The trend group for which the groups are needed.

    Returns:
        pd.DataFrame: Dataframe with the BISI configuration data.
    """
    # use colors from config file 'groepsindeling' for each group
    df_groups = read_csv_file(
        read_yaml_configuration("config_taxon_groups", "global_variables.yaml")
    )

    df_groups_filtered = df_groups[df_groups["Trendgroep"].isin(trend_group)]
    df_groups_filtered = df_groups_filtered[
        ["Trendgroep", "Groep", "Groepkleur"]
    ].drop_duplicates()

    return df_groups_filtered


@log_decorator.log_factory(__name__)
def read_column_mapping() -> pd.Series:
    """Reads the data model configuration file for mapping from api-column names to script-names (=Aquadesk-web).

    Returns:
        pd.DataFrame: Dataframe column name mapping and not null identifier.
    """
    df = read_csv_file(read_yaml_configuration("data_model", "global_variables.yaml"))
    df = df[["api_name", "script_name", "not_null", "benthos_import"]]
    df = df.dropna()
    df = df.loc[df["benthos_import"]]
    df = df[["api_name", "script_name", "not_null"]]
    return df


@log_decorator.log_factory(__name__)
def read_analysis_names() -> pd.DataFrame:
    """Reads the datamodel configuration file.

    Returns:
        pd.DataFrame: DataFrame with the total columns.
    """
    df = read_csv_file(read_yaml_configuration("data_model", "global_variables.yaml"))

    df = df[["analysis_name", "config"]]
    df = df.dropna()
    return df


@log_decorator.log_factory(__name__)
def read_skipped_columns() -> str:
    """Reads all the API columns which are not used in the script.

    Returns:
        str: list with the skipped columns.
    """
    df = read_csv_file(read_yaml_configuration("data_model", "global_variables.yaml"))
    df = df[["api_name", "benthos_import"]]
    df = df.dropna()
    df = df[df["benthos_import"] == False]
    df = df[["api_name"]]
    return ",".join(df["api_name"].tolist())


def read_sample_properties(column_name: str) -> List[str]:
    """Reads the columns which are used for the sample properties.

    Args:
        column_name (str): the column name read from the configuration.

    Returns:
        List[str]: columns which are true for the sample properties.
    """
    df = read_csv_file(read_yaml_configuration("data_model", "global_variables.yaml"))
    df = df[[column_name, "sample_property"]]
    df = df.dropna()
    df = df[df["sample_property"] == True]
    df = df[column_name]
    col_list = df.tolist()
    return col_list
