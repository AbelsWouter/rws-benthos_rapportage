"""This script generates the species richness."""

"""
Two calcucations are possible:
- calculate the species richness per area
- calculate the species richness as the mean over the counted species per samples 
"""

"""
# Author(s): M. Japink (m.japink@waardenburg.eco) & J. Haringa (j.haringa@waardenburg.eco)
# Creation date: 01-12-2023
# Last modification: 20-02-2024
"""

import logging
import os

import pandas as pd


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))

from preparation import log_decorator


logger = logging.getLogger(__name__)


@log_decorator.log_factory(__name__)
def species_richness_over_samples(
    df: pd.DataFrame,
    aggregate_columns: list,
    level: str = None,
    by_sample: bool = False,
) -> pd.DataFrame:
    """Calculate the nr of species for each waterbody (=soortenrijkdom).

    Args:
        df (pd.DataFrame): dataframe.
        aggregate_columns (list): the columns to aggregate by.
        by_sample (bool): dummy variable, not used.

    Returns:
        pd.DataFrame: a Pandas DataFrame with at least the waterbodies and species.
    """

    df_copy = df.copy(deep=True)

    # default group columns
    group_columns = ["Monsterjaar_cluster", "Heeft_Seizoen", "Seizoen", "Gebruik"]
    group_columns[0:0] = aggregate_columns
    if "Waterlichaam" not in aggregate_columns:
        group_columns.insert(0, "Waterlichaam")

    # filter unique species per sample
    # azoic samples and presence species which count as species have a value of 0 and are rightfully filtered.
    df_copy = df_copy[df_copy["nm2_Soort_Monster"].notnull()]

    # add Azoisch column
    df_copy["Is_Azoisch"] = df_copy["Analyse_taxonnaam"] == "Azoisch"

    # we assume that the samples are representative for the area, therefore
    # we can calculate the species richness over all support units

    # get the unique species per sample
    unique_columnslist = [
        "Collectie_Referentie",
        "Analyse_taxonnaam",
        "Is_Azoisch",
    ] + group_columns
    df_sample_species_unique = df_copy[unique_columnslist].drop_duplicates()

    # calculate the number of unique species per sample
    unique_columnslist = [
        "Collectie_Referentie",
        "Is_Azoisch",
    ] + group_columns

    df_sample_species = df_sample_species_unique.groupby(
        unique_columnslist,
        dropna=False,
        as_index=False,
    )["Analyse_taxonnaam"].count()
    df_sample_species = df_sample_species.rename(
        columns={"Analyse_taxonnaam": "Soortenrijkdom_Monster"}
    )

    # correct count for azoic samples
    df_sample_species["Soortenrijkdom_Monster"] = df_sample_species[
        "Soortenrijkdom_Monster"
    ].where(df_sample_species["Is_Azoisch"] == False, 0)

    # calculate the average number of species per sample per area
    df_sample_species_area = (
        df_sample_species.groupby(
            group_columns,
            dropna=False,
            as_index=False,
        )["Soortenrijkdom_Monster"]
        .mean()
        .round(1)
    )
    return df_sample_species_area


@log_decorator.log_factory(__name__)
def species_richness_by_area(
    df: pd.DataFrame,
    aggregate_columns: list,
    level: str = None,
    by_sample: bool = False,
) -> pd.DataFrame:
    """Calculate the nr of species for each waterbody (=soortenrijkdom).

    Args:
        df (pd.DataFrame): dataframe.
        aggregate_columns (list): the columns to aggregate by.
        level (str): the level to calculate the species richness for.
        by_sample (bool): dummy variable, not used.

    Returns:
        pd.DataFrame: a Pandas DataFrame with at least the waterbodies and species.
    """

    df_copy = df.copy(deep=True)

    # default group columns
    group_columns = ["Monsterjaar_cluster", "Heeft_Seizoen", "Seizoen", "Gebruik"]
    group_columns[0:0] = aggregate_columns
    if "Waterlichaam" not in aggregate_columns:
        group_columns.insert(0, "Waterlichaam")

    # get the unique species for the requested level and count by level
    variable = "nm2_Soort_" + level

    # filter the species for the level
    df_copy = df_copy[df_copy[variable].notnull()]

    # remove Azoic samples
    df_copy = df_copy[df_copy["Analyse_taxonnaam"] != "Azoisch"]

    # get the unique species per level
    unique_columnslist = ["Analyse_taxonnaam"] + group_columns
    df_species_unique = df_copy[unique_columnslist].drop_duplicates()

    # calculate the number of unique species per level
    df_species_area = df_species_unique.groupby(
        group_columns,
        dropna=False,
        as_index=False,
    )["Analyse_taxonnaam"].count()
    df_species_area = df_species_area.rename(
        columns={"Analyse_taxonnaam": "Soortenrijkdom"}
    )

    return df_species_area
