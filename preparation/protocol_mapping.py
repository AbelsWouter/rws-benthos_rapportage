"""Protocol mapping: 
\n - All valid twn-taxa are mapped to the requested determination levels.
\n - All valid twn-taxa are marked for abundance vs precence and whether or not an biomassa determination
"""

"""
# File: twn.py
# Author(s): M. Japink (m.japink@waardenburg.eco) & J. Haringa (j.haringa@waardenburg.eco)
# Creation date: 5-07-2023
# Last modification: 20-02-2024
# Python v3.12.1
"""

import logging
import os
import typing

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
def uniform_determination_mapping(twn: pd.DataFrame, protocol: str) -> pd.DataFrame:
    """Recodes the twn taxa to required, current, determination level.

    Args:
        twn (pd.DataFrame): a Pandas DataFrame with the twn data.
        protocol (str): determination protocol for fresh water (zoet) or salt water (zout).

    Returns:
        pd.DataFrame: a Pandas DataFrame with the recoded twn.
    """
    parent_recode = get_parents(
        action="Aggregate", analysis="Determinatie", protocol=protocol
    )
    parent_contra = get_parents(
        action="Aggregate", analysis="Determinatie", protocol=protocol, iscontra=True
    )
    recode = build_taxon_hierarchie(parent_recode, twn)
    contra = build_taxon_hierarchie(parent_contra, twn, iscontra=True)
    recode = recode.merge(contra, on="Name", how="left")

    recode[protocol + "overrule_taxonname"] = recode.apply(
        lambda row: utility.coalesce(
            row["Contra_taxonname"], row["Overrule_taxonname"]
        ),
        axis=1,
    )

    recode = recode.drop(columns=["Overrule_taxonname", "Contra_taxonname"])

    mapping = twn.merge(recode, on="Name", how="left")

    return mapping


@log_decorator.log_factory(__name__)
def get_parents(
    action: str, analysis: str, protocol: str, iscontra: typing.Optional[bool] = False
) -> typing.Any:
    """Reads the configuration file with the twn hierarchy.

    Args:
        analysis (str): the analysis method (determination or biomassa)
        protocol (str): the protocol (zoet of zout)
        iscontra (typing.Optional[bool], optional): whether the taxa need to be
        aggregated or not. Defaults to False.

    Returns:
        typing.Any: the value from the configuration hierarchy.yaml.
    """

    # based on the contra variable read the parents from the yaml configuration file.
    if iscontra:
        x = action + "-contra"
    else:
        x = action
    parents = read_system_config.read_yaml_configuration(
        analysis + "." + protocol + "." + x, "hierarchy.yaml"
    )

    return parents


@log_decorator.log_factory(__name__)
def build_taxon_hierarchie(
    parents: typing.Any, twn: pd.DataFrame, iscontra: typing.Optional[bool] = False
) -> pd.DataFrame:
    """Builds the twn taxon hierarchy if there are parents.

    Args:
        parents (typing.Any): a list of parents (or none if there are no parents).
        twn (pd.DataFrame): a Pandas DataFrame
        iscontra (typing.Optional[bool], optional):  whether the taxa need to be
        aggregated or not. Defaults to False.

    Returns:
        pd.DataFrame: a Pandas DataFrame with the twn hierarchy.
    """

    # guard: if no parents then return an empty dataframe
    if parents is None:
        if iscontra:
            df = pd.DataFrame({"Contra_taxonname": [""], "Name": [""]})
        else:
            df = pd.DataFrame({"Overrule_taxonname": [""], "Name": [""]})
        return df

    taxon_hierarchie = pd.DataFrame()
    twn_tree = build_twn_tree(twn)
    for parent in parents:
        result = get_descendants(parent, twn_tree)
        if result is not None:
            if iscontra:
                result = pd.DataFrame({"Name": result, "Contra_taxonname": result})
            else:
                result = pd.DataFrame({"Name": result, "Overrule_taxonname": parent})
            taxon_hierarchie = pd.concat([taxon_hierarchie, result])

    taxon_hierarchie = append_parents(taxon_hierarchie, parents, iscontra)

    return taxon_hierarchie


@log_decorator.log_factory(__name__)
def build_twn_tree(twn: pd.DataFrame) -> pd.DataFrame:
    """Builds the twn tree by selecting all the parentnames and taxanames.

    Args:
        twn (pd.DataFrame): a Pandas DataFrame with the twn.

    Returns:
        pd.DataFrame: a Pandas DataFrame with the twn including parent- and taxanames.
    """
    twn_tree = twn.copy()
    twn_tree = twn_tree[["Name", "Parentname"]]
    twn_tree = twn_tree[~twn_tree["Name"].isna()]
    twn_tree = twn_tree[
        ~(twn_tree["Parentname"].isna() & ~twn_tree["Name"].isin(["Animalia"]))
    ]
    return twn_tree


@log_decorator.log_factory(__name__)
def get_descendants(
    name: str, tree: pd.DataFrame, descendants: typing.Optional[list] = []
) -> list:
    """Gets the descendents for all the children if there are children without a parent.

    Args:
        name (str): the parentname.
        tree (pd.DataFrame): the twn tree from the build_twn_tree function.
        descendants (typing.Optional[list], optional): the list of decendents
        need to be filled if there are no children for the parentname. Defaults to [].

    Returns:
        list: a list of descendants.
    """
    children = tree.loc[tree["Parentname"].isin([name]), "Name"]
    if len(children) == 0:
        return descendants

    descendants = descendants + children.tolist()
    for child in children:
        descendants = get_descendants(child, tree, descendants)
    return list(set(descendants))


@log_decorator.log_factory(__name__)
def append_parents(df: pd.DataFrame, parents: list, iscontra: bool) -> pd.DataFrame:
    """Appends the parents and taxonname depending on the contra argument.

    Args:
        df (pd.DataFrame): a Pandas DataFrame with the twn hierarchy.
        parents (list): a list of parents.
        iscontra (bool): whether the taxa is overruled or not.

    Returns:
        pd.DataFrame: a Pandas DataFrame with the parents of the taxa appended.
    """
    if iscontra:
        result = pd.DataFrame({"Name": parents, "Contra_taxonname": parents})
    else:
        result = pd.DataFrame({"Name": parents, "Overrule_taxonname": parents})
    df = pd.concat([result, df])
    return df


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def presence_mapping(twn: pd.DataFrame, protocol: str) -> pd.DataFrame:
    """Marks the taxa for presence only

    Args:
        twn (pd.DataFrame): a Pandas DataFrame with the twn data
        protocol (str): determination protocol for fresh water (zoet) as well as for salt water (zout)

    Returns:
        pd.DataFrame: a Pandas DataFrame with the marked twn taxa.
    """

    # read the configured parents
    presence_parent = get_parents(
        action="Presence", analysis="Determinatie", protocol=protocol
    )
    presence_parent_contra = get_parents(
        action="Presence", analysis="Determinatie", protocol=protocol, iscontra=True
    )

    # get all descendants for each parent
    precense = build_taxon_hierarchie(presence_parent, twn)
    presence_contra = build_taxon_hierarchie(presence_parent_contra, twn, iscontra=True)

    # exclude the contra descendants
    presence = precense.merge(presence_contra, on="Name", how="left")
    presence = presence[presence["Contra_taxonname"].isnull()]
    presence = presence.drop(columns=["Overrule_taxonname", "Contra_taxonname"])
    presence[protocol + "protocol_presentie"] = True

    # add presence mapping as column to the TWN
    mapping = twn.merge(presence, on="Name", how="left")

    # fill out column with boolean true
    mapping[protocol + "protocol_presentie"] = mapping.apply(
        lambda row: utility.coalesce(row[protocol + "protocol_presentie"], False),
        axis=1,
    )

    return mapping


@check_decorator.row_difference_decorator(0)
@log_decorator.log_factory(__name__)
def biomassa_exlude_mapping(twn: pd.DataFrame, protocol: str = "Zout") -> pd.DataFrame:
    """Marks the taxa which should be cremated or not

    Args:
        twn (pd.DataFrame): a Pandas DataFrame with the twn data
        protocol (str): biomass protocol is only determined for salt waterbodies

    Returns:
        pd.DataFrame: a Pandas DataFrame with the marked twn taxa.
    """

    # read the configured parents
    biomassa_exclude_parent = get_parents(
        action="Exclude", analysis="Biomassa", protocol=protocol
    )
    biomassa_exclude_parent_contra = get_parents(
        action="Exclude", analysis="Biomassa", protocol=protocol, iscontra=True
    )

    # get all descendants for each parent
    biomassa_exclude = build_taxon_hierarchie(biomassa_exclude_parent, twn)
    biomassa_exclude_contra = build_taxon_hierarchie(
        biomassa_exclude_parent_contra, twn, iscontra=True
    )

    # exclude the contra descendants
    biomassa_exclude = biomassa_exclude.merge(
        biomassa_exclude_contra, on="Name", how="left"
    )
    biomassa_exclude = biomassa_exclude[biomassa_exclude["Contra_taxonname"].isnull()]
    biomassa_exclude = biomassa_exclude.drop(
        columns=["Overrule_taxonname", "Contra_taxonname"]
    )
    biomassa_exclude[protocol + "protocol_biomassa"] = False

    # add biomass excude as column to the TWN
    mapping = twn.merge(biomassa_exclude, on="Name", how="left")

    # fill out column with boolean true
    mapping[protocol + "protocol_biomassa"] = mapping.apply(
        lambda row: utility.coalesce(row[protocol + "protocol_biomassa"], True), axis=1
    )

    return mapping


def main_protocol_mapping(twn_corrected: pd.DataFrame) -> pd.DataFrame:
    """Adds the various protocols and mappings to the twn.

    Args:
        twn_corrected (pd.DataFrame): the corrected TWN.

    Returns:
        pd.DataFrame: the TWN with the protocols added.
    """
    valid_twn = process_twn.filter_valid_twn(twn_corrected)

    # protocol mapping
    df_protocol_map = process_twn.select_twn_mapping_columns(valid_twn)

    df_protocol_map = uniform_determination_mapping(df_protocol_map, "Zoet")
    df_protocol_map = uniform_determination_mapping(df_protocol_map, "Zout")
    df_protocol_map = presence_mapping(df_protocol_map, "Zoet")
    df_protocol_map = presence_mapping(df_protocol_map, "Zout")
    df_protocol_map = biomassa_exlude_mapping(df_protocol_map, "Zout")

    return df_protocol_map
