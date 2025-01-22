"""This script generates the shannon diversity index."""

"""Two calcucations are possible:
- calculate the shannon diversity index per area
- calculate the shannon diversity index as the mean over the shannon index over the samples 

"""

"""
# File: shannon.py
# Author(s): M. Japink (m.japink@waardenburg.eco) & J. Haringa (j.haringa@waardenburg.eco)
# Creation date: 21-09-2023
# Last modification: 20-02-2024
# Python v3.12.1

"""


import logging
import os
import typing

import numpy as np
import pandas as pd

from preparation import log_decorator


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))

logger = logging.getLogger(__name__)


@log_decorator.log_factory(__name__)
def shannon_index(species_data: pd.Series) -> typing.Any:
    """Calculate the Shannon index. It corrects for zero's and NA's.

    Args:
        species_data (pd.DataFrame): a column with the aggregated density per species.

    Returns:
        typing.Any: the calculated Shannon index as a numerical value.
    """

    # filter out 0 and NA, because cannot calculate Shannon for 0 (division by 0)
    if len(species_data) == 0:
        return 0
    som_ind = sum(species_data)
    pi = species_data / som_ind
    if round(sum(pi), 0) != 1.0:
        logger.warning(
            f"Shannon berekening: som pi moet 1.0 zijn, niet {round(sum(pi), 0)}."
        )
    lnpi = np.log(pi)
    pilnpi = lnpi * pi
    shannon = -sum(pilnpi)
    return shannon


@log_decorator.log_factory(__name__)
def calculate_shannon_over_samples(
    df_density: pd.DataFrame,
    aggregate_columns: list,
    level: str = None,
    by_sample: bool = False,
) -> pd.DataFrame:
    """Calculate the Shannon index as mean over the index per sample.

    Args:
        df (pd.DataFrame): dataframe for which the shannon will be calculated.
        aggregate_columns (list): the columns to aggregate by.
        by_sample (bool): dummy field. so it fits in the analysis tree
    """

    # default group columns
    group_columns = ["Monsterjaar_cluster", "Heeft_Seizoen", "Seizoen", "Gebruik"]
    group_columns[0:0] = aggregate_columns
    if "Waterlichaam" not in aggregate_columns:
        group_columns.insert(0, "Waterlichaam")

    # Filter out animalia and 0.
    df_density = df_density.loc[(df_density["Analyse_taxonnaam"] != "Azoisch")]

    # we asume that the samples are representative for the area, therefore
    # we can calculate the Shannon over all support units

    # filter out 0 and NA, because cannot calculate Shannon for 0 (division by 0)
    df_density = df_density.loc[
        (df_density["nm2_Soort_Monster"] > 0) & df_density["nm2_Soort_Monster"].notna()
    ]

    # get the unique species per sample
    unique_columnslist = ["Collectie_Referentie", "Analyse_taxonnaam"] + group_columns

    df_density_sample_sum = df_density.groupby(
        unique_columnslist,
        dropna=False,
        as_index=False,
    )["nm2_Soort_Monster"].agg("sum")

    # calculate the Shannon index per sample
    unique_column_list = ["Collectie_Referentie"] + group_columns

    df_sample_shannon = (
        df_density_sample_sum.groupby(
            unique_column_list,
            dropna=False,
            group_keys=False,
        )["nm2_Soort_Monster"]
        .apply(lambda x: shannon_index(x))
        .reset_index(name="Shannon_Monster")
    )

    # calculate the mean Shannon index per area
    unique_columnslist = group_columns

    df_sample_shannon_area = (
        df_sample_shannon.groupby(
            unique_columnslist,
            dropna=False,
            as_index=False,
        )["Shannon_Monster"]
        .mean()
        .round(2)
    )
    return df_sample_shannon_area


@log_decorator.log_factory(__name__)
def calculate_shannon_by_area(
    df_density: pd.DataFrame,
    aggregate_columns: list,
    level: str = None,
    by_sample: bool = False,
) -> pd.DataFrame:
    """Calculate the Shannon index per area.

    Args:
        df_density (pd.DataFrame): dataframe with the density data.
        aggregate_columns (list): the columns to aggregate by.
        by_sample (bool): dummy field. so it fits in the analysis tree

    Returns:
        pd.DataFrame: the dataframe with the Shannon index per area.
    """

    # default group columns
    group_columns = ["Monsterjaar_cluster", "Heeft_Seizoen", "Seizoen", "Gebruik"]
    group_columns[0:0] = aggregate_columns
    if "Waterlichaam" not in aggregate_columns:
        group_columns.insert(0, "Waterlichaam")

    # Filter out animalia and 0.
    df_density = df_density.loc[
        (df_density["Analyse_taxonnaam"] != "Azoisch")
        & (df_density["Gebruik"] == "trend")
        & (df_density["Support_Eenheid"] == "m2")
    ]

    variable = "nm2_Soort_" + level

    # filter out 0 and NA, because cannot calculate Shannon for 0 (division by 0)
    density_df_area = df_density.loc[
        (df_density[variable] > 0) & (df_density[variable].notna())
    ]

    # get the unique species per level
    unique_columnslist = ["Analyse_taxonnaam"] + group_columns

    df_density_area_sum = density_df_area.groupby(
        unique_columnslist,
        dropna=False,
        as_index=False,
    )[variable].agg("sum")

    df_shannon_area = (
        df_density_area_sum.groupby(
            group_columns,
            dropna=False,
        )[variable]
        .agg(shannon_index)
        .round(2)
        .reset_index()
    )
    df_shannon_area.rename(columns={variable: "Shannon"}, inplace=True)

    return df_shannon_area
