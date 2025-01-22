"""Script to import and check benthos data."""

"""
# File: benthos_data.py
# Author(s): M. Japink (m.japink@waardenburg.eco) & J. Haringa (j.haringa@waardenburg.eco)
# Creation date: 21-01-2023
# Last modification: 20-02-2024
# Python v3.12.1
"""

import logging
import os
from typing import List

import numpy as np
import pandas as pd


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))

from checks import check_config
from checks import check_data
from preparation import add_mapping
from preparation import aquadesk
from preparation import benthos_data_helpers
from preparation import check_decorator
from preparation import diversity
from preparation import log_decorator
from preparation import process_twn
from preparation import protocol_mapping
from preparation import read_system_config
from preparation import read_user_config
from preparation import taxa_mapping
from preparation import utility


# Initializing logger object to write custom logs
logger = logging.getLogger(__name__)


@log_decorator.log_factory(__name__)
def read_benthos_data(file_path: str) -> pd.DataFrame:
    """Make a pandas DataFrame from the Excel data.

    Args:
        file_path (str): the location of the Excel input data

    Returns:
        pd.DataFrame: returns a Pandas DataFrame of Excel specified in the file_path
    """

    filename = utility.get_file_name(file_path)
    root_ext = os.path.splitext(filename)
    file_type = root_ext[1]
    if file_type == ".csv":
        df = read_system_config.read_csv_file(file_path + "/" + filename)
    if file_type == ".xlsx":
        check_data.check_number_of_excelsheets(file_path + "/" + filename)
        df = pd.read_excel(file_path + "/" + filename, engine="openpyxl")
    req_columns = read_system_config.read_column_mapping()
    req_columns_not_null = req_columns.loc[req_columns["not_null"]]["script_name"]
    check_data.check_missing_values(df, req_columns_not_null, "Aquadesk")
    return df


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def get_required_columns(df: pd.DataFrame, required_columns: List) -> pd.DataFrame:
    """Make a DataFrame with only the required columns.

    Args:
        file_path (str): the location of the Excel data for which to make a DataFrame.
        required_columns (List): the list of required column names

    Returns:
        pd.DataFrame: a Pandas DataFrame with only the required columns for later functionality.
    """
    df = df[required_columns]
    logger.debug(
        f"Alleen de benodigde kolommen zijn geselecteerd: \n {required_columns} \n"
    )
    return df


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def correct_aquadesk_taxa(df: pd.DataFrame) -> pd.DataFrame:
    """Corrects the Aquadesk data

    Args:
        df(pd.DataFrame): a pandas dataframe with the aquadesk data

    Returns:
        pd.DataFrame: a Pandas DataFrame with corrected aquadesk data.
    """

    # set parentnames
    replace_dict = read_system_config.read_yaml_configuration(
        "parameter_specificatie", "aquadesk_corrections.yaml"
    )
    df = utility.replace_values(
        df, replace_dict, "Parameter_Specificatie", "Parameter_Specificatie", "Aquadesk"
    )
    return df


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def add_location_data(df: pd.DataFrame, df_location_data: pd.DataFrame) -> pd.DataFrame:
    """Add location data from the configuration file.

    Args:
        df (pd.DataFrame): the DataFrame with the input data.
        df_location_data (pd.DataFrame): the DataFrame with the location data.

    Returns:
        pd.DataFrame: dataframe with the location info added.
    """

    df_location_data = df_location_data.rename(columns={"Methode": "Bemonsteringsapp"})

    df.loc[:, "Meetobject_Code"].str.strip()
    df_new = df.merge(
        df_location_data[
            [
                "Waterlichaam",
                "Meetobject_Code",
                "Project_Code",
                "Strata",
                "Gebied",
                "BISI_gebied",
                "BISI_deelgebied",
                "BISI_Eunis",
                "BISI_Eunis_asev",
                "BISI_Habitat",
                "Margalef",
                "Gebruik",
                "Bemonsteringsapp",
            ]
        ],
        on=["Meetobject_Code", "Bemonsteringsapp", "Project_Code"],
        how="left",
    )
    waterbodies = df_new["Waterlichaam"].unique()
    logger.info(
        f"De data met de waterlichamen uit de configuratie zijn geselecteerd: {waterbodies}."
    )
    return df_new


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def add_waterbody_data(
    df: pd.DataFrame, df_waterbody_data: pd.DataFrame
) -> pd.DataFrame:
    """Add the waterbody information from the configuration file.

    Args:
        df (pd.DataFrame): the DataFrame with the input data.
        df_waterbody_data (pd.DataFrame): the DataFrame with the waterbody data.

    Returns:
        pd.DataFrame: dataframe with the waterbody info added.
    """

    df_new = df.merge(
        df_waterbody_data[
            [
                "Waterlichaam",
                "Heeft_Seizoen",
                "Trendgroep",
                "Determinatie_protocol",
                "Biomassa_protocol",
                "Startjaar",
                "Min_trend_monsters",
            ]
        ],
        on=["Waterlichaam"],
        how="left",
    )
    return df_new


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def filter_waterbodies(df: pd.DataFrame, waterbodies: list[str]) -> pd.DataFrame:  # type: ignore
    """Filter the waterbody as configured by the user in the configuration file.

    Args:
        df (pd.DataFrame): dataframe with the input data.
        waterbodies: the waterbodies from the config file.

    Returns:
        pd.DataFrame: dataframe with the selected waterbody/waterbodies.
    """

    # add the not selected records to the records_removed dictionary
    filter_waterbodies.records_removed["removed samples mulitple device"] = df[
        ~df["Waterlichaam"].isin(waterbodies)
    ].shape[0]
    df_select_water = df[df["Waterlichaam"].isin(waterbodies)]
    check_data.check_waterbodies_present(df_select_water, waterbodies)
    return df_select_water


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def filter_required_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Filters only the rows that are required for the analysis.
    When the data is downloaded from Aquadesk then this is a double check.

    Args:
        df (pd.DataFrame): dataframe.

    Returns:
        pd.DataFrame: the DataFrame with only the selected rows.
    """

    # read measuremenst.query_filter from aquadesk.yaml to dictionary
    dict_query_filter = benthos_data_helpers.split_query_filter_to_dictionary()

    dict_query_filter_renamed = benthos_data_helpers.rename_query_filter_columns(
        dict_query_filter
    )

    # loop over dict_query_filter_renamed and
    # if column exists then filter data by value of dict_query_filter_renamed
    for key, value in dict_query_filter_renamed.items():
        if key == "Collectie_DatumTijd":
            continue
        if key in df:
            check = df[~df[key].isin(value)]
            unwanted_values = check[key].unique().tolist()
            if len(check) > 0:
                logger.warning(
                    f"In kolom {key} zijn andere waarden dan {value} gevonden: {unwanted_values}). "
                    f"Voor {len(check['Collectie_Referentie'].unique())} "
                    "monsters zijn de regels met deze waarden verwijderd."
                )
                # add the number of removed sample records to the records_removed dictionary
                filter_required_rows.records_removed[key] = df[
                    df[key].isin(unwanted_values)
                ].shape[0]
                # remove records
                df = df[~df[key].isin(unwanted_values)]

    return df


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def sample_device_to_column(df: pd.DataFrame) -> pd.DataFrame:
    """Sets sample devices/substrates for BEMSRAPRT and SUBSMTRAL from row to column. Value must be unique for sample.

    Args:
        df (pd.DataFrame): the DataFrame for which the sample devices/substrate should be transformed to a column.

    Returns:
        pd.DataFrame: the updated DataFrame.
    """

    # filter the columns "Collectie_Referentie", "Classificatie_Code", "Grootheid_Code"
    df_sample_device = df[
        ["Collectie_Referentie", "Classificatie_Code", "Grootheid_Code"]
    ]

    # filter the rows with Grootheid_Code "BEMSRAPRT", "SUBSMTRAL"
    df_sample_device = df_sample_device[
        df_sample_device["Grootheid_Code"].isin(["BEMSRAPRT", "SUBSMTRAL"])
    ]

    # remove duplicate rows
    df_sample_device = df_sample_device.drop_duplicates()

    # select the rows where the Collectie_Referentie and Grootheid_Code are equal but the Classificatie_Code is not and
    # remove complete samples from df and df_sample_device
    check = df_sample_device[
        df_sample_device.duplicated(subset=["Collectie_Referentie", "Grootheid_Code"])
    ]
    if len(check) > 0:
        logger.error(
            "De volgende monsters hebben meerdere bemonsteringsapparaten en zijn volledig verwijderd:\n"
            f'{check["Collectie_Referentie"].unique().tolist()}'
        )
    # add the number of removed samples to the records_removed dictionary
    sample_device_to_column.records_removed["removed samples mulitple device"] = df[
        df["Collectie_Referentie"].isin(check["Collectie_Referentie"])
    ].shape[0]
    # remove records
    df = df[~df["Collectie_Referentie"].isin(check["Collectie_Referentie"])]
    df_sample_device = df_sample_device[
        ~df_sample_device["Collectie_Referentie"].isin(check["Collectie_Referentie"])
    ]

    # select the rows where the Collectie_Referentie is equal but where the Grootheid_Code is not and
    # remove the duplicate rows from df_sample_device where the Grootheid_Code is SUBSMTRAL
    check = df_sample_device[
        df_sample_device.duplicated(subset=["Collectie_Referentie"])
    ]
    if len(check) > 0:
        logger.warning(
            "De volgende monsters hebben zowel een bemonsteringsapparaat als een substraatmateriaal,\n"
            f'het bemonsteringsapparaat is overgenomen:\n {check["Collectie_Referentie"].unique().tolist()}'
        )
    df_sample_device = df_sample_device[
        ~(
            (
                df_sample_device["Collectie_Referentie"].isin(
                    check["Collectie_Referentie"]
                )
            )
            & (df_sample_device["Grootheid_Code"] == "SUBSMTRAL")
        )
    ]

    # rename classificatie_code to Bemonsteringsapp
    df_sample_device = df_sample_device.rename(
        columns={"Classificatie_Code": "Bemonsteringsapp"}
    )

    # add Bemonsteringsapp to df
    df_new = df.merge(
        df_sample_device[["Collectie_Referentie", "Bemonsteringsapp"]],
        on=["Collectie_Referentie"],
        how="left",
    )

    # check if there are any samples without an bemonsteringsapp
    check = df_new[df_new["Bemonsteringsapp"].isna()]

    if len(check) > 0:
        logger.warning(
            f'Er zijn {check["Collectie_Referentie"].nunique()} monsters '
            f"zonder bemonsteringsapparaat en/of substraatmateriaal, deze zijn verwijderd:\n"
            f'{check["Collectie_Referentie"].unique().tolist()}'
        )

        # add the number of removed samples records to the records_removed dictionary
        sample_device_to_column.records_removed["removed samples no device"] = df_new[
            df_new["Bemonsteringsapp"].isna()
        ].shape[0]
        # remove records
        df_new = df_new[~df_new["Bemonsteringsapp"].isna()]

    # clean
    # add the number of removed sample devices to the records_removed dictionary
    sample_device_to_column.records_removed["removed samples_devices"] = df_new[
        df_new["Grootheid_Code"].isin(["BEMSRAPRT", "SUBSMTRAL"])
    ].shape[0]
    # remove sample device records
    df_new = df_new[~df_new["Grootheid_Code"].isin(["BEMSRAPRT", "SUBSMTRAL"])]

    return df_new


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def support_to_column(df: pd.DataFrame) -> pd.DataFrame:
    """Set sample size OPPVT or VOLME and unit to support columns.
    Support (size) and support unit must be unique for sample.

    Args:
        df (pd.DataFrame): the DataFrame for which the support should be transformed to a column.

    Returns:
        pd.DataFrame: the updated DataFrame.
    """

    # check field type
    if df["Waarde_Berekend"].dtypes != "float64":
        df["Waarde_Berekend"] = df["Waarde_Berekend"].astype(float)

    # filter the columns "Collectie_Referentie", "Grootheid_Code", "Waarde_Berekend", "Eenheid_Berekend"
    # select the rows where the Grootheid_Code is OPPVT or VOLME
    df_support = df[
        [
            "Collectie_Referentie",
            "Grootheid_Code",
            "Waarde_Berekend",
            "Eenheid_Berekend",
        ]
    ]
    df_support = df_support[df_support["Grootheid_Code"].isin(["OPPVTE", "VOLME"])]

    # remove duplicate rows
    df_support = df_support.drop_duplicates()

    # check if there are samples with multiple support values, remove complete samples from df and df_support
    check = df_support[df_support.duplicated(subset=["Collectie_Referentie"])]
    if len(check) > 0:
        logger.warning(
            f"De volgende monsters hebben meerdere supportwaarden en zijn volledig verwijderd: \
                {check['Collectie_Referentie'].unique().tolist()}"
        )
    # add the number of removed sample records to the records_removed dictionary
    support_to_column.records_removed["removed samples multiple supports"] = df[
        df["Collectie_Referentie"].isin(check["Collectie_Referentie"])
    ].shape[0]
    # remove records
    df = df[~df["Collectie_Referentie"].isin(check["Collectie_Referentie"])]
    df_support = df_support[
        ~df_support["Collectie_Referentie"].isin(check["Collectie_Referentie"])
    ]

    # rename Waarde_Berekend to Support and Eenheid_Berekend to Support_Eenheid
    df_support = df_support.rename(
        columns={"Waarde_Berekend": "Support", "Eenheid_Berekend": "Support_Eenheid"}
    )

    # add support to df
    df_new = df.merge(
        df_support[["Collectie_Referentie", "Support", "Support_Eenheid"]],
        on=["Collectie_Referentie"],
        how="left",
    )

    # clean
    # add the number of removed support records to the records_removed dictionary
    support_to_column.records_removed["removed support records"] = df_new[
        df_new["Grootheid_Code"].isin(["OPPVTE", "VOLME"])
    ].shape[0]
    df_new = df_new[~df_new["Grootheid_Code"].isin(["OPPVTE", "VOLME"])]

    # check if there are any samples without an support
    check = df_new[(df_new["Support"].isna()) | (df_new["Support_Eenheid"].isna())]
    if len(check) > 0:
        logger.warning(
            f'Er zijn {check["Collectie_Referentie"].nunique()} monsters zonder support, deze zijn verwijderd: \
                {check["Collectie_Referentie"].unique().tolist()}'
        )
    # add the number of removed sample records to the records_removed dictionary
    support_to_column.records_removed["removed samples no supports"] = df_new[
        (df_new["Support"].isna()) | (df_new["Support_Eenheid"].isna())
    ].shape[0]
    # remove records
    df_new = df_new[~df_new["Support"].isna()]
    df_new = df_new[~df_new["Support_Eenheid"].isna()]

    # check if there are any samples with support = 0
    check = df_new[df_new["Support"] == 0]
    if len(check) > 0:
        logger.warning(
            f'Er zijn {check["Collectie_Referentie"].nunique()} monsters met een bemonsterde oppervlakte/volume = 0, \
                deze zijn verwijderd: \
                {check["Collectie_Referentie"].unique().tolist()}'
        )
    # add the number of removed sample records to the records_removed dictionary
    support_to_column.records_removed["removed samples support = 0"] = df_new[
        df_new["Support"] == 0
    ].shape[0]
    # remove records
    df_new = df_new[df_new["Support"] != 0]

    return df_new


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def add_sample_year(df: pd.DataFrame) -> pd.DataFrame:
    """Add a column with the sample year retrieved from the 'Collectie_DatumTijd' field

    Args:
        df (pd.DataFrame): aquadesk dataframe

    Returns:
        pd.DataFrame: the dataframe with the column Monsterjaar added.
    """
    df_new = df.copy()

    if df_new["Collectie_DatumTijd"].dtypes != "object":
        df_new["Collectie_DatumTijd"] = df_new["Collectie_DatumTijd"].astype(str)
        logger.debug(
            f"Collectie_DatumTijd omgezet naar {df_new['Collectie_DatumTijd'].dtypes}"
        )
    df_new["Monsterjaar"] = df_new["Collectie_DatumTijd"].str.extract("(\\d\\d\\d\\d)")
    df_new["Monsterjaar"] = df_new["Monsterjaar"].astype("int32")
    return df_new


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def add_season(df: pd.DataFrame) -> pd.DataFrame:
    """Adds spring or autumn based on the month.

    Args:
        df (pd.DataFrame): dataframe with the input data.

    Returns:
        pd.DataFrame: dataframe with the added season column.
    """
    df["Month"] = df["Collectie_DatumTijd"].str[5:7]
    df["Month"] = df["Month"].astype(int)
    df["Seizoen"] = np.where(df["Month"] < 7, "voorjaar", "najaar")
    df = df.drop(columns="Month")

    return df


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def check_season(df: pd.DataFrame) -> pd.DataFrame:
    """Check if multiple seasons are present and allowed.
    If multiple seasons are present but not allowed then the lesser are removed
    (number of samples per waterbody per year).

    Args:
        df (pd.DataFrame): dataframe with the input data.

    Returns:
        pd.DataFrame: A Pandas DataFrame with valid seasons.
    """

    # get distinct_samples
    sample_df = df[
        [
            "Waterlichaam",
            "Collectie_Referentie",
            "Monsterjaar",
            "Heeft_Seizoen",
            "Seizoen",
        ]
    ].drop_duplicates()

    # calculate the number of season occasions per waterbody per year
    result_df = (
        sample_df.groupby(["Waterlichaam", "Monsterjaar", "Seizoen", "Heeft_Seizoen"])
        .size()
        .reset_index(name="n")
        .pivot(
            index=["Waterlichaam", "Monsterjaar", "Heeft_Seizoen"],
            columns="Seizoen",
            values="n",
        )
        .reset_index()
    )
    result_df.columns.name = None

    # rename voorjaar and najaar columns to Voorjaar and Najaar
    rename_list = {"voorjaar": "Voorjaar", "najaar": "Najaar"}
    result_df.rename(
        columns={k: v for k, v in rename_list.items() if v not in result_df},
        inplace=True,
    )

    # check for and append missing season columns
    result_df = result_df.reindex(
        result_df.columns.union(["Voorjaar", "Najaar"], sort=False), axis=1
    )

    # mark for error if no seasons are allowed and spring as well as autumn are given
    result_df["Error"] = False
    result_df.loc[
        result_df[["Voorjaar", "Najaar"]].notnull().all(1)
        & ~result_df["Heeft_Seizoen"],
        "Error",
    ] = True

    # merge calculations with samples
    result_df = pd.merge(
        sample_df,
        result_df,
        on=["Waterlichaam", "Monsterjaar", "Heeft_Seizoen"],
        how="left",
    )

    # extract erroneous rows
    error_df = result_df[result_df["Error"]][
        [
            "Waterlichaam",
            "Collectie_Referentie",
            "Monsterjaar",
            "Heeft_Seizoen",
            "Seizoen",
            "Voorjaar",
            "Najaar",
        ]
    ]

    # warn user
    # three different errortypes:
    equal_error = error_df[error_df["Voorjaar"] == error_df["Najaar"]]
    spring_error = error_df[error_df["Voorjaar"] < error_df["Najaar"]]
    spring_error = spring_error[spring_error["Seizoen"] == "voorjaar"]
    autumn_error = error_df[error_df["Najaar"] < error_df["Voorjaar"]]
    autumn_error = autumn_error[autumn_error["Seizoen"] == "najaar"]

    clean_df = df
    keys = ["Waterlichaam", "Collectie_Referentie", "Monsterjaar"]

    if len(equal_error.index) > 0:
        # drop both spring and autumn samples
        log_message = (
            equal_error.groupby("Waterlichaam")["Collectie_Referentie"]
            .apply(list)
            .to_dict()
        )
        logger.warning(
            f"De volgende monsters zijn verwijderd vanwege een verkeerd seizoen: \n {log_message}"
        )
        i1 = clean_df.set_index(keys).index
        i2 = equal_error.set_index(keys).index
        # add removed samples to records_removed dictionary
        check_season.records_removed["removed samples equal seasons"] = clean_df[
            i1.isin(i2)
        ].shape[0]
        clean_df = clean_df[~i1.isin(i2)]

    if len(spring_error.index) > 0:
        # only drop the lesser = spring samples
        log_message = (
            spring_error.groupby("Waterlichaam")["Collectie_Referentie"]
            .apply(list)
            .to_dict()
        )
        logger.warning(
            f"De volgende voorjaarsmonsters zijn verwijderd vanwege een verkeerd seizoen: \n {log_message}"
        )
        i1 = clean_df.set_index(keys).index
        i2 = spring_error.set_index(keys).index

        # add removed samples to records_removed dictionary
        check_season.records_removed["removed samples spring seasons"] = clean_df[
            i1.isin(i2)
        ].shape[0]
        clean_df = clean_df[~i1.isin(i2)]

    if len(autumn_error.index) > 0:
        # only drop the lesser = autumn samples
        log_message = (
            autumn_error.groupby("Waterlichaam")["Collectie_Referentie"]
            .apply(list)
            .to_dict()
        )
        logger.warning(
            f"De volgende Najaarsmonsters zijn verwijderd vanwege een verkeerd seizoen: \n {log_message}"
        )
        i1 = clean_df.set_index(keys).index
        i2 = autumn_error.set_index(keys).index

        # add removed samples to records_removed dictionary
        check_season.records_removed["removed samples autumn seasons"] = clean_df[
            i1.isin(i2)
        ].shape[0]
        clean_df = clean_df[~i1.isin(i2)]

    return clean_df


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def mark_azoisch(df: pd.DataFrame) -> pd.DataFrame:
    """Replace Animalia for Azoisch for Parameter_Specificatie if
    the Limiet_Symbool is NaN en Waarde_Berekend is 0.

    Args:
        df (pd.DataFrame): a Pandas DataFrame with at least the columns: analyse_taxonnaam,
        Waarde_Berekend, Limiet_Symbool

    Returns:
        pd.DataFrame: The updated Pandas DataFrame
    """

    df_new = df.copy()
    df_new.loc[
        (
            (df_new["Analyse_taxonnaam"] == "Animalia")
            & (df_new["Waarde_Berekend"] == 0)
            & (df_new["Limiet_Symbool"].isna())
        ),
        "Analyse_taxonnaam",
    ] = "Azoisch"
    return df_new


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def usage_based_on_samples(df: pd.DataFrame) -> pd.DataFrame:
    """Checks the number of samples, if it is less than the minimum nr of samples
    to be used in trends, it becomes 'overig'.

    Args:
        df (pd.DataFrame): The DataFrame with the samples.

    Returns:
        pd.DataFrame: original dataframe incl. column "Gebruik" with possible adaptations.
    """

    df_new = df.copy()

    # filter the Gebruik = trend samples
    df_nr_of_samples = df_new[df_new["Gebruik"] == "trend"]

    df_nr_of_samples = df_nr_of_samples.groupby(
        [
            "Monsterjaar",
            "Waterlichaam",
        ],
        dropna=False,
        as_index=False,
    ).agg(Nmonsters=("Collectie_Referentie", "nunique"))
    df_merge_Nsamples = df_new.merge(
        df_nr_of_samples,
        how="left",
        on=[
            "Monsterjaar",
            "Waterlichaam",
        ],
    )

    condition = df_merge_Nsamples["Nmonsters"] < df_merge_Nsamples["Min_trend_monsters"]
    df_merge_Nsamples.loc[condition, "Gebruik"] = "overig"

    # clean
    df_clean = df_merge_Nsamples.drop(columns=["Nmonsters"])

    return df_clean


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def presence_to_abundance(df: pd.DataFrame) -> pd.DataFrame:
    """Assign 1 to Waarde_berekend if species was fount in screening

    Args:
        df (pd.DataFrame): a Pandas Dataframe with at least the columns: Limiet_symbool,
        Waarde_Berekend, Grootheid_Code, IsPresentie_Protocol

    Returns:
        pd.DataFrame: a Pandas DataFrame

    """
    df_new = df.copy()
    df_new.loc[
        (
            (df_new["Grootheid_Code"] == "AANTL")
            & (df_new["Limiet_Symbool"] == ">")
            & (df_new["Waarde_Berekend"] == 0)
            & (~df_new["IsPresentie_Protocol"])
        ),
        "Waarde_Berekend",
    ] = 1
    return df_new


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def abundance_to_presence(df: pd.DataFrame) -> pd.DataFrame:
    """Assign 0 to Waarde_berekend if protocol says presence

    Args:
        df (pd.DataFrame): a Pandas Dataframe with at least the columns: Waarde_Berekend,
        Grootheid_Code, protocol_presentie

    Returns:
        pd.DataFrame: a Pandas DataFrame

    """
    df_new = df.copy()

    if "Grootheid_Code" in df_new.columns:
        df_new.loc[
            ((df_new["Grootheid_Code"] == "AANTL") & (df_new["IsPresentie_Protocol"])),
            "Waarde_Berekend",
        ] = 0
    return df_new


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def biomass_to_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Sets the number to NA if there should not have been calculated biomass according to the protocol.

    Args:
        df (pd.DataFrame): The input Pnadas DataFrame.

    Returns:
        pd.DataFrame: DataFrame with biomass and a boolean columnm IsBiomassa_Protocol.
    """
    df_new = df.copy()
    if "Grootheid_Code" in df_new.columns:
        df_new.loc[
            ((df_new["Grootheid_Code"] == "MASSA") & (~df_new["IsBiomassa_Protocol"])),
            "Waarde_Berekend",
        ] = np.NaN

    return df_new


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def aggregate_taxa(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate taxa grouped by and sums the column Waarde_Berekend.

    Args:
        df (pd.DataFrame): dataframe

    Returns:
        pd.DataFrame: dataframe for which the taxa are aggregated.
    """
    aggregate_taxa.records_removed["removed"] = df[
        ~df["Grootheid_Code"].isin(["AANTL", "MASSA", "BEDKG"])
    ].shape[0]
    df_new = df[df["Grootheid_Code"].isin(["AANTL", "MASSA", "BEDKG"])]
    col_list = df_new.columns.difference(
        ["Limiet_Symbool", "Name_mapping_taxa", "Overrule_taxonname", "Waarde_Berekend"]
    ).values.tolist()
    df_grouped = df_new.groupby(by=col_list, dropna=False, as_index=False).aggregate(
        {
            "Waarde_Berekend": "sum",
        }
    )
    aggregate_taxa.records_removed["grouped_diff"] = (
        df_new.shape[0] - df_grouped.shape[0]
    )

    return df_grouped


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def taxa_quantities_to_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Set the measured values for taxa ("AANTL","MASSA"."BEDEKG") to their respective columns.

    Args:
        df (pd.DataFrame): the input Pandas DataFrame

    Returns:
        pd.DataFrame: the output DataFrame with extra column added.
    """

    df = df.copy()
    # add unwanted quantities to records_removed dictionary
    taxa_quantities_to_columns.records_removed["unwanted quantity rows"] = df[
        ~df["Grootheid_Code"].isin(["AANTL", "MASSA", "BEDKG"])
    ].shape[0]
    df = df[df["Grootheid_Code"].isin(["AANTL", "MASSA", "BEDKG"])]

    # check if there is gram in unit of mass, convert to mg
    SEL = (df["Grootheid_Code"].isin(["MASSA"])) & (df["Eenheid_Berekend"].isin(["g"]))
    if len(df[SEL]) > 0:
        logger.warning(
            "MASSA bevat 'g' als eenheid, deze meetwaarden zijn geconverteerd naar mg."
        )
    # convert mass to mg
    df.loc[SEL, "Waarde_Berekend"] = df.loc[SEL, "Waarde_Berekend"] * 1000
    df.loc[SEL, "Eenheid_Berekend"] = "mg"

    # set measured values to columns
    df.loc[df["Grootheid_Code"].isin(["AANTL"]), "Aantal"] = df.loc[
        df["Grootheid_Code"].isin(["AANTL"]), "Waarde_Berekend"
    ]
    df.loc[df["Grootheid_Code"].isin(["MASSA"]), "Massa"] = df.loc[
        df["Grootheid_Code"].isin(["MASSA"]), "Waarde_Berekend"
    ]
    df.loc[df["Grootheid_Code"].isin(["BEDKG"]), "Bedekking"] = df.loc[
        df["Grootheid_Code"].isin(["BEDKG"]), "Waarde_Berekend"
    ]
    return df


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def calculate_density(df: pd.DataFrame, density_unit: str) -> pd.DataFrame:
    """Calculate the density for abundances and mass.

    Args:
        df (pd.DataFrame): the input Pandas DataFrame.
        density_unit (str): the column ("Aantal" or "Massa").

    Returns:
        pd.DataFrame: the output DataFrame with density column added.
    """
    df_new = df.copy()
    df_new["Dichtheid_" + density_unit] = np.where(
        (df_new[density_unit].notna()) & (df_new["Support_Eenheid"].isin(["m2", "l"])),
        df_new[density_unit] / df_new["Support"],
        np.NaN,
    )
    return df_new


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def mark_cluster_sample_years(df: pd.DataFrame) -> pd.DataFrame:
    """Marks the clusters of year defined in the configuration file into a new column.

    Args:
        df (pd.DataFrame): the benthos data with unclustered sample years.

    Returns:
        pd.DataFrame: benthos data with added "Monsterjaar_cluster" column.
    """
    df["Monsterjaar_cluster"] = df["Monsterjaar"].astype(str)
    for area in df["Waterlichaam"].dropna().unique():
        for project in df["Project_Code"].unique():
            cluster_config = read_system_config.read_yaml_configuration(
                area + "." + project, "clustered_sample_year.yaml"
            )
            if cluster_config is not None:
                for cluster_years in cluster_config:
                    cluster_year_str = list(map(str, cluster_years))
                    for year in cluster_year_str:
                        if int(year) in df["Monsterjaar"].unique():
                            select = (df["Waterlichaam"] == area) & (
                                df["Project_Code"] == project
                            )
                            df.loc[select, "Monsterjaar_cluster"] = df.loc[
                                select, "Monsterjaar_cluster"
                            ].apply(
                                lambda x: "-".join(
                                    map(str, cluster_year_str)
                                )  # pylint: disable=cell-var-from-loop
                                if x == year  # pylint: disable=cell-var-from-loop
                                else x
                            )
                        else:
                            logger.warning(
                                f"Data voor {year} komt niet voor in de data. "
                                f"Dit geldt voor {area}, {project}."
                            )
    return df


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def extract_ecotoop_code(df: pd.DataFrame, ecotoop_prefix: str) -> pd.DataFrame:
    """Extract the ecotoops with the specified prefix from the Ecotoop_Codes column.

    Args:
        df (pd.DataFrame): the input dataframe.
        ecotoop_prefix (str): the prefix of the ecotoop code.

    Returns:
        pd.DataFrame: the dataframe with the extracted ecotoop codes.
    """
    df = df.copy()

    # set Ecotoop_Codes column to string and split
    df["Ecotoop_Codes"] = df["Ecotoop_Codes"].astype(str)
    codes_split = df["Ecotoop_Codes"].str.split(",", expand=True)

    # Extract the codes starting with the specified prefix and create a new column
    def extract_prefix(row):
        prefix_codes = [
            code.replace(f"{ecotoop_prefix}=", "")
            for code in row
            if code and f"{ecotoop_prefix}=" in code
        ]
        return ",".join(prefix_codes)

    # construct new columname with the dot removed from ecotoop_prefix
    ecotoop_column_name = ecotoop_prefix.replace(".", "")
    ecotoop_column_name = f"Ecotoop_{ecotoop_column_name}"

    df[ecotoop_column_name] = codes_split.apply(extract_prefix, axis=1)

    # replace empty strings with NaN
    df[ecotoop_column_name] = df[ecotoop_column_name].replace(
        r"^\s*$", np.NaN, regex=True
    )
    df["Ecotoop_Codes"] = df["Ecotoop_Codes"].replace("nan", np.nan)
    df["Ecotoop_Codes"] = df["Ecotoop_Codes"].fillna(np.nan)
    return df


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def aggregate_analysis_taxa(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregates the analysis taxa and checks the difference.

    Args:
        df (pd.DataFrame): dataframe which should be aggregated.

    Returns:
        pd.DataFrame: The aggregated taxa.
    """

    difference_kols = [
        "Aantal",
        "Massa",
        "Bedekking",
        "Dichtheid_Massa",
        "Dichtheid_Aantal",
        "Waarde_Berekend",
        "Grootheid_Code",
        "Eenheid_Berekend",
        "Meetpakket_Code",
        "Parameter_Specificatie",
        "Overrule_subspeciesname",
        "Zoetoverrule_taxonname",
        "Zoutoverrule_taxonname",
        "Classificatie_Code",
        "Zoetprotocol_presentie",
        "Zoutprotocol_presentie",
        "Zoutprotocol_biomassa",
        "IsBiomassa_Protocol",
        "IsPresentie_Protocol",
        "Nmonsters",
        "Verrichting_Methoden",
    ]

    aggregate_kols = {
        "Aantal": lambda column: column.sum() if column.notna().any() else np.nan,
        "Massa": lambda column: column.sum() if column.notna().any() else np.nan,
        "Dichtheid_Massa": lambda column: column.sum()
        if column.notna().any()
        else np.nan,
        "Dichtheid_Aantal": lambda column: column.sum()
        if column.notna().any()
        else np.nan,
        "Bedekking": lambda column: column.sum() if column.notna().any() else np.nan,
        "IsBiomassa_Protocol": "any",
        "IsPresentie_Protocol": "any",
    }

    col_list = df.columns.difference(difference_kols).values.tolist()
    df_aggregated = df.groupby(by=col_list, dropna=False, as_index=False).aggregate(
        aggregate_kols
    )

    # add the difference between the grouped and ungrouped rows to the records_removed dictionary
    aggregate_analysis_taxa.records_removed["grouped_diff"] = (
        df.shape[0] - df_aggregated.shape[0]
    )

    # check if Analysis_taxonnaam is unique within each sample(Collectie_Referentie)
    df_check = df_aggregated.groupby(
        ["Collectie_Referentie", "Analyse_taxonnaam"], dropna=False, as_index=False
    ).size()
    df_check = df_check[df_check["size"] > 1]
    if len(df_check) > 0:
        logger.critical(
            f"In de volgende monsters is Analyse_taxonnaam niet uniek: \
                {df_check['Collectie_Referentie'].unique().tolist()}"
        )
        utility.stop_script()

    return df_aggregated


@log_decorator.log_factory(__name__)
def main_benthos_data() -> pd.DataFrame:
    """Processes all the benthos_data functions to import and process the (Aquadesk) data.

    Returns:
        pd.DataFrame: The analysis data.
    """
    waterbodies = read_user_config.read_required_waterbodies()
    projects = read_user_config.read_required_projects()

    # download Aquadesk data if nessesary
    if check_config.check_empty_input_folder():
        locations = read_system_config.read_meetobject_codes(waterbodies, projects)
        locations.sort()
        aquadesk.aquadesk_download(projects, locations)

    # download twn and correct TWN data
    twn_corrected = process_twn.main_twn()

    print("\nStart verwerken benthos data")
    logger.info("Start verwerken benthos data")

    # retrieve required rows and columns
    req_columns = read_system_config.read_column_mapping()
    req_columns_script = req_columns["script_name"]
    data_folder = read_system_config.read_yaml_configuration(
        "data_path", "global_variables.yaml"
    )

    # read the benthos data
    df = read_benthos_data(data_folder)
    nrow_start = len(df)
    print(f"Aantal records benthos data: {nrow_start}")

    # some basic checking
    check_data.check_projects_present(df, projects)
    check_data.check_unique_distinct(
        df,
        ["Collectie_Referentie", "Collectie_DatumTijd", "Meetobject_Code"],
        "Collectie_Referentie",
        "Aquadesk",
    )
    distinct_col = read_system_config.read_sample_properties("script_name")
    check_data.check_unique_distinct(
        df, distinct_col, "Collectie_Referentie", "Aquadesk"
    )
    df = check_data.check_has_taxa(df)

    # some format changes
    df_col = get_required_columns(df, req_columns_script)
    df_app = sample_device_to_column(df_col)
    df_support = support_to_column(df_app)

    # add location and waterbody data from configuration files
    df_location_data = read_system_config.read_locations_config(waterbodies, projects)
    df_waterbodies_data = read_system_config.read_waterbodies_config(waterbodies)

    df_water = add_location_data(df_support, df_location_data)
    df_loc_info = add_waterbody_data(df_water, df_waterbodies_data)

    # some additional filtering, primerly on user defined data
    df_select = filter_waterbodies(df_loc_info, waterbodies)
    df_row = filter_required_rows(df_select)

    # correct taxa
    df_cor = correct_aquadesk_taxa(df_row)

    # check required columns
    exp_col = read_system_config.read_analysis_names()
    exp_config_col = exp_col.loc[exp_col["config"]]["analysis_name"]
    check_data.check_required_col(df_cor, expected_req_col=exp_config_col)

    # calculate and add columns
    df_year = add_sample_year(df_cor)
    df_season = add_season(df_year)
    df_season = check_season(df_season)

    # TWN mappings
    protocol_map = protocol_mapping.main_protocol_mapping(twn_corrected)
    taxa_map = taxa_mapping.main_taxa_mapping(twn_corrected)
    df_mapped = add_mapping.main_add_mapping(
        df_season, twn_corrected, protocol_map, taxa_map
    )

    # calculate and add columns
    df_azo = mark_azoisch(df_mapped)
    df_usage = usage_based_on_samples(df_azo)
    df_pres = presence_to_abundance(df_usage)
    df_abund = abundance_to_presence(df_pres)
    df_biomass = biomass_to_missing(df_abund)
    df_agg = aggregate_taxa(df_biomass)
    df_n_opp = taxa_quantities_to_columns(df_agg)
    df_density_n = calculate_density(df_n_opp, "Aantal")
    df_density_m = calculate_density(df_density_n, "Massa")
    df_cluster_year = mark_cluster_sample_years(df_density_m)
    df_ecotoop = extract_ecotoop_code(df_cluster_year, "ZES.1")
    df_ecotoop = extract_ecotoop_code(df_ecotoop, "EUNIS")

    # write calculated and added columns to output file for user to check
    filenamepath = read_system_config.read_yaml_configuration(
        "calculated_data", "global_variables.yaml"
    )
    utility.export_df(df_ecotoop, filenamepath)
    msg = "De dataset met doorgevoerde correcties, berekende en toegevoegde kolommen is te vinden in: "
    logger.info(msg + filenamepath)
    print(f"\n{msg}\n{filenamepath}\n")

    # aggregate the analysis taxa
    df_aggr = aggregate_analysis_taxa(df_ecotoop)
    df_aggr = abundance_to_presence(df_aggr)

    # distribute the amount over the species
    diversity_levels = read_system_config.read_yaml_configuration(
        "diversity_levels", "global_variables.yaml"
    )

    df_spe = diversity.mark_diversity_species(df_aggr, diversity_levels)
    df_dist = diversity.distribute_taxa_abundances(
        df_spe, diversity_levels, "Dichtheid_Aantal", "nm2_Soort"
    )
    df_dist = diversity.distribute_taxa_abundances(
        df_dist, {"Monster": ["Collectie_Referentie"]}, "Aantal", "n_Soort"
    )

    # perform checks of final df
    exp_total_col = exp_col["analysis_name"]
    req_columns_not_null = req_columns.loc[req_columns["not_null"]]["script_name"]
    df_final = check_data.main_check_data(
        data=df_dist,
        exp_col=exp_total_col,
        col_names_not_be_NA=req_columns_not_null,
    )

    # write input data for next steps to the output file for user to check
    filenamepath = read_system_config.read_yaml_configuration(
        "analysis_data", "global_variables.yaml"
    )
    utility.export_df(df_final, filenamepath)

    msg = "De data gereed voor de analysis van het script staat in: "
    logger.info(msg + filenamepath)
    print(f"{msg}\n{filenamepath}\n")

    return df_final
