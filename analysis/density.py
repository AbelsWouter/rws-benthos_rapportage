"""The density of species per area will be calculated."""

"""
# File: density.py
# Author(s): M. Japink (m.japink@waardenburg.eco) & J. Haringa (j.haringa@waardenburg.eco)
# Creation date: 21-01-2023
# Last modification: 20-02-2024
# Python v3.12.1
"""

import logging
import os

import numpy as np
import pandas as pd


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))

from preparation import log_decorator
from preparation import read_system_config
from preparation import utility


logger = logging.getLogger(__name__)


@log_decorator.log_factory(__name__)
def prepare_density(df: pd.DataFrame) -> pd.DataFrame:
    """Add's all configured groups and colors to each sample.
    Sum's the density of the groups and fills the missing groups with 0.

    Args:
        df (pd.DataFrame): dataframe

    Returns:
        pd.DataFrame: the input dataframe with a color column and the missing groups added and filled with 0 .
    """

    # get the groups and colors for the trend group
    trend_group = df["Trendgroep"].dropna().unique()
    df_trend_group = read_system_config.read_groups_config(trend_group)

    # read diversity levels
    subplots_levels = read_system_config.read_yaml_configuration(
        "subplots_levels", "global_variables.yaml"
    )

    # Create a set to store unique values
    subplots_levels_set = set()

    # Iterate through the values in the dictionary and extend the set
    for values_list in subplots_levels.values():
        subplots_levels_set.update(values_list)

    # Convert the set back to a list
    subplots_levels_list = sorted(list(subplots_levels_set))

    unique_columnslist = [
        "Collectie_Referentie",
        "Waterlichaam",
        "Monsterjaar_cluster",
        "Heeft_Seizoen",
        "Seizoen",
        "Support_Eenheid",
        "Gebruik",
        "Trendgroep",
    ] + subplots_levels_list

    df_sample_unique = df[unique_columnslist].drop_duplicates()

    # check unique Collectie_Referentie
    is_unique = not df_sample_unique["Collectie_Referentie"].duplicated().any()
    if not is_unique:
        logger.critical("Collectie_Referentie is niet uniek te aggregeren.")
        utility.stop_script()

    # drop the Azoisch taxa
    df_taxa = df.loc[(df["Analyse_taxonnaam"] != "Azoisch")]
    # and sum by group
    df_group_totals = df_taxa.groupby(
        ["Collectie_Referentie", "Groep"],
        dropna=False,
        as_index=False,
    ).aggregate(
        {
            "Dichtheid_Aantal": lambda column: column.sum()
            if column.notna().any()
            else np.nan,
            "Dichtheid_Massa": lambda column: column.sum()
            if column.notna().any()
            else np.nan,
        }
    )

    # create a cross section of the samples and all the groups
    merged_df = pd.merge(df_sample_unique, df_trend_group, how="left", on="Trendgroep")

    merged_df = pd.merge(
        merged_df, df_group_totals, how="left", on=["Collectie_Referentie", "Groep"]
    )

    # fill nodata with 0
    merged_df["Dichtheid_Massa"].fillna(0, inplace=True)
    merged_df["Dichtheid_Aantal"].fillna(0, inplace=True)

    return merged_df


@log_decorator.log_factory(__name__)
def aggregate_density(
    df: pd.DataFrame,
    aggregate_columns: list,
    level: str = None,
    with_groups: bool = False,
) -> pd.DataFrame:
    """Aggregates the densities to the requested level.

    Args:
        df (pd.DataFrame): dataframe
        aggregate_columns (list): columns to aggregate on.
        with_groups (bool): True if groups should be included in the aggregation.

    Returns:
        pd.DataFrame: the input dataframe with a new column "dichtheid" calculated.
    """

    df = df.copy()
    if len(df) == 0:
        logger.error("Geen data voor het berekenen van de dichtheden.")
        utility.stop_script()

    mean_aggregate_columns = aggregate_columns + [
        "Heeft_Seizoen",
        "Seizoen",
        "Gebruik",
        "Monsterjaar_cluster",
        "Support_Eenheid",
        "Groep",
        "Groepkleur",
    ]

    df_density = df.groupby(
        mean_aggregate_columns,
        dropna=False,
        as_index=False,
    ).aggregate(
        {
            "Dichtheid_Aantal": lambda column: column.mean()
            if column.notna().any()
            else np.nan,
            "Dichtheid_Massa": lambda column: column.mean()
            if column.notna().any()
            else np.nan,
            "Collectie_Referentie": "count",
        }
    )
    df_density.rename(columns={"Collectie_Referentie": "Aantal_Monsters"}, inplace=True)

    # calculate the summarized densities if groups are not requested
    if with_groups == False:
        sum_aggregate_columns = aggregate_columns + [
            "Heeft_Seizoen",
            "Seizoen",
            "Gebruik",
            "Monsterjaar_cluster",
            "Support_Eenheid",
            "Aantal_Monsters",
        ]

        df_density = df_density.groupby(
            sum_aggregate_columns,
            dropna=False,
            as_index=False,
        ).aggregate(
            {
                "Dichtheid_Aantal": lambda column: column.sum()
                if column.notna().any()
                else np.nan,
                "Dichtheid_Massa": lambda column: column.sum()
                if column.notna().any()
                else np.nan,
            }
        )

    # round the densities
    df_density["Dichtheid_Aantal"] = df_density["Dichtheid_Aantal"].round(2)
    df_density["Dichtheid_Massa"] = df_density["Dichtheid_Massa"].round(2)

    return df_density
