"""Data will be checked and written conform the TWN."""

"""
# File: add_mappings.py
# Author(s): M. Japink (m.japink@waardenburg.eco) & J. Haringa (j.haringa@waardenburg.eco)
# Creation date: 20-09-2023
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
from preparation import protocol_mapping
from preparation import read_system_config
from preparation import utility


logger = logging.getLogger(__name__)


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def add_valid_taxonnames(df: pd.DataFrame, usefull_twn: pd.DataFrame) -> pd.DataFrame:
    """Adds valid TWN names to the aquadesk data.

    Args:
        df (pd.DataFrame): Aquadesk data with at least the following columns: Parameter_Specificatie.
        usefull_twn (pd.DataFrame): TWN with at least the following colums: Name, Synonym.

    Returns:
        pd.DataFrame: input df plus a column with valid synonyms.
    """

    # check required columns
    check = set(["Name", "Synonymname"]).issubset(usefull_twn.columns)
    if not check:
        logger.critical("De TWN voldoet mist de kolommen: 'Name','Synonymname'.")
        utility.stop_script()

    check = set(["Parameter_Specificatie"]).issubset(df.columns)
    if not check:
        logger.critical("De Aquadesk data mist de kolom: 'Parameter_Specificatie'.")
        utility.stop_script()

    # from usefull twn drop all columns but name and synonymname
    twn_mapping = usefull_twn[["Name", "Synonymname"]].copy()

    # fill out synonymname column with all valid names
    twn_mapping["Synonymname"] = twn_mapping.apply(
        lambda row: utility.coalesce(row["Synonymname"], row["Name"]), axis=1
    )

    # add valid names to the aquadesk data
    df = df.merge(
        twn_mapping,
        left_on="Parameter_Specificatie",
        right_on="Name",
        how="left",
        suffixes=("", "_DROP"),
    ).filter(regex="^(?!.*_DROP)")
    df.drop(columns="Name", inplace=True)
    # check all names are mapped to synonym
    check_names = df[df["Synonymname"].isna()]
    if len(check_names) > 0:
        logger.error(
            f'De Aquadeskdata bevat de volgende ongeldige taxa: \n {check_names["Parameter_Specificatie"].unique()}'
        )
        utility.stop_script()

    return df


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def add_protocol_mapping(
    df: pd.DataFrame, df_protocol_mapping: pd.DataFrame
) -> pd.DataFrame:
    """Adds the protocol mapping to the aquadesk data.

    Args:
        df (pd.DataFrame): Aquadesk data with at least the following columns:
        df_protocol_mapping (pd.DataFrame): dataframe with the protocol mapping.

    Returns:
        pd.DataFrame: input df plus a column with protocol mapping.
    """

    # join protocol data to the aquadesk data
    df = df.merge(
        df_protocol_mapping,
        left_on="Synonymname",
        right_on="Name",
        how="left",
    )

    # fill new column with mapped name based on zoet- or zoetprotocol
    df["Analyse_taxonnaam"] = df.apply(
        lambda row: (
            utility.coalesce(row["Zoetoverrule_taxonname"], row["Synonymname"], row)
            if row["Determinatie_protocol"] == "zoet"
            else utility.coalesce(
                row["Zoutoverrule_taxonname"], row["Synonymname"], row
            )
        ),
        axis=1,
    )

    # fill new column with presence or abundance discriminator
    df["IsPresentie_Protocol"] = np.where(
        df["Determinatie_protocol"] == "zout",
        df["Zoutprotocol_presentie"],
        df["Zoetprotocol_presentie"],
    )

    # fill new column with biomass discrimator
    df["IsBiomassa_Protocol"] = np.where(
        df["Biomassa_protocol"] == "zout",
        df["Zoutprotocol_biomassa"],
        False,
    )

    # cleaning
    df.drop(
        columns=["Parentname", "Name", "Statuscode"],
        inplace=True,
    )

    # checks
    check = df[df["Analyse_taxonnaam"].isna()]
    if len(check > 0):
        logger.critical(
            "Join tussen Aquadeskdata en protocol mapping gaat fout voor de volgende soorten:\n "
            f"{check['Analyse_taxonnaam'].unique()}"
        )
        utility.stop_script()

    check = df[df["IsPresentie_Protocol"].isna()]
    if len(check > 0):
        logger.critical(
            "Join tussen Aquadeskdata en protocol mapping gaat fout voor de volgende soorten:\n"
            f"{check['Analyse_taxonnaam'].unique()}"
        )
        utility.stop_script()

    check = df[df["IsBiomassa_Protocol"].isna()]
    if len(check > 0):
        logger.critical(
            "Join tussen Aquadeskdata en protocol mapping gaat fout voor de volgende soorten:\n"
            f"{check['Analyse_taxonnaam'].unique()}"
        )
        utility.stop_script()

    return df


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def add_taxa_mapping(df: pd.DataFrame, df_taxa_mapping: pd.DataFrame) -> pd.DataFrame:
    """Adds the taxa mapping to the aquadesk data

    Args:
        df (pd.DataFrame): Aquadesk data with at least the following columns:
        df_protocol_mapping (pd.DataFrame): dataframe with the taxa mapping

    Returns:
        pd.DataFrame: input df plus a column with taxa mapping
    """

    # join taxa data to the aquadesk data
    df = df.merge(
        df_taxa_mapping,
        left_on="Analyse_taxonnaam",
        right_on="Twn_name",
        how="left",
    )

    # drop all twn_name and name equal to each other
    df.loc[df["Twn_name"] == df["Name"], ["Twn_name", "Name"]] = np.nan

    # overrule analyse taxonnames with
    SEL = df["Analyse_taxonnaam"] == df["Twn_name"]
    df.loc[SEL, "Analyse_taxonnaam"] = df.loc[SEL, "Name"]

    # cleaning
    df.rename(columns={"Name": "Overrule_subspeciesname"}, inplace=True)
    df.drop(columns=["Twn_name"], inplace=True)

    # checks
    check = df[(df["Hierarchie"].isna()) & (df["Synonymname"] != "Animalia")]
    if len(check) != 0:
        logger.error(
            f'De volgende taxa hebben geen Hierarchie:\n {check["Synonymname"].unique()}'
        )
        utility.stop_script()

    check = df[df["Analyse_taxonnaam"].isna()]
    if len(check) != 0:
        logger.error(
            f'De volgende taxa hebben geen Analyse taxonnaam:\n {check["Synonymname"].unique()}'
        )
        utility.stop_script()

    check = df[["Analyse_taxonnaam", "Taxonrank", "Order"]].drop_duplicates()
    check = check.groupby("Analyse_taxonnaam").size().reset_index(name="n")
    check = check[check["n"] > 1]
    if len(check) > 0:
        logger.error(
            f'Verschillen in toekenning van taxonranks voor de volgende taxa:\n {check["Analyse taxonnaam"].unique()}'
        )
        utility.stop_script()

    return df


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def add_twn(df: pd.DataFrame, twn: pd.DataFrame) -> pd.DataFrame:
    """Adds TWN info to the mapped aquadesk data

    Args:
        df (pd.DataFrame): Aquadesk data mapped to protocol and taxa.
        df_protocol_mapping (pd.DataFrame): TWN

    Returns:
        pd.DataFrame: input df plus a column with taxa mapping
    """

    # preparation
    twn = twn.drop(columns="Synonymname")
    twn.rename(columns={"Taxonrank": "Taxonrank_check"}, inplace=True)

    # join twn to the aquadesk data
    df = df.merge(
        twn,
        left_on="Analyse_taxonnaam",
        right_on="Name",
        how="left",
    )

    # checks
    check = df[df["Taxonrank"] != df["Taxonrank_check"]]
    if len(check) > 0:
        logger.error(
            f"Verschil in het toekennen van de taxonranks voor de volgende taxa:\n"
            f'{check["Analyse_taxonnaam"].unique()}'
        )
        utility.stop_script()

    check = df[df["Taxongroup_code"].isna()]
    if len(check) > 0:
        logger.error(
            f'Niet alle taxa hebben een taxongroup_code toegewezen gekregen:\n {check["Analyse_taxonnaam"].unique()}'
        )
        utility.stop_script()

    # cleaning
    df.drop(
        columns=["Name", "Taxonrank_check", "Parentname", "Synonymname"], inplace=True
    )

    return df


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def add_taxon_groups(df: pd.DataFrame) -> pd.DataFrame:
    """Reads the groups configuration yaml and merges to get the groups.

    Args:
        df (pd.DataFrame): dataframe with the input data.

    Returns:
        pd.DataFrame: dataframe with the merged group ('groep') column.
    """

    groups = read_system_config.read_csv_file(
        read_system_config.read_yaml_configuration(
            "config_taxon_groups", "global_variables.yaml"
        )
    )

    # Remove column Groepkleur and filter on non-hierarchical groups
    # both are handled in subseding functionality.
    groups = groups.drop(columns=["Groepkleur"])
    groups = groups[groups["Hierarchisch"].isna()]

    df = df.merge(
        groups[["Taxongroup_code", "Trendgroep", "Groep"]],
        on=["Taxongroup_code", "Trendgroep"],
        how="left",
    )

    # check
    check = df[df["Groep"].isna()]
    if len(check) > 0:
        logger.error(
            f'Voor de volgende taxa is de groepsindeling onbekend: \n {check["Analyse_taxonnaam"].unique()}'
        )
        utility.stop_script()
    return df


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def add_hierarchical_groups(
    df: pd.DataFrame, twn_corrected: pd.DataFrame
) -> pd.DataFrame:
    """Calculates the hierarchich group taxa and updates the aquadesk accordingly.

    Args:
        df (pd.DataFrame): dataframe with the input data.
        twn_valid: the valid twn

    Returns:
        pd.DataFrame: dataframe with the merged group ('groep') column.
    """

    groups = read_system_config.read_csv_file(
        read_system_config.read_yaml_configuration(
            "config_taxon_groups", "global_variables.yaml"
        )
    )

    # filter valid twn
    twn_valid = process_twn.filter_valid_twn(twn_corrected)

    # filter parents from groupsconfiguration for used groups
    trendgroep = df["Trendgroep"].unique().tolist()
    if len(trendgroep) == 0:
        return df

    df_hierarchical = groups[
        (groups["Trendgroep"].isin(trendgroep)) & (~groups["Hierarchisch"].isna())
    ][["Trendgroep", "Taxongroup_code", "Groep", "Hierarchisch"]]
    group_parent = df_hierarchical["Hierarchisch"].unique().tolist()
    if len(group_parent) == 0:
        return df

    # build hierarchy from relevant parents
    hierarchie = protocol_mapping.build_taxon_hierarchie(group_parent, twn_valid)
    hierarchie.rename(columns=({"Overrule_taxonname": "Hierarchisch"}), inplace=True)

    # merge hierarchy to groups configuration
    df_hierarchical = df_hierarchical.merge(hierarchie, on="Hierarchisch", how="left")
    df_hierarchical.drop(columns=("Hierarchisch"), inplace=True)
    df_hierarchical.rename(
        columns=({"Groep": "Groep_update", "Name": "Analyse_taxonnaam"}), inplace=True
    )

    # hierarchical groups to data en update data
    df = df.merge(
        df_hierarchical,
        on=["Trendgroep", "Taxongroup_code", "Analyse_taxonnaam"],
        how="left",
    )
    df["Groep"] = df.apply(
        lambda row: utility.coalesce(row["Groep_update"], row["Groep"]), axis=1
    )

    # clean
    df.drop(columns=("Groep_update"), inplace=True)

    # check
    check = df[df["Groep"].isna()]
    if len(check) > 0:
        logger.error(
            f'Voor de volgende taxa is de groepsindeling onbekend: \n {check["Analyse_taxonnaam"].unique()}'
        )
        utility.stop_script()

    check = (
        df[["Groep", "Analyse_taxonnaam", "Waterlichaam"]]
        .drop_duplicates()
        .groupby(["Waterlichaam", "Analyse_taxonnaam"])
        .size()
        .reset_index(name="count")
    )
    check = check[check["count"] != 1]
    if len(check) > 0:
        logger.error(
            f"De volgende taxa hebben meerdere groepsindelingen gekregen.\n {check}"
        )
        utility.stop_script()
    return df


@log_decorator.log_factory(__name__)
def check_mapped_df(df: pd.DataFrame) -> bool:
    """Checks Aquadesk dataframe on NA's after adding mapping and TWN.

    Args:
        df (pd.DataFrame): dataframe with Aquadesk data enriched with mapping and TWN

    Returns:
        bool: whether all the checks pass or not.
    """
    valid_data = True

    non_na_columns = [
        "Collectie_Referentie",
        "Parameter_Specificatie",
        "Determinatie_protocol",
        "Order",
        "Analyse_taxonnaam",
        "IsPresentie_Protocol",
        "IsBiomassa_Protocol",
        "Statuscode",
        "Taxontype",
        "Taxongroup_code",
        "Taxonrank",
    ]
    for columnname in non_na_columns:
        check = df[df[columnname].isna()]
        if len(check) > 0:
            logger.error(
                f"""De {columnname} heeft {len(check)} lege velden na het toekennen van \
                    mapping- en TWN-gegevens aan de Aquadesk data. 
                    Het gaat om de volgende soorten: \n{check['Parameter_Specificatie'].unique()}"""
            )

            valid_data = False

    if not valid_data:
        utility.stop_script()

    return True


def main_add_mapping(
    df: pd.DataFrame,
    twn_corrected: pd.DataFrame,
    protocol_map: pd.DataFrame,
    taxa_map: pd.DataFrame,
) -> pd.DataFrame:
    """Integrates all the add mapping functions.

    Args:
        df (pd.DataFrame): dataframe with the taxa data.
        twn_corrected (pd.DataFrame): the corrected TWN.
        protocol_map (pd.DataFrame): the protocol added to the TWN.
        taxa_map (pd.DataFrame): the taxa added to the TWN.

    Returns:
        pd.DataFrame: dataframe with the added mapping.
    """
    twn_usefull = process_twn.filter_usefull_twn(twn_corrected)
    df = add_valid_taxonnames(df, twn_usefull)
    df = add_protocol_mapping(df, protocol_map)
    df = add_taxa_mapping(df, taxa_map)
    df = add_twn(df, twn_usefull)
    df = add_taxon_groups(df)
    df = add_hierarchical_groups(df, twn_corrected)
    check_mapped_df(df)

    return df
