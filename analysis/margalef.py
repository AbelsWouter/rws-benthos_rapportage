"""The Margalef's Index will be calculated."""

"""
# File: margalef.py
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


from typing import Any

from preparation import log_decorator


logger = logging.getLogger(__name__)


@log_decorator.log_factory(__name__)
def calculate_margalef_over_samples(
    df: pd.DataFrame, aggregate_columns: list, level: str = None, by_sample: bool = True
) -> pd.DataFrame:
    """Calculate the Margalef index as mean over the index per sample.

    Args:
        df (pd.DataFrame): dataframe for which the index is calculated.
        aggregate_columns (list): list of columns that will be aggregated.
        by_sample (bool): if True, the index will be calculated per sample.
        If False, the index will be calculated per area.

    Returns:
        pd.DataFrame: dataframe with the Margalef's index.
    """

    # default group columns
    group_columns = ["Monsterjaar_cluster", "Heeft_Seizoen", "Seizoen", "Gebruik"]
    group_columns[0:0] = aggregate_columns
    if "Waterlichaam" not in aggregate_columns:
        group_columns.insert(0, "Waterlichaam")

    # Filter out animalia and NA.
    df_select = df.loc[
        (df["Analyse_taxonnaam"] != "Azoisch")
        & (df["n_Soort_Monster"].notna())
        & (df["Margalef"].notna())
    ]

    # check if there are any samples left
    if len(df_select) == 0:
        logger.debug("Er zijn geen samples over om de Margalef's index te berekenen.")
        return pd.DataFrame()

    # get the unique species per sample
    unique_columnslist = ["Collectie_Referentie", "Analyse_taxonnaam"] + group_columns

    df_sample_sum = df_select.groupby(
        unique_columnslist,
        dropna=False,
        as_index=False,
    )["n_Soort_Monster"].agg("sum")

    # Calculate the Margalef index per sample
    unique_column_list = ["Collectie_Referentie"] + group_columns

    df_margalef = df_sample_sum.groupby(
        unique_column_list,
        dropna=False,
        as_index=False,
        group_keys=False,
    )["n_Soort_Monster"].apply(lambda x: margalef_index(x))
    df_margalef = df_margalef.rename(columns={"n_Soort_Monster": "Margalef_Monster"})

    # calculate the mean Margalef index per area
    unique_columnslist = group_columns

    df_margalef_area = (
        df_margalef.groupby(unique_columnslist, dropna=False, as_index=False)[
            "Margalef_Monster"
        ]
        .mean()
        .round(2)
    )
    return df_margalef_area


def margalef_index(species_data: pd.Series) -> Any:
    """Use the number of species to calculate the Margalef's index.
    This is a metric for the purpose of measuring diversity.
    If there are 1 or less number of species, the index will not be calculated.

    Args:
        S (pd.Series): The number of species for one sample.

    Returns:
        int: The Margalef's Index.
    """

    # filter out 0 and NA, because cannot calculate Shannon for 0 (division by 0)
    if len(species_data) == 0:
        return 0

    # S = total nr of species observed
    # N = total nr of individuals
    S = len(species_data)
    N = sum(species_data)

    if N == 0:
        logger.warning(
            f"N (totaal aantal (nr)) = {N}, wat resulteert in NaN voor de Margalef's index."
        )
        return None

    D = (S - 1) / np.log(N)
    index = D.item()
    return index
