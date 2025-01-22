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

import numpy as np
import pandas as pd


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))

from preparation import check_decorator
from preparation import log_decorator
from preparation import process_twn
from preparation import read_system_config
from preparation import utility


logger = logging.getLogger(__name__)


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def create_taxonomy(valid_twn: pd.DataFrame) -> pd.DataFrame:
    """Creates the taxonomy by adding the taxonomic order and checks.

    Args:
        valid_twn (pd.DataFrame): the valid twn taxa.

    Returns:
        pd.DataFrame: the TWN data with the taxonomy.
    """

    # select relevant twn data
    taxonomy = valid_twn[["Name", "Parentname", "Taxonrank"]]

    # add rank order
    rank_order = read_system_config.read_csv_file(
        read_system_config.read_yaml_configuration(
            "config_taxonomic_order", "global_variables.yaml"
        )
    )
    taxonomy = taxonomy.merge(rank_order, on="Taxonrank", how="left")

    # check for missing taxonorders
    check = len(taxonomy[taxonomy["Order"].isnull()])
    if check:
        logger.error(
            "Er zijn onbekende taxonranks aangetroffen in de TWN, vul het configuatiebestand aan."
        )
        utility.stop_script()

    return taxonomy


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def recode_subspecies(valid_twn: pd.DataFrame, taxonomy: pd.DataFrame) -> pd.DataFrame:
    """Recodes the twn taxa below the species level to species level.

    Args:
        twn (pd.DataFrame): a Pandas DataFrame with the twn data.

    Returns:
        pd.DataFrame: a Pandas DataFrame with the below species to species conversion.
    """

    # add parent rank
    parent_taxon = taxonomy.loc[:, ("Name", "Taxonrank", "Order")]
    parent_taxon.rename(
        columns={
            "Name": "Childname",
            "Taxonrank": "Parentrank",
            "Order": "Parentorder",
        },
        inplace=True,
    )
    taxonomy = taxonomy.merge(
        parent_taxon, left_on="Parentname", right_on="Childname", how="left"
    )

    # define start twn
    df = valid_twn[["Name"]].copy()
    df["Twn_name"] = df["Name"].values

    # rename all ranks below species
    x = 1
    while x > 0:
        df = df.merge(taxonomy, on="Name", how="left")
        SEL = (df["Order"] < 1) & (~df["Parentorder"].isna())
        df.loc[SEL, "Name"] = df.loc[SEL, "Parentname"]
        del SEL

        # calculate the number of rows still to process
        x = len(df[(df["Parentorder"] < 1) & (~df["Parentorder"].isna())])

        # drop all  but the "twn_name" and "species_name" columns
        df = df[["Twn_name", "Name"]]

    return df


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def glue_hierarchie(
    twn_recodedsubspecies: pd.DataFrame, taxonomy: pd.DataFrame
) -> pd.DataFrame:
    """Checks and adds the hierarhical order.

    Args:
        twn_recodedsubspecies (pd.DataFrame): recoded below species to species.
        taxonomy (pd.DataFrame): the taxonomic order.

    Returns:
        pd.DataFrame: the taxa with the hierarchy added.
    """

    # add extra fields
    twn_recodedsubspecies.loc[:, "Hierarchie"] = pd.NA
    twn_recodedsubspecies.loc[:, "Parent"] = twn_recodedsubspecies["Name"].values

    # add rank and order
    df = twn_recodedsubspecies.merge(
        taxonomy[["Name", "Taxonrank", "Order"]], on="Name", how="left"
    )

    # check for unexpected errors
    check = df[df["Order"] < 1]
    if len(check) > 0:
        logger.error(
            f'Onverwachte subspecies tijdens het opbouwen van de hierarchie, voor de volgende taxa: \n {check["Name"]}'
        )
        utility.stop_script()

    check = df[df["Taxonrank"].isnull()]
    if len(check) > 0:
        logger.error(
            f'Er zijn onbekende taxonranks aangetroffen in de TWN, vul het configuatiebestand aan: \n {check["Name"]}.'
        )
        utility.stop_script()

    # join all successive parents into one hierarchie string, taxa separated by a pipe '|'
    x = len(df[~df["Parent"].isnull()])
    while x > 0:
        result_df = df.merge(
            taxonomy[["Name", "Parentname"]],
            left_on="Parent",
            right_on="Name",
            how="left",
            suffixes=("", "_DROP"),
        ).filter(
            regex="^(?!.*_DROP)"
        )  # pandas hack to remove duplicate_columns
        result_df["Parent"] = result_df["Parentname"]
        result_df["Hierarchie"] = (
            result_df[["Hierarchie", "Parentname"]].astype(str).agg("|".join, axis=1)
        )
        result_df = result_df.drop(columns=["Parentname"])
        df = result_df.copy()

        # check if any parent left
        x = len(df[~df["Parent"].isnull()])

    # clean hierarchie column
    df["Hierarchie"] = df["Hierarchie"].str.replace(r"<NA>", "", regex=True)
    df["Hierarchie"] = df["Hierarchie"].str.replace(r"\|nan", "", regex=True)
    df["Hierarchie"] = df["Hierarchie"].str.replace(r"nan|", "", regex=True)
    df["Hierarchie"] = df["Hierarchie"].str.replace(r"^\|", "", regex=True)

    # check if all hierarchies -except Animalia end with Animalia
    check = df[
        (~df["Hierarchie"].str.contains("Animalia")) & (df["Twn_name"] != "Animalia")
    ]
    if len(check) != 0:
        logger.error(
            f'Voor de volgende taxa klopt de hierarchie niet in de TWN:\n {check["Twn_name"]}'
        )
        utility.stop_script()

    # replace empty values with Nan
    df["Hierarchie"].replace(r"^\s*$", np.nan, regex=True, inplace=True)

    # cleaning
    df.drop("Parent", axis=1, inplace=True)

    return df


@check_decorator.row_difference_decorator(0)
def split_combined_taxa(hierarchie: pd.DataFrame, split_rank: str) -> pd.DataFrame:
    """Splits the combined twn taxa and concatenates their full names to a new "combi" column.

    Args:
        twn (pd.DataFrame): a Pandas DataFrame with the twn data.
        split_rank (str): the taxonrank to split on combies.

    Returns:
        pd.DataFrame: a Pandas DataFrame wit the splitted taxa added to the combi column.
    """

    # filter taxa combies with "/" separated taxa names
    df = hierarchie[
        (hierarchie["Twn_name"].str.contains("/"))
        & (hierarchie["Taxonrank"] == split_rank)
    ].copy()

    # check if logic for requested combi rank is defined
    if split_rank not in ["SpeciesCombi", "GenusCombi"]:
        logger.warning(
            f"De opgegeven taxonrank kan niet worden gesplitst: logica voor {split_rank} is niet gedefinieerd."
        )
        return hierarchie

    # split twn combis to parts
    if split_rank == "GenusCombi":
        df["Combi_update"] = df["Twn_name"].str.replace("/", "|")

    if split_rank == "SpeciesCombi":
        df["Space"] = df["Twn_name"].str.find(" ")
        df["Genusname"] = df.apply(lambda x: x["Twn_name"][0 : x["Space"]], axis=1)
        df["Combi_update"] = df.apply(
            lambda row: row["Twn_name"].replace("/", f'|{row["Genusname"]} '), axis=1
        )

    # cleaning
    df["Combi_update"] = df["Combi_update"].str.replace(r"\|nan", "", regex=True)
    taxacombi = df[["Twn_name", "Combi_update"]].copy()

    # update hierarchie
    if "Combi" not in hierarchie:
        hierarchie["Combi"] = np.nan
    hierarchie[["Combi"]] = hierarchie[["Combi"]].astype(object)

    hierarchie = hierarchie.merge(taxacombi, on="Twn_name", how="left")
    hierarchie.loc[~hierarchie["Combi_update"].isna(), "Combi"] = hierarchie.loc[
        ~hierarchie["Combi_update"].isna(), "Combi_update"
    ]

    # cleaning
    hierarchie.drop("Combi_update", axis=1, inplace=True)

    return hierarchie


def main_taxa_mapping(twn_corrected: pd.DataFrame) -> pd.DataFrame:
    """Creates the taxonomy and hierarchy.

    Args:
        twn_corrected (pd.DataFrame): the corrected TWN data.

    Returns:
        pd.DataFrame: taxa mapping added to the taxa data.
    """
    valid_twn = process_twn.filter_valid_twn(twn_corrected)

    # taxa mappings
    taxonomy = create_taxonomy(valid_twn)
    df_taxa_map = recode_subspecies(valid_twn, taxonomy)
    df_taxa_map = glue_hierarchie(df_taxa_map, taxonomy)
    df_taxa_map = split_combined_taxa(df_taxa_map, "SpeciesCombi")
    df_taxa_map = split_combined_taxa(df_taxa_map, "GenusCombi")

    return df_taxa_map
