"""Data will be checked and written conform the TWN."""

"""
# File: twn.py
# Author(s): M. Japink (m.japink@waardenburg.eco) & J. Haringa (j.haringa@waardenburg.eco)
# Creation date: 5-07-2023
# Last modification: 20-02-2024
# Python v3.12.1
"""

import logging
import os
import typing

import numpy as np
import pandas as pd


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))

from preparation import check_decorator
from preparation import ddecoapi_data_parser
from preparation import log_decorator
from preparation import read_system_config
from preparation import utility


logger = logging.getLogger(__name__)


@log_decorator.log_factory(__name__)
def download_twn(test_clause: typing.Optional[bool] = False) -> pd.DataFrame:
    """Download TWN from Aquadesk api.

    Args:
        test_clause (bool): for pytest to just download one species.

    Returns:
        pd.DataFrame: a Pandas DataFrame with the TWN.
    """

    config_yaml = "aquadesk.yaml"
    aquadesk_url = read_system_config.read_yaml_configuration(
        "aquadesk_url", config_yaml
    )
    api_key = read_system_config.read_yaml_configuration("api_key", config_yaml)
    query_url = read_system_config.read_yaml_configuration("twn.query_url", config_yaml)
    query_filter = read_system_config.read_yaml_configuration(
        "twn.query_filter", config_yaml
    )
    skip_properties = read_system_config.read_yaml_configuration(
        "twn.skip_properties", config_yaml
    )
    page_size = read_system_config.read_yaml_configuration("twn.page_size", config_yaml)

    if test_clause:
        query_filter = query_filter + ';name:eq:"Abietinaria"'

    print("\nTWN download")

    ddecoapi = ddecoapi_data_parser.dataparser(
        aquadesk_url=aquadesk_url,
        api_key=api_key,
        query_url=query_url,
        query_filter=query_filter,
        skip_properties=skip_properties,
        page_size=page_size,
    )
    twn = ddecoapi.parse_data_dump()
    twn = twn.rename(
        columns={
            "name": "Name",
            "taxongroup": "Taxongroup_code",
            "taxontype": "Taxontype",
            "taxonrank": "Taxonrank",
            "parentname": "Parentname",
            "statuscode": "Statuscode",
            "synonymname": "Synonymname",
        }
    )
    print(f"Download {len(twn)} records: gereed")
    filename = read_system_config.read_yaml_configuration(
        "twn_download", "global_variables.yaml"
    )
    try:
        twn.to_csv(filename, index=False, sep=";")
    except Exception as e:
        logger.error(f"Vermoedelijk staat {filename} nog open.")
        logger.debug(f"{e} with %s", "arguments", exc_info=True)
        utility.stop_script()

    return twn


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def correct_twn(twn: pd.DataFrame) -> pd.DataFrame:
    """Corrects the TWN

    Args:
        twn (pd.DataFrame): the dataframe with TWN data to correct.

    Returns:
        pd.DataFrame: a Pandas DataFrame with the new twn.
    """
    # twn = read_system_config.read_csv_file(twn_filepath)
    # twn = twn[twn["taxontype"].isin(["MACEV", "NEMTD"])]

    # add the number of duplicated rows to the records_removed dictionary
    correct_twn.records_removed["duplicates"] = twn.duplicated(
        subset=["Name"], keep="first"
    ).sum()
    # delete duplicate taxa
    twn = twn.drop_duplicates(subset=["Name"])

    # set parentnames
    parent_dict = read_system_config.read_yaml_configuration(
        "set_parentnames", "twn_corrections.yaml"
    )
    twn = utility.replace_values(twn, parent_dict, "Name", "Parentname", "TWN")

    # make sure Animalia has no parent
    twn.loc[twn["Name"] == "Animalia", "Parentname"] = np.nan

    # set taxongroups
    overige_taxa = ["NEMTD"]
    twn.loc[twn["Taxontype"].isin(overige_taxa), "Taxongroup_code"] = "REMAIN"

    parent_dict = read_system_config.read_yaml_configuration(
        "set_taxongroup_codes", "twn_corrections.yaml"
    )
    twn = utility.replace_values(twn, parent_dict, "Name", "Taxongroup_code", "TWN")

    # set taxonranks
    parent_dict = read_system_config.read_yaml_configuration(
        "set_taxonranks", "twn_corrections.yaml"
    )
    twn = utility.replace_values(twn, parent_dict, "Name", "Taxonrank", "TWN")

    # set refernames
    parent_dict = read_system_config.read_yaml_configuration(
        "set_refernames", "twn_corrections.yaml"
    )

    twn = utility.replace_values(twn, parent_dict, "Name", "Synonymname", "TWN")

    filenamepath = read_system_config.read_yaml_configuration(
        "twn_corrected", "global_variables.yaml"
    )

    utility.export_df(twn, filenamepath)
    return twn


@log_decorator.log_factory(__name__)
def check_twn(twn: pd.DataFrame) -> typing.Union[None, bool]:
    """Performs checking if the twn is complete.

    Args:
        twn (pd.DataFrame): a Pandas DataFrame with the twn.

    Returns:
        bool: False if the checks are not met.
    """

    valid_twn = True

    # everywhere a parentname for valid taxa
    missing_parentnames = twn[
        (twn["Statuscode"].isin([10, 80]))
        & (twn["Parentname"].isna())
        & (~twn["Name"].isin(["Animalia"]))
    ]
    if len(missing_parentnames) > 0:
        logger.error(
            f'De volgende twn-taxa hebben geen parentname:\n {", ".join(missing_parentnames["Name"].tolist())}'
        )
        valid_twn = False

    # everywhere a taxongroup_code
    missing_taxongroups = twn[twn["Taxongroup_code"].isna()]
    if len(missing_taxongroups) > 0:
        logger.error(
            f'De volgende twn-taxa hebben geen taxongroup_code:\n {", ".join(missing_taxongroups["Name"].tolist())}'
        )
        valid_twn = False

    # everywhere a taxonrank
    missing_taxonranks = twn[twn["Taxonrank"].isna()]
    if len(missing_taxonranks) > 0:
        logger.error(
            f'De volgende twn-taxa hebben geen taxonrank:\n {", ".join(missing_taxonranks["Name"].tolist())}'
        )
        valid_twn = False

    # all invalid (statuscodes) have a refername
    # twn-error (statuscode 9x) optionaly have a synonymname, and so can't be checked
    missing_refernames = twn[
        (twn["Statuscode"].isin([20, 30])) & (twn["Synonymname"].isna())
    ]
    if len(missing_refernames) > 0:
        logger.error(
            f'De volgende twn-synoniemen hebben geen refername:\n {", ".join(missing_refernames["Name"].tolist())}'
        )
        valid_twn = False

    if not valid_twn:
        utility.stop_script()
    return valid_twn


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def filter_valid_twn(twn: pd.DataFrame) -> pd.DataFrame:
    """Filters the valid twn taxa: statuscodes 10 and 80.

    Args:
        twn (pd.DataFrame): a Pandas DataFrame with the twn data

    Returns:
        pd.DataFrame: a Pandas DataFrame with the valid taxa.
    """

    # add the number of excluded rows to the records_removed dictionary
    filter_valid_twn.records_removed["invalid_statuscode"] = twn[
        ~twn["Statuscode"].isin([10, 80])
    ].shape[0]

    return twn[(twn["Statuscode"].isin([10, 80]))]


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def filter_usefull_twn(twn: pd.DataFrame) -> pd.DataFrame:
    """Filters the valid twn taxa: statuscodes 10 and 80 or invalid taxa with a synonym

    Args:
        twn (pd.DataFrame): a Pandas DataFrame with the twn data

    Returns:
        pd.DataFrame: a Pandas DataFrame with the valid taxa.
    """

    # add the number of excluded rows to the records_removed dictionary
    filter_usefull_twn.records_removed["invalid_statuscode"] = twn[
        (~twn["Statuscode"].isin([10, 80])) & (twn["Synonymname"].isna())
    ].shape[0]

    return twn[(twn["Statuscode"].isin([10, 80])) | (~twn["Synonymname"].isna())]


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def select_twn_mapping_columns(twn: pd.DataFrame) -> pd.DataFrame:
    """Selects the minimal requested columns for the taxa mapping.

    Args:
        twn (pd.DataFrame): a Pandas DataFrame with the twn data

    Returns:
        pd.DataFrame: the minimal requested columns
    """

    twn = twn[["Name", "Parentname", "Statuscode"]]
    return twn


@log_decorator.log_factory(__name__)
def has_synonym(twn: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    """Checks whether there are synonymnnames.

    Args:
        df (pd.DataFrame): dataframe with the twn data.

    Returns:
        pd.DataFrame: dataframe with the taxa that have a synonymnname.
    """
    twn = twn["Name"]

    twn_df_merged = df.merge(
        twn, left_on="Analyse_taxonnaam", right_on="Name", how="left"
    )
    have_synonym = twn_df_merged[twn_df_merged["Name"].notna()][
        "Analyse_taxonnaam"
    ].unique()

    return have_synonym


@log_decorator.log_factory(__name__)
def get_twn_validity(twn: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    """Checks whether there are synonymnames or invalid names.
    Taxa can have the following statusses:
    - they are unknown in the twn or
    - they are invalid without an synonym or
    - they are invalid with a synonym
    - they are valid

    Args:
        twn (pd.DataFrame): DataFrame with the twn corrected data.
        df (pd.DataFrame): DataFrame with taxanames to check for.

    Returns:
        pd.DataFrame: A DataFrame with indication: synonym, invalid or unknown.
    """

    twn = twn.copy()
    twn = twn[["Name", "Statuscode", "Synonymname"]]

    df_twn_merged = df.merge(
        twn, left_on="Analyse_taxonnaam", right_on="Name", how="left"
    )

    # mark unknown twn taxa
    df_twn_merged.loc[df_twn_merged["Name"].isna(), "Status"] = "unknown"

    # mark invalid twn taxa
    df_twn_merged.loc[
        (~df_twn_merged["Name"].isna())
        & (~df_twn_merged["Statuscode"].isin([10, 80]))
        & (df_twn_merged["Synonymname"].isna()),
        "Status",
    ] = "invalid"

    # mark synonym twn taxa
    df_twn_merged.loc[
        (~df_twn_merged["Statuscode"].isin([10, 80]))
        & (~df_twn_merged["Synonymname"].isna()),
        "Status",
    ] = "synonym"

    # mark valid twn taxa
    df_twn_merged.loc[df_twn_merged["Statuscode"].isin([10, 80]), "Status"] = "valid"

    # remove columns
    df_twn_merged = df_twn_merged[["Analyse_taxonnaam", "Status", "Synonymname"]]

    return df_twn_merged


def main_twn() -> pd.DataFrame:
    """Downloads, corrects and checks the TWN.

    Returns:
        pd.DataFrame: the corrected TWN.
    """
    twn = download_twn()
    twn_corrected = correct_twn(twn)
    check_twn(twn_corrected)
    return twn_corrected
