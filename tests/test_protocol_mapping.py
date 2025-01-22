"""Tests the protocol mapping of the twn."""

import os

import pandas as pd


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))

from preparation import protocol_mapping


def test_build_twn_tree(twn: pd.DataFrame) -> None:
    """Tests building the twn tree.

    Args:
        twn (pd.DataFrame): the input for the building twn tree function.
    """
    result = protocol_mapping.build_twn_tree(twn)
    assert isinstance(result, pd.DataFrame)
    assert set(sorted(["Name", "Parentname"])).issubset(sorted(result.columns))


def test_get_parents() -> None:
    """Tests getting the parents of the taxa."""
    result = protocol_mapping.get_parents(
        action="Presence", analysis="Determinatie", protocol="Zoet"
    )
    assert result == ["Bryozoa", "Hydrozoa", "Porifera"]


def test_uniform_determination_mapping_zoet(mapping_twn: pd.DataFrame) -> None:
    """Tests recoding the twn taxa to required, current, determination level for fresh water.

    Args:
        mapping_twn (pd.DataFrame): the twn mapping data.
    """
    result = protocol_mapping.uniform_determination_mapping(mapping_twn, "Zoet")
    assert isinstance(result, pd.DataFrame)
    assert {"Zoetoverrule_taxonname"}.issubset(result.columns)


def test_uniform_determination_mapping_zout(mapping_twn: pd.DataFrame) -> None:
    """Tests recoding the twn taxa to required, current, determination level for salt water.

    Args:
        mapping_twn (pd.DataFrame): the twn mapping data.
    """
    result = protocol_mapping.uniform_determination_mapping(mapping_twn, "Zout")
    assert isinstance(result, pd.DataFrame)
    assert {"Zoutoverrule_taxonname"}.issubset(result.columns)


def test_presence_mapping(mapping_twn: pd.DataFrame) -> None:
    """Tests the presence of the mapping.

    Args:
        mapping_twn (pd.DataFrame): the twn mapping data.
    """
    result = protocol_mapping.presence_mapping(mapping_twn, "Zoet")
    assert isinstance(result, pd.DataFrame)
    assert len(result[result["Zoetprotocol_presentie"].isna()]) == 0


def test_biomassa_exlude_mapping(mapping_twn: pd.DataFrame) -> None:
    """Tests the exclusion of biomass from the mapping.

    Args:
        mapping_twn (pd.DataFrame): the twn mapping data.
    """
    result = protocol_mapping.biomassa_exlude_mapping(mapping_twn)
    assert isinstance(result, pd.DataFrame)
    assert len(result[result["Zoutprotocol_biomassa"].isna()]) == 0


def test_integration_protocol_mapping(
    twn_corrected: pd.DataFrame, output_integration_protocol_mapping: pd.DataFrame
) -> None:
    """Tests the integration of the protocol mapping script.

    Args:
        twn_corrected (pd.DataFrame): the corrected twn data.
        output_integration_protocol_mapping (pd.DataFrame): the output of the integration function.
    """
    result = protocol_mapping.main_protocol_mapping(twn_corrected)
    ## AWARE: only works if hierarchie.yaml remaines unchanged
    pd.testing.assert_frame_equal(result, output_integration_protocol_mapping)
