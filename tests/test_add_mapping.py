"""Tests for adding the mapping to the twn."""

import pandas as pd
import pytest

from preparation import add_mapping


def test_add_valid_taxonnames(
    input_add_valid_taxonnames: pd.DataFrame,
    usefull_twn: pd.DataFrame,
    input_add_protocol: pd.DataFrame,
) -> None:
    """Tests the adding of valid taxonnames.

    Args:
        input_add_valid_taxonnames (pd.DataFrame): Fixture that loads the 'input_add_vaild_taxonnames.csv' file.
        usefull_twn (_type_): Fixture that filters the 'twn_corrected' DataFrame based on specific conditions.
        input_add_protocol (pd.DataFrame): Fixture that loads the 'input_add_protocol.csv' file.
    """

    result = add_mapping.add_valid_taxonnames(input_add_valid_taxonnames, usefull_twn)
    pd.testing.assert_frame_equal(result, input_add_protocol)


def test_add_valid_names_invalid_names(usefull_twn: pd.DataFrame) -> None:
    """Tests whether the function of adding valid taxonnames returns an error when names are invalid.

    Args:
        usefull_twn (pd.DataFrame): Fixture that filters the 'twn_corrected' DataFrame based on specific conditions.
    """
    df_invalid = pd.DataFrame(
        {
            "Parameter_Specificatie": ["Invalid name"],
            "Determinatie_protocol": ["any"],
            "Biomassa_protocol": ["any"],
        }
    )
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_mapping.add_valid_taxonnames(df_invalid, usefull_twn)
        assert pytest_wrapped_e.type == SystemExit


def test_add_valid_names_invalid_twn_columns(usefull_twn: pd.DataFrame) -> None:
    """Tests whether the function gives an error based on invalid twn columns.

    Args:
        usefull_twn (pd.DataFrame): Fixture that filters the 'twn_corrected' DataFrame based on specific conditions.
    """
    df_invalid = pd.DataFrame(
        {
            "Parameters_Specificatie": ["Abietinaria"],
            "Determinatie_protocol": ["any"],
            "Biomassa_protocol": ["any"],
        }
    )
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_mapping.add_valid_taxonnames(df_invalid, usefull_twn)
        assert pytest_wrapped_e.type == SystemExit


def test_add_valid_names_invalid_df_columns(
    input_add_valid_taxonnames: pd.DataFrame,
) -> None:
    """Tests whether invalid dataframe columns give an error.

    Args:
        input_add_valid_taxonnames (pd.DataFrame): Fixture that loads the 'input_add_vaild_taxonnames.csv' file.
    """
    invalid_twn = pd.DataFrame({"Name": ["Abietinaria"]})
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_mapping.add_valid_taxonnames(input_add_valid_taxonnames, invalid_twn)
        assert pytest_wrapped_e.type == SystemExit


def test_add_protocol_mapping(
    input_add_protocol: pd.DataFrame,
    output_integration_protocol_mapping: pd.DataFrame,
    input_add_taxa: pd.DataFrame,
) -> None:
    """Tests adding the protocol mapping of TWN to the aquadesk data.

    Args:
        input_add_protocol (pd.DataFrame): Fixture that loads the 'input_add_protocol.csv' file.
        output_integration_protocol_mapping (pd.DataFrame): Fixture with 'output_integration_protocol_mapping.csv' file.
        input_add_taxa (pd.DataFrame): Fixture that loads the 'input_add_taxa.csv' file.
    """
    result = add_mapping.add_protocol_mapping(
        input_add_protocol, output_integration_protocol_mapping
    )
    pd.testing.assert_frame_equal(result, input_add_taxa)


def test_add_taxa_mapping(
    input_add_taxa: pd.DataFrame,
    output_integration_taxa_mapping: pd.DataFrame,
    input_add_twn: pd.DataFrame,
) -> None:
    """Tests adding the taxa mapping of TWN to the aquadesk data.

    Args:
        input_add_protocol (pd.DataFrame): Fixture that loads the 'input_add_protocol.csv' file.
        output_integration_protocol_mapping (pd.DataFrame): Fixture with 'output_integration_protocol_mapping.csv' file.
        input_add_taxa (pd.DataFrame): Fixture that loads the 'input_add_taxa.csv' file.
    """
    result = add_mapping.add_taxa_mapping(
        input_add_taxa, output_integration_taxa_mapping
    )
    pd.testing.assert_frame_equal(result, input_add_twn)


def test_add_taxa_mapping_invalid_hierarchie(
    input_add_taxa: pd.DataFrame, output_integration_taxa_mapping: pd.DataFrame
) -> None:
    """Tests adding the taxa mapping with invalid hierarchie giving an error.

    Args:
        input_add_taxa (pd.DataFrame): Fixture that loads the 'input_add_protocol.csv' file.
        output_integration_taxa_mapping (pd.DataFrame): Fixture of 'output_integration_taxa_mapping.csv' file.
    """
    input_taxa_mapping_invalid = output_integration_taxa_mapping.drop(
        output_integration_taxa_mapping.Twn_name.isin(["Oligochaeta", "Hydrozoa"]).index
    )
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_mapping.add_taxa_mapping(input_add_taxa, input_taxa_mapping_invalid)
        assert pytest_wrapped_e.type == SystemExit


def test_add_twn(
    input_add_twn: pd.DataFrame, usefull_twn: pd.DataFrame, output_add_twn: pd.DataFrame
) -> None:
    """Tests adding the twn to Aquadesk data mapped to protocol and taxa.

    Args:
        input_add_twn (pd.DataFrame): Fixture that loads the 'input_add_protocol.csv' file.
        usefull_twn (pd.DataFrame): Fixture that loads the 'usefull_twn.csv' file.
        output_add_twn (pd.DataFrame): Fixture that loads the 'output_add_twn.csv' file.
    """
    result = add_mapping.add_twn(input_add_twn, usefull_twn)
    pd.testing.assert_frame_equal(result, output_add_twn)


def test_add_twn_invalid_rank(
    input_add_twn: pd.DataFrame, usefull_twn: pd.DataFrame
) -> None:
    """Tests whether an error is raised when invalid rank is added to twn.

    Args:
        input_add_twn (pd.DataFrame): Fixture that loads the 'input_add_protocol.csv' file.
        usefull_twn (pd.DataFrame): Fixture that loads the 'usefull_twn.csv' file.
    """
    usefull_twn_rank = usefull_twn.copy()
    usefull_twn_rank.loc[
        usefull_twn_rank["Name"] == "Oligochaeta", "Taxonrank"
    ] = "Genus"
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_mapping.add_twn(input_add_twn, usefull_twn_rank)
        assert pytest_wrapped_e.type == SystemExit


def test_add_twn_invalid_group(
    input_add_twn: pd.DataFrame, usefull_twn: pd.DataFrame
) -> None:
    """Tests whether an error is raised when invalid group is added to twn.

    Args:
        input_add_twn (pd.DataFrame): Fixture that loads the 'input_add_protocol.csv' file.
        usefull_twn (pd.DataFrame): Fixture that loads the 'usefull_twn.csv' file.
    """
    useful_twn_group = usefull_twn.copy()
    useful_twn_group.loc[
        useful_twn_group["Name"] == "Oligochaeta", "Taxongroup_code"
    ] = pd.NA
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_mapping.add_twn(input_add_twn, useful_twn_group)
        assert pytest_wrapped_e.type == SystemExit


def test_add_taxon_groups(
    input_add_groups: pd.DataFrame, input_add_hierarchical_groups: pd.DataFrame
) -> None:
    """Tests reading the groups configuration yaml and merges to get the groups.

    Args:
        input_add_groups (pd.DataFrame): Fixture that loads the 'input_add_groups.csv' file.
        input_add_hierarchical_groups (pd.DataFrame): Fixture that loads the 'input_add_hierarchical_groups.csv' file.
    """
    result = add_mapping.add_taxon_groups(input_add_groups)
    pd.testing.assert_frame_equal(result, input_add_hierarchical_groups)


def test_add_taxon_groups_no_group(input_add_groups: pd.DataFrame) -> None:
    """Tests whether an error is raised when no groups are being added.

    Args:
        input_add_groups (pd.DataFrame): Fixture that loads the 'input_add_groups.csv' file.
    """
    invalid = input_add_groups.copy()
    invalid.loc[
        invalid["Analyse_taxonnaam"] == "Alboglossiphonia", "Taxongroup_code"
    ] = pd.NA
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_mapping.add_taxon_groups(invalid)
        assert pytest_wrapped_e.type == SystemExit


def test_add_hierarchical_groups(
    input_add_hierarchical_groups: pd.DataFrame,
    input_add_twn_hierarchical_groups: pd.DataFrame,
    output_add_hierarchical_groups: pd.DataFrame,
) -> None:
    """Tests whether adding the hierarchical groups results in the expected outcome.

    Args:
        input_add_hierarchical_groups (pd.DataFrame): Fixture that loads the 'input_add_hierarchical_groups.csv' file.
        input_add_twn_hierarchical_groups (pd.DataFrame): Fixture with the 'input_add_twn_hierarchical_groups.csv' file.
        output_add_hierarchical_groups (pd.DataFrame): Fixture that loads the 'output_add_hierarchical_groups.csv' file.
    """
    result = add_mapping.add_hierarchical_groups(
        input_add_hierarchical_groups, input_add_twn_hierarchical_groups
    )
    pd.testing.assert_frame_equal(result, output_add_hierarchical_groups)


def test_add_hierarchical_groups_no_trendgroup(twn_corrected: pd.DataFrame) -> None:
    """Tests adding the hierarchical groups without trendgroups in the input.

    Args:
        twn_corrected (pd.DataFrame): Fixture with the corrected TWN data.
    """
    invalid_data = pd.DataFrame({"Trendgroep": [pd.NA]})
    result = add_mapping.add_hierarchical_groups(invalid_data, twn_corrected)
    pd.testing.assert_frame_equal(result, invalid_data)


def test_add_hierarchical_groups_no_unique_group(
    input_add_hierarchical_groups: pd.DataFrame, twn_corrected: pd.DataFrame
) -> None:
    """Tests adding the hierarchical groups without unique groups in the input.

    Args:
        input_add_hierarchical_groups (pd.DataFrame): Fixture that loads the 'input_add_hierarchical_groups.csv' file.
        twn_corrected (pd.DataFrame): Fixture with the corrected TWN data.
    """
    data = input_add_hierarchical_groups.copy()
    invalid_row = ["Porifera", "BRHYP", "zoet", "Zoet", "Oligochaeta"]
    data.loc[len(data)] = invalid_row
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_mapping.add_hierarchical_groups(data, twn_corrected)
        assert pytest_wrapped_e.type == SystemExit


def test_integration_main_add_mapping(
    input_integration_add_mapping: pd.DataFrame,
    twn_corrected: pd.DataFrame,
    output_integration_protocol_mapping: pd.DataFrame,
    output_integration_taxa_mapping: pd.DataFrame,
    output_integration_add_mapping: pd.DataFrame,
) -> None:
    """Tests the integration of the add mapping functions.

    Args:
        input_integration_add_mapping (pd.DataFrame): Fixture with the input of the integration add mapping.
        twn_corrected (pd.DataFrame): Fixture with the corrected TWN data.
        output_integration_protocol_mapping (pd.DataFrame): Fixture with the expected output of the protocol mapping.
        output_integration_taxa_mapping (pd.DataFrame): Fixture with the expected output of the taxa mapping.
        output_integration_add_mapping (pd.DataFrame): Fixture with the expected output of the add mapping.
    """
    result = add_mapping.main_add_mapping(
        input_integration_add_mapping,
        twn_corrected,
        output_integration_protocol_mapping,
        output_integration_taxa_mapping,
    )
    pd.testing.assert_frame_equal(result, output_integration_add_mapping)


def test_check_mapped_df(output_integration_add_mapping: pd.DataFrame) -> None:
    """Tests checking Aquadesk dataframe on NA's after adding mapping and TWN.

    Args:
        output_integration_add_mapping (pd.DataFrame): Fixture with the expected output of the add mapping.
    """
    result = add_mapping.check_mapped_df(output_integration_add_mapping)
    assert result is True


def test_check_mapped_df_invalid() -> None:
    """Tests with invalid data whether the checking gives the right error."""
    invalid_data = {
        "Collectie_Referentie": [1],
        "Parameter_Specificatie": ["soort"],
        "Determinatie_protocol": ["zoet"],
        "Order": [1],
        "Analyse_taxonnaam": ["soort"],
        "IsPresentie_Protocol": [True],
        "IsBiomassa_Protocol": [True],
        "Statuscode": [10],
        "Taxontype": [None],
        "Taxongroup_code": ["REMAIN"],
        "Taxonrank": ["Genus"],
    }
    df = pd.DataFrame(invalid_data)

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        add_mapping.check_mapped_df(df)
        assert pytest_wrapped_e.type == SystemExit
