"""A table with newly found species, disappeared species and returned species will be generated."""

"""
# File: new_disappeared_species.py
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

from analysis import tables
from preparation import log_decorator
from preparation import read_system_config
from preparation import utility


logger = logging.getLogger(__name__)


@log_decorator.log_factory(__name__)
def select_observed_species(
    df: pd.DataFrame,
    waterbody: list[str],
    min_year: int,
    max_year: int,
) -> pd.DataFrame:
    """Select species within the waterbody and period range,
    groups them (aggregation) and if the amount is > 0, it adds it to observed.

    Args:
        df (pd.DataFrame): dataframe with the data.
        waterbody (list[str]): the list of waterbodies.
        min_year (int): the start year of the period.
        max_year (int): the end year of the period.

    Returns:
        pd.DataFrame: dataframe with the observed species.
    """
    if min_year == max_year:
        period_range = [max_year]
    else:
        period_range = list(range(min_year, max_year + 1))
    df_copy = df.copy()
    df_select = df_copy.loc[
        (df_copy["Waterlichaam"].isin(waterbody))
        & (df_copy["Monsterjaar"].isin(period_range))
    ]
    df_select_waterbody = df_select.copy()
    df_select_waterbody["Gebied"] = df_select_waterbody["Gebied"].fillna("overig")
    grouped = (
        df_select_waterbody.groupby(["Analyse_taxonnaam", "Gebied"], dropna=False)
        .agg(Nsum=("N", "sum"))
        .reset_index()
    )
    observed = grouped[grouped["Nsum"] > 0].reset_index()[
        ["Analyse_taxonnaam", "Gebied"]
    ]
    return observed


@log_decorator.log_factory(__name__)
def select_not_observed_species(
    df: pd.DataFrame, waterbody: list[str], min_year: int, max_year: int
) -> pd.DataFrame:
    """Select species within the waterbody and period range,
    groups them (aggregation) and if the amount is < 0, it adds it to non-observed.

    Args:
        df (pd.DataFrame): dataframe with the data.
        waterbody (list[str]): the list of waterbodies.
        min_year (int): the start year of the period.
        max_year (int): the end year of the period.

    Returns:
        pd.DataFrame: dataframe with the non-observed species.
    """
    df_copy = df.copy()
    period_range = list(range(min_year, max_year))
    df_select = df_copy.loc[
        (df_copy["Waterlichaam"].isin(waterbody))
        & (df_copy["Monsterjaar"].isin(period_range))
    ]
    grouped = (
        df_select.groupby(["Analyse_taxonnaam", "Gebied"])
        .agg(Nsum=("N", "sum"))
        .reset_index()
    )
    not_observed = grouped[grouped["Nsum"] == 0].reset_index()[
        ["Analyse_taxonnaam", "Gebied"]
    ]
    return not_observed


@log_decorator.log_factory(__name__)
def create_full_dataframe(
    df: pd.DataFrame, waterbody: list[str], min_year: int, max_year: int
) -> pd.DataFrame:
    """Create a dataframe with the observed and non-observed species
    for each waterbody and each year in the period.

    Args:
        df (pd.DataFrame): dataframe with the species data.
        waterbody (list[str]): the list of waterbodies.
        min_year (int): The starting year of the period.
        max_year (int): The ending year of the period.

    Returns:
        pd.DataFrame: dataframe with the observed and non-observed species.
    """
    # subset waterlichaam
    df_copy = df.copy()
    df_select_water = df_copy.loc[df_copy["Waterlichaam"].isin(waterbody)]
    df_taxa = df_copy[["Analyse_taxonnaam", "Waterlichaam", "Gebied"]].drop_duplicates()
    years = pd.DataFrame({"Monsterjaar": list(range(min_year, max_year + 1))})

    # cross join om nulwaarnemingen toe te voegen
    df_cross = pd.merge(df_taxa, years, how="cross")
    df_cross = df_cross.rename(columns={0: "Monsterjaar"})

    # aggregate per waterlichaam, monsterjaar, taxonnaam
    # N = aanwezigheid; 1=aanwezig, 0 = afwezig
    # Nsum = aantal beestjes opgeteld per jaar per taxa per waterlichaam
    df_agg = (
        df_select_water.groupby(["Analyse_taxonnaam", "Monsterjaar", "Gebied"])
        .agg(Tot_meetwaarde=("Aantal", "sum"))
        .reset_index()
    )
    df_agg["N"] = 1
    df_full = pd.merge(
        df_cross,
        df_agg,
        how="left",
        on=["Analyse_taxonnaam", "Monsterjaar", "Gebied"],
    )

    return df_full


def samples_a_year_each_area(
    df: pd.DataFrame, min_year: int, max_year: int
) -> pd.DataFrame:
    """Calculates how many samples a year are taken for each area.

    Args:
        df (pd.DataFrame): dataframe with the taxa data.
        min_year (int): the first year.
        max_year (int): the last year.

    Returns:
        pd.DataFrame: the samples a year for each area.
    """
    df_copy = df.copy()

    year = pd.DataFrame({"Monsterjaar": list(range(min_year, max_year + 1))})
    area = df_copy[["Gebied"]].drop_duplicates()
    df_cross = pd.merge(year, area, how="cross")

    df_agg = (
        df_copy.groupby(["Monsterjaar", "Gebied"])
        .agg(Nmonsters=("Collectie_Referentie", "nunique"))
        .reset_index()
    )

    df_full = pd.merge(df_cross, df_agg, how="left", on=["Monsterjaar", "Gebied"])

    df_samples = pd.pivot_table(
        data=df_full,
        index=["Gebied"],
        columns="Monsterjaar",
        values="Nmonsters",
        aggfunc="sum",
    ).reset_index()
    return df_samples


@log_decorator.log_factory(__name__)
def determine_new_returned_disappeared(
    dataframe: pd.DataFrame, waterbody: list[str], min_year: int, max_year: int
) -> typing.Any:
    """Create a full dataframe with for each year the number of observed species.
    This dataframe is used to create a list of 1) observed taxa and 2) non-observed taxa.
    These are used to create dataframe with 1) new taxa, 2) taxa which are returned, and 3) taxa
    which have disappeared.

    Args:
        dataframe (pd.DataFrame): dataframe with the species data.
        waterbody (list[str]): The waterbodies selected by the user.
        min_year (int): the start year of the period.
        max_year (int): the end year of the period.

    Returns:
        pd.DataFrame: The Dataframes with the new, returned and disappeared taxa.
    """
    df_samples = samples_a_year_each_area(
        dataframe, min_year=min_year, max_year=max_year
    )

    df_full = create_full_dataframe(
        df=dataframe, waterbody=waterbody, min_year=min_year, max_year=max_year
    )
    df_full.rename(columns={"Waterlichaam_x": "Waterlichaam"}, inplace=True)
    # gesommeerde aantalllen per jaar voor alle taxa per waterlichaam
    sum_taxon_number_a_year = pd.pivot_table(
        data=df_full,
        index=["Gebied", "Analyse_taxonnaam"],
        columns="Monsterjaar",
        values="Tot_meetwaarde",
        aggfunc="sum",
    ).reset_index()

    # lijst nieuwe taxa waargenomen
    observed_last_year = select_observed_species(
        df=df_full, waterbody=waterbody, min_year=max_year, max_year=max_year
    )
    # lijst van taxa niet waargenomen
    not_observed_before = select_not_observed_species(
        df=df_full, waterbody=waterbody, min_year=min_year, max_year=max_year
    )

    l_new = pd.merge(
        observed_last_year,
        not_observed_before,
        how="inner",
        on=["Analyse_taxonnaam", "Gebied"],
    )

    # lijst van verdwenen taxa
    first_period = select_observed_species(
        df=df_full, waterbody=waterbody, min_year=min_year, max_year=max_year - 9
    )
    not_last_period = select_not_observed_species(
        df=df_full, waterbody=waterbody, min_year=max_year - 9, max_year=max_year + 1
    )
    l_disappeared = pd.merge(
        first_period,
        not_last_period,
        how="inner",
        on=["Analyse_taxonnaam", "Gebied"],
    )

    # lijst van teruggevonden taxa
    not_past_period = select_not_observed_species(
        df_full, waterbody, min_year=max_year - 10, max_year=max_year
    )
    l_returned_between = pd.merge(
        observed_last_year,
        not_past_period,
        how="inner",
        on=["Analyse_taxonnaam", "Gebied"],
    )
    l_returned = pd.merge(
        l_returned_between,
        first_period,
        how="inner",
        on=["Analyse_taxonnaam", "Gebied"],
    )

    # generate output
    df_new = pd.merge(
        l_new,
        sum_taxon_number_a_year,
        on=["Analyse_taxonnaam", "Gebied"],
        how="left",
    )
    df_new["Kenmerk"] = "nieuw"

    df_returned = pd.merge(
        l_returned,
        sum_taxon_number_a_year,
        on=["Analyse_taxonnaam", "Gebied"],
        how="left",
    )
    df_returned["Kenmerk"] = "terug"

    df_disappeared = pd.merge(
        l_disappeared,
        sum_taxon_number_a_year,
        on=["Analyse_taxonnaam", "Gebied"],
        how="left",
    )
    df_disappeared["Kenmerk"] = "verdwenen"
    logger.debug(f"df_monsters= \n {df_samples}")
    logger.debug(f"df_nieuw= \n {df_new}")
    logger.debug(f"df_terug= \n {df_returned}")
    logger.debug(f"df_verdwenen= \n {df_disappeared}")
    return df_samples, df_new, df_returned, df_disappeared


@log_decorator.log_factory(__name__)
def determine_most_recent_observation(
    df: pd.DataFrame, min_year: int, max_year: int
) -> pd.DataFrame:
    """Iterate over each taxa and each year to check if the observed value
    is greater than zero (which means an the taxa was in the sample).

    Args:
        df (pd.DataFrame): The input Pandas DataFrame
        min_year (int): the starting year
        max_year (int): the end year

    Returns:
        pd.DataFrame: dataframe with the laatste_wrn column added.
    """
    col_names = df.columns.tolist()
    col_names += ["Laatste_wrn"]
    period = list(range(min_year, max_year))
    df["Laatste_wrn"] = min_year
    for taxa in range(df.shape[0]):
        for i in range(len(period)):
            if df.iloc[taxa, i + 2] > 0:
                min_year = period[i]
        df.at[taxa, "Laatste_wrn"] = min_year
    df.columns = col_names
    return df


@log_decorator.log_factory(__name__)
def abundance_to_presence(
    df_new: pd.DataFrame, df_returned: pd.DataFrame, df_disappeared: pd.DataFrame
) -> typing.Any:
    """Write X for presence and - for non-presence instead of a number.

    Args:
        df_new (pd.DataFrame): dataframe with the new species.
        df_returned (pd.DataFrame): dataframe with the species that are found again.
        df_disappeared (pd.DataFrame): dataframe with the disappeared species.

    Returns:
        tuple(pd.DataFrame, pd.DataFrame, pd.DataFrame): a tuple with dataframe of the new,
        disappeared and found again species with X or -.
    """
    col_list_nieuw = df_new.columns.difference(
        ["Gebied", "Monsterjaar", "Analyse_taxonnaam", "Kenmerk"]
    ).values.tolist()
    col_list = df_returned.columns.difference(
        ["Gebied", "Monsterjaar", "Analyse_taxonnaam", "Kenmerk", "Laatste_wrn"]
    ).values.tolist()
    df_new[col_list_nieuw] = df_new[col_list_nieuw].astype(float)
    df_returned[col_list] = df_returned[col_list].astype(float)
    df_disappeared[col_list] = df_disappeared[col_list].astype(float)
    df_new[col_list_nieuw] = np.where(df_new[col_list_nieuw] == 0.0, "-", "X")
    df_returned[col_list] = np.where(df_returned[col_list] == 0.0, "-", "X")
    df_disappeared[col_list] = np.where(df_disappeared[col_list] == 0.0, "-", "X")
    return df_new, df_returned, df_disappeared


@log_decorator.log_factory(__name__)
def merge_new_disappeared_returned(
    df: pd.DataFrame, waterbody: list[str], min_year: int, max_year: int
) -> pd.DataFrame:
    """Determines the new, returned and disappeared species and samples.
    Then, it uses these three to retrieve the last year with the most recent observations
    and concatenates the thee DataFrames.

    Args:
        df (pd.DataFrame): The input Pandas DataFrame
        waterbody (list[str]): a list of waterbodies
        min_year (int): the starting year
        max_year (int): the end year

    Returns:
        pd.DataFrame: dataframe with the new, found again and disappeared species.
    """
    df_copy = df.copy()
    df_copy["Gebied"] = df_copy["Gebied"].fillna("overig")

    (
        df_samples,
        df_new,
        df_returned,
        df_disappeared,
    ) = determine_new_returned_disappeared(
        df_copy,
        waterbody,
        min_year,
        max_year,
    )
    df_returned = determine_most_recent_observation(df_returned, min_year, max_year)
    df_disappeared = determine_most_recent_observation(
        df_disappeared, min_year, max_year
    )
    df_new, df_returned, df_disappeared = abundance_to_presence(
        df_new, df_returned, df_disappeared
    )
    return df_samples, df_new, df_returned, df_disappeared


@log_decorator.log_factory(__name__)
def mark_new_exotic_species(df: pd.DataFrame, sample_year: int) -> pd.DataFrame:
    """Marks the exotic species in the newly found species.

    Args:
        df (pd.DataFrame): dataframe with the newly found species.
        sample_year (_type_): The sample year.

    Returns:
        pd.DataFrame: dataframe with the exotic species.
    """
    exotic_list = read_system_config.read_csv_file(
        read_system_config.read_yaml_configuration(
            "config_exotics", "global_variables.yaml"
        )
    )
    exotic_list = exotic_list.rename(columns={"TWN": "Analyse_taxonnaam"})
    merge_exotic = pd.merge(df, exotic_list, on="Analyse_taxonnaam", how="left")
    merge_copy = merge_exotic[["Analyse_taxonnaam", "Exoot", "Toelichting"]].copy()
    merge_copy["Monsterjaar"] = sample_year
    select_exotic = merge_copy[merge_copy["Exoot"].notna()]
    unique_exotic = select_exotic.drop_duplicates()
    if len(unique_exotic[unique_exotic["Exoot"].notna()]) == 0:
        no_exotic = pd.DataFrame(columns=["Geen nieuwe exoten gevonden"])
        return no_exotic
    return unique_exotic


@log_decorator.log_factory(__name__)
def export_to_excel(
    df_samples: pd.DataFrame,
    df_new: pd.DataFrame,
    df_returned: pd.DataFrame,
    df_disappeared: pd.DataFrame,
    df_exotic: pd.DataFrame,
    waterbody: str,
) -> None:
    """Write the output of the new, disappeared and returned species.

    Args:
        df_samples (pd.DataFrame): dataframe with the samples.
        df_new (pd.DataFrame): dataframe with the newly found species.
        df_returned (pd.DataFrame): dataframe with the returned (after 10 year not found) species.
        df_disappeared (pd.DataFrame): dataframe with the disappeared species.
    """

    try:
        utility.check_and_make_output_subfolder(".//output//" + waterbody)
        # pylint: disable=abstract-class-instantiated
        with pd.ExcelWriter(
            f"./output/{waterbody}/{waterbody} - Nieuw_terug_verdwenen.xlsx",
            engine="openpyxl",
        ) as writer:
            df_samples.to_excel(writer, sheet_name="monsters per jaar", index=False)
            df_new.to_excel(writer, sheet_name="nieuwe taxa", index=False)
            df_disappeared.to_excel(writer, sheet_name="verdwenen taxa", index=False)
            df_returned.to_excel(writer, sheet_name="teruggevonden taxa", index=False)
            df_exotic.to_excel(writer, sheet_name="exoten", index=False)
    except Exception:
        logger.error(
            "Er treed een fout op het exporteren naar Excel"
            "voor de nieuw/verdwenen/teruggevonden soorten."
        )
        logger.debug("Error Message with %s", "arguments", exc_info=True)
        utility.stop_script()


@log_decorator.log_factory(__name__)
def main_new_disappeared_returned_species(df: pd.DataFrame) -> None:
    """Merges the new/disappeared/returned species and marks the exotic species.

    Args:
        df (pd.DataFrame): dataframe with the taxa data.
    """
    for waterbody in df["Waterlichaam"].unique().tolist():
        df_waterbody = df.loc[df["Waterlichaam"].isin([waterbody])]
        min_year = tables.get_min_year([waterbody])
        max_year = df_waterbody["Monsterjaar"].max()
        logger.debug(
            f"The starting year is {min_year} and the last year is {max_year}."
        )

        (
            df_samples,
            df_new,
            df_returned,
            df_disappeared,
        ) = merge_new_disappeared_returned(
            df=df_waterbody,
            waterbody=[waterbody],
            min_year=min_year,
            max_year=max_year,
        )
        exotic_species = mark_new_exotic_species(df=df_new, sample_year=max_year)

        export_to_excel(
            df_samples, df_new, df_returned, df_disappeared, exotic_species, waterbody
        )
    msg = "Nieuw, verdwenen en weer verschenen taxa: gereed"
    logger.info(msg)
    print(msg)
