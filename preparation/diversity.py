"""Script to calculate diversity parameters"""

"""
# File: diversity.py
# Author(s): M. Japink (m.japink@waardenburg.eco) & J. Haringa (j.haringa@waardenburg.eco)
# Creation date: 21-01-2023
# Last modification: 20-02-2024
# Python v3.12.1
"""

import logging
import os
import re

import pandas as pd


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))

from typing import List

from preparation import check_decorator
from preparation import log_decorator
from preparation import utility


# Initializing logger object to write custom logs
logger = logging.getLogger(__name__)


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def mark_diversity_species(
    df: pd.DataFrame, diversity_levels: dict[str, List[str]]
) -> pd.DataFrame:
    """Marks the diversity species for every level of analysis.
    Starting at the species rank, all subsequent rank are checked for new taxa.
    New taxa have not been observed at a lower taxonomic rank.
    The levels of analysis are the sample (Collectie-Referentie), area, strata and waterbody.

    Args:
        df (pd.DataFrame): dataframe
        diversity_levels (dict[str, str]): dictionary with the levels of analysis

    Returns:
        pd.DataFrame: a Pandas DataFrame with a boolean column added for every level of analysis.
    """

    # split the dataframe in two parts for given use
    df_trend = df[df["Gebruik"] == "trend"].copy(deep=True)
    df_overig = df[df["Gebruik"] == "overig"].copy(deep=True)

    if len(df_trend) == 0:
        logger.error("Er zijn geen trend monsters aanwezig. Het script wordt gestopt.")
        utility.stop_script()
        return df

    # set all overig to False
    for key, value in diversity_levels.items():
        if len(df_overig) > 0:
            df_overig.loc[:, "IsSoort_" + key] = False

    ### Continue with trend dataframe ###
    # account for taxon-combinations
    df_trend["Analyse_taxonnaam_suffix"] = df_trend.apply(
        lambda row: utility.coalesce(row["Combi"], row["Analyse_taxonnaam"]), axis=1
    )
    df_trend["Hierarchie_suffix"] = (
        df_trend["Analyse_taxonnaam_suffix"] + "|" + df_trend["Hierarchie"]
    )

    # apply suffixes to prevent for finding taxon in part-of-taxon mistakes
    df_trend["Analyse_taxonnaam_suffix"] = (
        df_trend["Analyse_taxonnaam_suffix"].apply(str).apply(utility.add_prefix_suffix)
    )
    df_trend["Hierarchie_suffix"] = (
        df_trend["Hierarchie_suffix"].apply(str).apply(utility.add_prefix_suffix)
    )

    # mark everything up to species-level
    for key, value in diversity_levels.items():
        df_trend.loc[:, "IsSoort_" + key] = False
        # mark all taxon up to the species level
        SEL = df_trend["Order"] <= 1
        df_trend.loc[SEL, "IsSoort_" + key] = True

    # get highest rank
    max_rank = df_trend["Order"].max()

    # divide rest of ranks
    for key, value in diversity_levels.items():
        rank = 2
        while rank <= max_rank:
            # distinct taxonlist of next taxonomic rank
            distinct_columns = value + ["Analyse_taxonnaam_suffix"]
            df_next = df_trend[df_trend["Order"] == rank][
                distinct_columns
            ].drop_duplicates()

            if df_next.empty:  # escape if no taxa in rank
                rank += 1
                continue

            # get all taxa already marked for species diversity
            filter_columns = value + ["Hierarchie_suffix"]
            df_marked = df_trend[df_trend["IsSoort_" + key]][
                filter_columns
            ].drop_duplicates()

            # determine if remaining taxa of current rank are already marked based on hierarchie
            df_new = pd.merge(df_next, df_marked, on=value, how="left")
            df_new["Hierarchie_suffix"] = df_new["Hierarchie_suffix"].apply(
                str
            )  # if hierarchie_calc is empty
            df_new["Presence"] = df_new.apply(
                lambda row: re.search(
                    row["Analyse_taxonnaam_suffix"], row["Hierarchie_suffix"]
                )
                is not None,
                axis=1,
            )
            df_new = (
                df_new[df_new["Presence"]]
                .drop(columns=["Hierarchie_suffix"])
                .drop_duplicates()
            )

            # mark species of current rank for diversity
            join_columns = value + ["Analyse_taxonnaam_suffix"]
            df_extra = pd.merge(df_next, df_new, on=join_columns, how="left")
            df_extra["Extra"] = df_extra["Presence"].isna()
            df_extra = df_extra.drop(columns="Presence")

            # administer marked species in the original dataframe
            join_columns = value + ["Analyse_taxonnaam_suffix"]
            df_trend = pd.merge(df_trend, df_extra, on=join_columns, how="left")
            df_trend["IsSoort_" + key] = df_trend["Extra"].fillna(
                df_trend["IsSoort_" + key]
            )
            df_trend = df_trend.drop(columns="Extra")

            rank += 1
    df_trend.drop(
        columns=["Analyse_taxonnaam_suffix", "Hierarchie_suffix"], inplace=True
    )

    # bring the two parts of the dataframe back together
    df_result = pd.concat([df_trend, df_overig], ignore_index=True)

    # check if number or rows is the same
    if len(df_result) != len(df):
        logger.critical(
            "De lengte van de dataframe is niet gelijk aan de lengte van de input dataframe."
        )
        utility.stop_script()

    # check if sum Dichtheid_Aantal is the same
    check = df_result["Dichtheid_Aantal"].sum() - df["Dichtheid_Aantal"].sum()
    if check >= 1:  # account for roundings
        logger.critical(
            f"De som van de kolom Dichtheid_Aantal is niet gelijk aan de som van de input dataframe. Verschil: {check}"
        )
        utility.stop_script()

    return df_result


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def distribute_taxa_abundances(
    df: pd.DataFrame,
    diversity_levels: dict[str, List[str]],
    abundance_field: str,
    prefix: str,
) -> pd.DataFrame:
    """Distributes the non-species taxa abundances over the species taxa.
    The abundances are distributed over the species taxa based on the hierarchie.
    If only species taxa are present, the abundances are not changed.]

    There is the problem that not always an abundance is given for the species taxa.
    If all species taxa within the hierachie have no abundance,
    the abundance of the parent is evenly distributed over these species taxa.
    If within the group of child species some have abundance and some don't,
    then the abundance of the parent is distributed over the species taxa with abundance.

    Args:
        df (pd.DataFrame): dataframe with marked species distribution
        diversity_levels (dict[str, str]): dictionary with the levels of analysis
        abundance_field (str): the field with abundances to be distributed, Aantal or Dichtheid_Aantal.
        prefix (str): prefix for the columns with the distributed abundances


    Returns:
        pd.DataFrame: a Pandas DataFrame with a boolean column added for every level of analysis.
    """

    # split the dataframe in two parts for given use
    df_trend = df[df["Gebruik"] == "trend"].copy(deep=True)
    df_overig = df[df["Gebruik"] == "overig"].copy(deep=True)

    if len(df_trend) == 0:
        logger.error("Er zijn geen trend monsters aanwezig. Het script wordt gestopt.")
        utility.stop_script()

    # account for taxon-combinations
    df_trend["Analyse_taxonnaam_suffix"] = df_trend.apply(
        lambda row: utility.coalesce(row["Combi"], row["Analyse_taxonnaam"]), axis=1
    )
    df_trend["Hierarchie_suffix"] = (
        df_trend["Analyse_taxonnaam_suffix"] + "|" + df_trend["Hierarchie"]
    )

    # apply suffixes to prevent for finding taxon in part-of-taxon mistakes
    df_trend["Analyse_taxonnaam_suffix"] = (
        df_trend["Analyse_taxonnaam_suffix"].apply(str).apply(utility.add_prefix_suffix)
    )
    df_trend["Hierarchie_suffix"] = (
        df_trend["Hierarchie_suffix"].apply(str).apply(utility.add_prefix_suffix)
    )

    for key, value in diversity_levels.items():
        ### Make two separate datasets for excluded and included species-taxa ###
        # dataframe with excluded species-taxa to distribute as parents
        df_excluded = df_trend[df_trend["IsSoort_" + key] == False]
        # aggregate to sum_parents for distibution
        group_columns = value + ["Analyse_taxonnaam_suffix"]
        df_excluded = (
            df_excluded.groupby(group_columns, dropna=False)
            .agg(sum_parents=(abundance_field, "sum"))
            .reset_index()
        )
        df_excluded.rename(columns={"Analyse_taxonnaam_suffix": "parent"}, inplace=True)

        # dataframe with included species-taxa
        df_included = df_trend[df_trend["IsSoort_" + key] == True]
        # aggregate to sums for correction factor in case isn't properly aggregated by taxon
        group_columns = value + [
            "Analyse_taxonnaam",
            "Analyse_taxonnaam_suffix",
            "Hierarchie_suffix",
            "IsSoort_" + key,
        ]
        df_included = (
            df_included.groupby(group_columns, dropna=False)[abundance_field]
            .sum()
            .reset_index()
        )

        ### Join included and excluded species taxa and calculate the distribution factor ###
        # join included and excluded taxa and
        # select only if excluded taxa are present in the hierarchie of included species-taxa
        df_merged = df_excluded.merge(df_included, on=value, how="left")
        df_merged = df_merged[
            df_merged.apply(
                lambda row: re.search(row["parent"], row["Hierarchie_suffix"])
                is not None,
                axis=1,
            )
        ]

        # calculate the factor from the sum of the childs for each parent
        group_columns = value + ["parent", "sum_parents"]
        df_calc = (
            df_merged.groupby(group_columns, dropna=False)[abundance_field]
            .sum()
            .reset_index()
        )
        df_calc.rename(columns={abundance_field: "sum_childs"}, inplace=True)
        df_calc.reset_index(drop=True, inplace=True)

        # remove sum_parents from df_merged to prevent double columns
        df_merged.drop(columns=["sum_parents"], inplace=True)

        # join calculated factor back on merged dataframe
        join_columns = value + ["parent"]
        df_factor = df_merged.merge(df_calc, on=join_columns, how="left")

        df_factor.loc[df_factor[abundance_field] != 0, "factor"] = (
            df_factor["sum_parents"] / df_factor["sum_childs"]
        )

        ### distibute the parent evenly over the childs when none of them has an abundance ###
        df_factor["occur"] = df_factor.groupby(value + ["parent"])["parent"].transform(
            "size"
        )
        condition = (df_factor[abundance_field] == 0) & (df_factor["sum_childs"] == 0)
        df_factor.loc[condition, "factor"] = (
            df_factor["sum_parents"] / df_factor["occur"]
        )

        # isolate factor
        filter_columns = value + ["Analyse_taxonnaam", "factor", "sum_childs"]
        df_factor = df_factor[filter_columns].copy()

        ### Use the factor to calculate the abundance to each individual data row ###
        # Select for each sample the included species-taxa
        select_columns = value + [
            "Collectie_Referentie",
            "Analyse_taxonnaam",
            abundance_field,
        ]
        select_columns = list(
            dict.fromkeys(select_columns)
        )  # make unique if Collectie_Referentie is already part of value
        SEL = df_trend["IsSoort_" + key] == True
        df_add = df_trend.loc[SEL, select_columns]

        # join the factor
        join_columns = value + ["Analyse_taxonnaam"]
        df_add = df_add.merge(df_factor, on=join_columns, how="right")

        # calculate number to add
        df_add["Add"] = df_add[abundance_field] * df_add["factor"]

        # correct Add to total factor if Dichtheid_Aantal = null and sum childs is 0
        condition = (df_add[abundance_field].isna()) & (df_add["sum_childs"] == 0)
        df_add.loc[condition, "Add"] = df_add["factor"]

        group_columns = value + ["Collectie_Referentie", "Analyse_taxonnaam"]
        group_columns = list(dict.fromkeys(group_columns))
        df_add = df_add.groupby(group_columns, dropna=False)["Add"].sum().reset_index()

        ### Update the data with the calculated distributions ###
        join_columns = value + ["Collectie_Referentie", "Analyse_taxonnaam"]
        join_columns = list(
            dict.fromkeys(join_columns)
        )  # make unique if Collectie_Referentie is already part of value
        df_trend = pd.merge(df_trend, df_add, on=join_columns, how="left")

        # calculate the prefixed column
        df_trend[f"{prefix}_{key}"] = df_trend.apply(
            lambda row: utility.coalesce(row[abundance_field], 0)
            + utility.coalesce(row["Add"], 0)
            if row["IsSoort_" + key]
            else None,
            axis=1,
        )

        # clean
        df_trend.drop(columns=["Add"], inplace=True)

    # clean
    df_trend.drop(
        columns=["Analyse_taxonnaam_suffix", "Hierarchie_suffix"], inplace=True
    )

    # checks
    # only abundances calculated for species-taxa
    for key in diversity_levels:
        check = df_trend[
            (df_trend["IsSoort_" + key] == False)
            & (~df_trend[f"{prefix}_{key}"].isna())
        ]
        if len(check) > 1:
            logger.critical(
                f"Onterecht abundanties toegekend voor {key} voor de volgende monsters en taxa:\n"
                f'{check[["Collectie_Referentie", "Analyse_taxonnaam"]]}'
            )
            utility.stop_script()

        check = df_trend[
            (df_trend["IsSoort_" + key] == True)
            & (df_trend[f"{prefix}_{key}"].isna())
            & (~df_trend[abundance_field].isna())
        ]
        if len(check) > 1:
            logger.critical(
                f"Onterecht geen abundanties toegekend voor de monsters en taxa:\n"
                f'{check[["Collectie_Referentie", "Analyse_taxonnaam"]]}'
            )
            utility.stop_script()

    # sum of calculated abundances equal to abundance field
    group_columns = ["Waterlichaam", "Monsterjaar", "Seizoen"]
    sum_fields = [f"{prefix}_" + s for s in diversity_levels.keys()] + [abundance_field]
    check = (
        df_trend.groupby(group_columns, dropna=False)[sum_fields].sum().reset_index()
    )

    check = check.loc[:, sum_fields].copy()
    for key in [f"{prefix}_" + s for s in diversity_levels.keys()]:
        diff = check[abundance_field].iloc[0] - check[key].iloc[0]
        if abs(diff) >= 1:  # account for roundings
            logger.warning(
                f"De kolom '{key}' heeft een verschil van {diff} met de kolom {abundance_field}."
            )

    # bring the two parts of the dataframe back together
    df_result = pd.concat([df_trend, df_overig], ignore_index=True)

    # check if number or rows is the same
    if len(df_result) != len(df):
        logger.critical(
            "De lengte van de dataframe is niet gelijk aan de lengte van de input dataframe."
        )
        utility.stop_script()

    # check if sum Dichtheid_Aantal is the same
    check = df_result[abundance_field].sum() - df[abundance_field].sum()

    if check >= 1:  # account for roundings
        logger.critical(
            f"De som van de kolom {abundance_field} is niet gelijk aan de som van de input dataframe."
            f"Verschil: {check}"
        )
        utility.stop_script()

    return df_result
