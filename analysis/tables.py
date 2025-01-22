"""This script generates the main tables."""

"""
# File: tables.py
# Author(s): M. Japink (m.japink@waardenburg.eco) & J. Haringa (j.haringa@waardenburg.eco)
# Creation date: 21-01-2023
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

from checks import check_tables
from preparation import log_decorator
from preparation import read_system_config
from preparation import utility


logger = logging.getLogger(__name__)


@log_decorator.log_factory(__name__)
def create_pivot_table(
    df: pd.DataFrame, level: str, variable: str, drop_columns: list = None
) -> pd.DataFrame:
    """Creates a privot table based on a pandas DataFrame.

    Args:
        df (pd.DataFrame): the Pandas DataFrame as input data.
        level (str): the columns for the pivot table.
        variable (str): the variable values in the pivot table.
        drop_columns (list, optional): the columns which should be dropped. Defaults to None.

    Returns:
        pd.DataFrame: _description_
    """
    if "-" in level and level not in df:
        col1, col2 = level.split("-")
        df.loc[:, level] = df[[col1, col2]].apply(
            lambda row: "-".join(map(str, row)), axis=1
        )

    # get column list without level and variabel columns
    col_list = list(df)
    col_list.remove(level)
    col_list.remove(variable)

    if drop_columns is not None:
        for column in drop_columns:
            if column in col_list:
                col_list.remove(column)

    df_pivot = pd.pivot_table(
        data=df,
        index=col_list,
        columns=level,
        values=variable,
        aggfunc="sum",
        fill_value=0,  # waar NA nu 0, maar wordt verderop omgezet naar NA
    ).reset_index()
    return df_pivot


@log_decorator.log_factory(__name__)
def get_min_year(waterbodies: list) -> typing.Any:
    """Retrieve the start year from the configuration file.

    Args:
        waterbodies (list): the waterbodies to retrieve the years from.

    Returns:
        Any: the starting year.
    """
    df_waterbody = read_system_config.read_csv_file(
        filename=read_system_config.read_yaml_configuration(
            "config_waterbodies", "global_variables.yaml"
        )
    )
    min_year = df_waterbody.loc[
        df_waterbody["Waterlichaam"].isin(waterbodies), "Startjaar"
    ].min()
    return min_year


@log_decorator.log_factory(__name__)
def export_samples_a_year(df: pd.DataFrame) -> pd.DataFrame:
    """Creates a table with the number of samples a year by first creating
    a full dataframe including all the years and meetobject_codes, and then
    joining this to the benthos data.

    Args:
        df (pd.DataFrame): dataframe with the benthos data.
    """

    df_copy = df.copy()
    empty_value_marker = "marker"

    heading = [
        "Waterlichaam",
        "Gebied",
        "Strata",
        "Ecotoop_Codes",
        "Meetobject_Code",
        "Bemonsteringsapp",
        "Gebruik",
        "Seizoen",
    ]
    # set all heading columns to string
    df_copy[heading] = df_copy[heading].astype(object)

    # Replace empty Area's with "overig" if there are areas
    count_per_column = df["Gebied"].count()
    if count_per_column > 0:
        df_copy["Gebied"] = df_copy["Gebied"].fillna("overig")

    # Replace NaN values with a marker value
    columns_to_fill = ["Strata", "Ecotoop_Codes", "Gebied"]
    df_copy[columns_to_fill] = df_copy[columns_to_fill].fillna(empty_value_marker)

    # make cross table
    min_year = get_min_year(df_copy["Waterlichaam"].unique().tolist())
    max_year = df_copy["Monsterjaar"].max()

    l_jaar = pd.DataFrame({"Monsterjaar": list(range(min_year, max_year + 1))})
    l_code = df_copy[heading].drop_duplicates()
    l_code["Gebied"] = l_code["Gebied"].fillna("overig")
    df_cross = pd.merge(l_jaar, l_code, how="cross")

    # aggregate the samples a year
    df_agg = df_copy.groupby(
        heading + ["Monsterjaar"],
        dropna=False,
        as_index=False,
    ).agg(Nmonsters=("Collectie_Referentie", "nunique"))

    # join the samples a year with the cross table
    df_full = pd.merge(
        df_cross,
        df_agg,
        how="left",
        on=heading + ["Monsterjaar"],
    )

    sum_samples_number_a_year = pd.pivot_table(
        data=df_full,
        index=heading,
        columns="Monsterjaar",
        values="Nmonsters",
        aggfunc="sum",
        fill_value=0,  # waar NA nu 0, maar wordt verderop omgezet naar NA
    ).reset_index()

    ### convert all the numeric columns (years) from 0 to empty cell ###
    # get the columns with the years
    col_list_years = list(sum_samples_number_a_year)
    for column in heading:
        col_list_years.remove(column)

    # replace 0 with NA
    sum_samples_number_a_year[col_list_years] = sum_samples_number_a_year[
        col_list_years
    ].astype(int)
    sum_samples_number_a_year[col_list_years] = np.where(
        sum_samples_number_a_year[col_list_years] == 0,
        np.nan,
        sum_samples_number_a_year[col_list_years],
    )
    logger.debug(f"sum_samples_number_a_year= \n {sum_samples_number_a_year}")

    ### add the sum of the years ###
    sum_samples_number_a_year["N_jaren"] = sum_samples_number_a_year[
        col_list_years
    ].count(axis=1)

    ### clean up the dataframe ###
    # Replace NaN values with a marker for the specified columns
    sum_samples_number_a_year.replace(empty_value_marker, np.nan, inplace=True)
    sum_samples_number_a_year[columns_to_fill] = sum_samples_number_a_year[
        columns_to_fill
    ].astype(object)

    utility.export_df(sum_samples_number_a_year, "./output/Monsters_per_jaar.xlsx")
    return sum_samples_number_a_year.reset_index(drop=True)


def make_species_list(df: pd.DataFrame, year: int = None) -> pd.DataFrame:
    """Creates a species list for each waterbody and includes the habitat species
    for the protected areas/N2000 areas. For the Noordzee, the sampling techniques are included.

    Args:
        df (pd.DataFrame): dataframe with the species data.
        year (int, optional): the year to use. Defaults to None.

    Returns:
        pd.DataFrame: dataframe with the species list.
    """

    df_copy = df.copy()

    heading = [
        "Waterlichaam",
        "Gebied",
        "Strata",
        "Ecotoop_Codes",
        "Meetobject_Code",
        "Bemonsteringsapp",
        "Gebruik",
    ]
    # set all heading columns to string
    df_copy[heading] = df_copy[heading].astype(object)

    # Replace empty Area's with "overig" if there are areas
    count_per_column = df_copy["Gebied"].count()
    if count_per_column > 0:
        df_copy["Gebied"] = df_copy["Gebied"].fillna("overig")

    habitat_species = check_tables.check_habitat_n2000_species_conform_twn()

    for waterbody in df_copy["Waterlichaam"].unique():
        if waterbody == "Noordzee":
            df_species_waterbody = df_copy[df_copy["Waterlichaam"] == waterbody][
                [
                    "Monsterjaar",
                    "Waterlichaam",
                    "Gebied",
                    "Bemonsteringsapp",
                    "Analyse_taxonnaam",
                ]
            ]
        else:
            df_species_waterbody = df_copy[df_copy["Waterlichaam"] == waterbody][
                [
                    "Monsterjaar",
                    "Waterlichaam",
                    "Gebied",
                    "Analyse_taxonnaam",
                ]
            ]

        if year is None:
            year = df_species_waterbody["Monsterjaar"].max()

        df_species_waterbody_year = df_species_waterbody[
            df_species_waterbody["Monsterjaar"] == year
        ]

        df_hr_species_waterbody = df_species_waterbody_year.merge(
            habitat_species[["Habitattype", "Analyse_taxonnaam", "N2000-gebied"]],
            left_on=["Analyse_taxonnaam", "Waterlichaam"],
            right_on=["Analyse_taxonnaam", "N2000-gebied"],
            how="left",
        )

        df_hr_species_waterbody = df_hr_species_waterbody.merge(
            habitat_species[["Habitattype", "Analyse_taxonnaam", "N2000-gebied"]],
            left_on=["Analyse_taxonnaam", "Gebied"],
            right_on=["Analyse_taxonnaam", "N2000-gebied"],
            how="left",
        )
        df_hr_species_waterbody = df_hr_species_waterbody.rename(
            columns={
                "Habitattype_x": "Habitattype_Waterlichaam",
                "N2000-gebied_x": "N2000-gebied_Waterlichaam",
                "Habitattype_y": "Habitattype_Gebied",
                "N2000-gebied_y": "N2000-gebied_Gebied",
            }
        )
        df_hr_species_waterbody = df_hr_species_waterbody.drop_duplicates()
        utility.check_and_make_output_subfolder("./output/" + waterbody)
        utility.export_df(
            df_hr_species_waterbody,
            f"./output/{waterbody}/{waterbody} - Soortenlijst - {str(year)}.xlsx",
        )

    return df_hr_species_waterbody
