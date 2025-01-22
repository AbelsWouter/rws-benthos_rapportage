"""Script to perform different checks on benthos data."""

"""
# File: checks_data.py
# Author(s): M. Japink (m.japink@waardenburg.eco) & J. Haringa (j.haringa@waardenburg.eco)
# Creation date: 21-01-2023
# Last modification: 20-02-2024
# Python v3.12.1
"""


import logging
import logging.config
import os

import pandas as pd


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))

from preparation import check_decorator
from preparation import log_decorator
from preparation import read_system_config
from preparation import utility


logger = logging.getLogger(__name__)


def check_number_of_excelsheets(file_path: str) -> pd.DataFrame:
    """checks if the number of sheets in an excel file is one.
       Prints an error message and stops the script if the file contains multiple sheets.

    Args:
        file_path (str): the path to the file.

    Returns:
        bool: True if the file contains one sheet,
    """
    try:
        xl = pd.ExcelFile(file_path, engine="openpyxl")
        sheet_names = xl.sheet_names
        if len(sheet_names) > 1:
            logger.error("De aangeboden excel bevat meerdere werkbladen.")
            utility.stop_script()
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")
    return True


@log_decorator.log_factory(__name__)
def check_rows_have_data(df: pd.DataFrame) -> bool:
    """Check if the dataframe contains rows of data.

    Args:
        df (pd.DataFrame): dataframe to be checked.

    Returns:
        bool: True if the df contains more than 1 row of data and False if not.
    """
    if len(df) > 0:
        logger.debug("The dataframe contains data rows")
        return True
    logger.error(f"Het dataframe {df} bevat geen rijen data.")
    utility.stop_script()
    return False


@log_decorator.log_factory(__name__)
def check_waterbodies_present(df: pd.DataFrame, waterbodies: list[str]) -> None:
    """Checks whether the waterbodies selected by the user are present in the data.

    Args:
        df (pd.DataFrame): dataframe with the data.
        waterbodies (list[str]): the selected waterbodies by the user.
    """
    for waterbody in waterbodies:
        if len(df) == 0:
            logger.error(
                f"De geselecteerde waterlichamen ({waterbodies}) zijn niet aangetroffen in de data.\n"
                "Selecteer een ander waterlichaam of gebruik andere input data."
            )
            utility.stop_script()
        if len(df[df["Waterlichaam"].isin([waterbody])]) == 0:
            logger.warning(
                f"Een van de geselecteerde waterlichamen ({waterbody}) is niet aangetroffen in de data."
            )


@log_decorator.log_factory(__name__)
def check_projects_present(df: pd.DataFrame, projects: list[str]) -> None:
    """Checks whether the projects selected by the user are present in the data.

    Args:
        df (pd.DataFrame): dataframe with the data.
        projects (list[str]): the selected projects by the user.
    """
    for project in projects:
        if len(df) == 0:
            logger.error(
                f"De geselecteerde projecten ({projects}) zijn niet aangetroffen in de data.\n"
                "Selecteer een ander project of gebruik andere input data."
            )
            utility.stop_script()
        if len(df[df["Project_Code"].isin([project])]) == 0:
            logger.warning(
                f"Een van de geselecteerde projecten ({project}) is niet aangetroffen in de data."
            )


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def check_has_taxa(df: pd.DataFrame) -> pd.DataFrame:
    """Check if the dataframe contains counted taxa.

    Args:
        df (pd.DataFrame): dataframe to be checked.

    Returns:
        bool: True if the df contains more than 1 row of data and False if not.
    """

    check = df[
        [
            "Collectie_Referentie",
            "Meetpakket_Code",
        ]
    ].copy()

    # set Meetpakketcode ME.AB to 1, the others to 0
    check.loc[check["Meetpakket_Code"] == "ME.AB", "has_taxa"] = 1
    check.loc[check["Meetpakket_Code"] != "ME.AB", "has_taxa"] = 0

    # Group by 'Collectie_Referentie' and calculate the sum of 'has_taxa'
    check = check.groupby("Collectie_Referentie")["has_taxa"].agg("sum").reset_index()

    check = check[check["has_taxa"] == 0]
    empty_samples = check["Collectie_Referentie"].unique().tolist()

    if len(empty_samples) == 0:
        logger.debug("Alle monsters hebben in ieder geval één geteld taxon.")
        return df

    logger.warning(
        f"In {len(empty_samples)} monsters zijn geen taxa geteld, "
        f"deze monsters zijn geheel verwijderd: {empty_samples}"
    )
    # add the number of removed records to the records_removed dictionary
    check_has_taxa.records_removed["without_taxa"] = df[
        df["Collectie_Referentie"].isin(empty_samples)
    ].shape[0]
    # Drop empty samples
    df = df[~df["Collectie_Referentie"].isin(empty_samples)]
    return df


@log_decorator.log_factory(__name__)
def check_missing_values(
    df: pd.DataFrame,
    check_columns: list[str],
    source_name: str,
) -> bool:
    """Checks if any of the given columns has missing values.

    Args:
        df (pd.DataFrame): The DataFrame to be checked.
        check_columns (list): the columns that should not hold NA's.
        source_name (str): the name of the source for the log message.

    Returns:
        bool: True if none of the columns holds NA's, False if any does.
    """
    nan_values = df.isna().any()
    nan_columns = df[df.columns[nan_values]]
    logger.debug(f"The columns with NA are {nan_columns.columns}")

    has_NA = False
    columns_mising_values = []

    for col in check_columns:
        if col in nan_columns:
            has_NA = True
            columns_mising_values.append(col)

    if has_NA:
        logger.error(
            f"De kolommen {columns_mising_values} in de {source_name}"
            " data mogen geen missende waarden hebben. Vul de lege cellen."
        )
        utility.stop_script()

    return has_NA


@log_decorator.log_factory(__name__)
def check_data_type_column(df: pd.DataFrame) -> pd.DataFrame:
    """Check the data type of each column.

    Args:
        df (pd.DataFrame): The DataFrame to be checked.

    Returns:
        pd.Series: a Pandas Series with the datatypes for each column.
    """
    datatypes = df.dtypes.astype(str)
    logger.debug(f"the actual_data_types are {datatypes}")

    if df["Aantal"].dtype != "float64" and df["Aantal"].dtype != "int64":
        logger.error("Datatype voor aantal moet nummeriek zijn")
        utility.stop_script()
    return datatypes


@log_decorator.log_factory(__name__)
def check_required_col(df: pd.DataFrame, expected_req_col: pd.Series) -> bool:
    """Check if the required columns are there.

    Args:
        df (pd.DataFrame): the DataFrame to be checked.
        expected_req_col (pd.Series): the list of expected required column names from the function.
    """

    actual_col_names = list(df.columns)
    expected_req_col = expected_req_col.tolist()

    check = list(set(expected_req_col) - set(actual_col_names))
    if len(check) > 0:
        logger.error(
            f"De volgende kolommen zijn niet aangetroffen in de data: \n {check}"
        )
        utility.stop_script()

    return True


@log_decorator.log_factory(__name__)
def check_uniqueness(
    df: pd.DataFrame, unique_columns: list[str], source_name: str
) -> bool:
    """Checks uniqueness over one or multiple columns.

    Args:
        df (pd.DataFrame): dataframe to be checked.
        unique_columns (list[str]): the columns which should be aggregated.
        source_name (str): the name of the source for the log message.
    """

    duplicates = df[df.duplicated(subset=unique_columns, keep=False)]

    is_unique = len(duplicates) == 0
    if not is_unique:
        logger.error(
            f"De combinatie van kolommen {unique_columns} in de {source_name} data is "
            f"{len(duplicates)}x niet uniek voor:\n {duplicates[unique_columns].drop_duplicates()}"
        )
        utility.stop_script()
    return is_unique


@log_decorator.log_factory(__name__)
def check_unique_distinct(
    df: pd.DataFrame,
    distinct_columns: list[str],
    unique_column: str,
    source_name: str,
) -> bool:
    """Check whether there are only unique records.

    Args:
        df (pd.DataFrame): dataframe to be checked.
        distinct_columns (list[str]): the columns which should be distinct.
        unique_column (str): the column to return for unique taxa.
        source_name (str, optional): the name of the source to show in log-message. Defaults to None.
    """

    df = df.copy()
    df_grouped = df.drop_duplicates(subset=distinct_columns)
    df_unique = df_grouped.groupby(unique_column).size().reset_index(name="Count")

    # check_uniqueness
    check = df_unique[df_unique["Count"] > 1]
    if len(check) > 0:
        logger.error(
            f"De combinatie van kolommen {distinct_columns} in de {source_name} data is "
            f"{len(check)}x niet uniek:\n {check[unique_column].unique()}"
        )
        utility.stop_script()

    return True


@log_decorator.log_factory(__name__)
def round_numeric_columns(df: pd.DataFrame, decimals: int = 9) -> pd.DataFrame:
    """Round the numbers in the dataframe to the required number of decimals.

    Args:
        df (pd.DataFrame): dataframe to be rounded.

    Returns:
        pd.DataFrame: the rounded dataframe.
    """

    diversity_levels = read_system_config.read_yaml_configuration(
        "diversity_levels", "global_variables.yaml"
    )
    configured_columns = list(diversity_levels.keys())
    configured_nm2_columns = ["nm2_Soort_" + item for item in configured_columns]
    configured_n_columns = ["n_Soort_" + item for item in configured_columns]

    hard_coded_columns = [
        "Aantal",
        "Massa",
        "Bedekking",
        "Dichtheid_Aantal",
        "Dichtheid_Massa",
    ]

    for column in hard_coded_columns + configured_nm2_columns + configured_n_columns:
        if column in df.columns:
            df[column] = df[column].astype(float).round(decimals)

    return df


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def remove_negative_measurements(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Check and remove negative taxa measurements.

    Args:
        df (pd.DataFrame): dataframe

    Returns:
        pd
    """

    df_negative = df[df[column] < 0.0]
    if len(df_negative) > 0:
        logger.warning(
            f"{column} mag niet negatief zijn, {len(df_negative)} regels zijn verwijderd. \n"
            f"Dit zijn: {df[df[column] < 0.0]}"
        )
        # add the number of removed records to the records_removed dictionary
        remove_negative_measurements.records_removed[column] = df[
            df[column] < 0.0
        ].shape[0]
        df_new = df[df[column] >= 0.0]
    else:
        logger.debug(f"Correct: No values of {column} of 0 or less")
        df_new = df.copy()

    return df_new


def main_check_data(
    data: pd.DataFrame, exp_col: list, col_names_not_be_NA: list
) -> pd.DataFrame:
    """Performs various checks on the data.

    Args:
        data (pd.DataFrame): dataframe with the data.
        exp_col (list): the expected columns in the data.
        col_names_not_be_NA (list): the columns that should not be NA.

    Returns:
        pd.DataFrame: the input data without negative values.
    """
    check_required_col(data, exp_col)
    check_rows_have_data(data)
    check_missing_values(data, col_names_not_be_NA, "Aquadesk")
    check_data_type_column(data)
    data = round_numeric_columns(data)

    hard_coded_columns = [
        "Aantal",
        "Massa",
        "Bedekking",
        "Dichtheid_Aantal",
        "Dichtheid_Massa",
    ]
    for column in hard_coded_columns:
        if column in data.columns:
            data = remove_negative_measurements(data, column)

    check_uniqueness(
        data, ["Collectie_Referentie", "Analyse_taxonnaam"], "Analyse_taxonnaam"
    )
    distinct_col = read_system_config.read_sample_properties("analysis_name")
    check_unique_distinct(data, distinct_col, "Collectie_Referentie", "analysis")
    return data
