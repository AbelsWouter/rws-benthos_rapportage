"""Tests for processing the TWN."""

import os

import numpy as np
import pandas as pd
import pytest


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))

from preparation import process_twn


def test_download_twn() -> None:
    """Tests whether the downloaded TWN is a pandas DataFrame."""
    result = process_twn.download_twn(True)
    assert isinstance(result, pd.DataFrame)


def test_correct_twn(twn: pd.DataFrame) -> None:
    """Tests whether the result of correcting TWN has all the data.

    Args:
        twn (pd.DataFrame): Fixture with a DataFrame containing taxonomic data.

    """
    result = process_twn.correct_twn(twn)
    assert isinstance(result, pd.DataFrame)
    assert (
        result[["Name", "Taxontype", "Taxongroup_code", "Taxonrank", "Statuscode"]]
        .isnull()
        .sum()
        .sum()
        == 0
    )


def test_correct_twn_duplicates(twn: pd.DataFrame) -> None:
    """Tests for duplicate TWN taxa.

    Args:
        twn (pd.DataFrame): Fixture with a DataFrame containing taxonomic data.
    """
    # add twn to twn to create duplicates
    twn = pd.concat([twn, twn], ignore_index=True)
    result = process_twn.correct_twn(twn)

    assert isinstance(result, pd.DataFrame)
    assert (
        result[["Name", "Taxontype", "Taxongroup_code", "Taxonrank", "Statuscode"]]
        .isnull()
        .sum()
        .sum()
        == 0
    )


def test_check_twn(twn: pd.DataFrame) -> None:
    """Tests the checks on the TWN (missing groups, parents and synonymnames).

    Args:
        twn (pd.DataFrame): Fixture with a DataFrame containing taxonomic data.
    """
    valid_twn = twn[twn["Taxongroup_code"].notnull()]
    result = process_twn.check_twn(valid_twn)
    assert result is True

    # test missing taxongroup
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        process_twn.check_twn(twn)
        assert pytest_wrapped_e.type == SystemExit

    # test missing parent
    invalid_data = [
        {
            "Name": "Abietinaria",
            "Taxontype": "MACEV",
            "Taxongroup_code": "BRYHP",
            "Taxonrank": "Genus",
            "Parentname": np.nan,
            "Statuscode": 10,
            "Synonymname": np.nan,
        }
    ]
    df = pd.DataFrame(invalid_data, index=[0])
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        process_twn.check_twn(df)
        assert pytest_wrapped_e.type == SystemExit

    # test missing synonymname with invalid statuscode
    invalid_data = [
        {
            "Name": "Abietinaria",
            "Taxontype": "MACEV",
            "Taxongroup_code": "BRYHP",
            "Taxonrank": "Genus",
            "Parentname": "Sertulidae",
            "Statuscode": 20,
            "Synonymname": np.nan,
        }
    ]
    df = pd.DataFrame(invalid_data)
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        process_twn.check_twn(df)
        assert pytest_wrapped_e.type == SystemExit


def test_filter_valid_twn(twn: pd.DataFrame) -> None:
    """Tests the filtering of valid TWN taxa.

    Args:
        twn (pd.DataFrame): Fixture with a DataFrame containing taxonomic data.
    """
    # make sure invalid taxa in data
    assert len(twn[(~twn["Statuscode"].isin([10, 80]))].index) > 0
    result = process_twn.filter_valid_twn(twn)
    assert isinstance(result, pd.DataFrame)
    assert len(result[(~result["Statuscode"].isin([10, 80]))].index) == 0


def test_select_twn_mapping_columns(twn: pd.DataFrame) -> None:
    """Tests the selection of TWN mapping columns.

    Args:
        twn (pd.DataFrame): Fixture with a DataFrame containing taxonomic data.
    """
    result = process_twn.select_twn_mapping_columns(twn)
    assert isinstance(result, pd.DataFrame)
    assert result.columns.tolist() == ["Name", "Parentname", "Statuscode"]


def test_filter_usefull_twn(twn: pd.DataFrame) -> None:
    """Tests whether there is only valid TWN data.

    Args:
        twn (pd.DataFrame): Fixture with a DataFrame containing taxonomic data.
    """
    # make sure invalid taxa in data usefull_twn
    assert len(twn[(twn["Statuscode"].isin([20, 30]))].index) > 0
    result = process_twn.filter_usefull_twn(twn)
    assert (
        len(
            result[
                (~result["Statuscode"].isin([10, 80])) & (result["Synonymname"].isna())
            ].index
        )
        == 0
    )


def test_integration_main_twn(
    mocker: pd.DataFrame, twn: pd.DataFrame, twn_corrected: pd.DataFrame
) -> None:
    """Tests the integration of the TWN process.

    Args:
        mocker (pd.DataFrame): Makes sure the fixture TWN is the result of the download_twn function.
        twn (pd.DataFrame): Fixture with a DataFrame containing taxonomic data.
        twn_corrected (pd.DataFrame): Fixture with the output of the processed TWN.
    """
    mocker.patch("preparation.process_twn.download_twn", return_value=twn)

    result = process_twn.main_twn()
    pd.testing.assert_frame_equal(result, twn_corrected)


def test_get_twn_validity(twn_corrected: pd.DataFrame) -> None:
    """Tests whether the checks whether there are synonymnames or invalid names.

    Args:
        twn_corrected (pd.DataFrame): Fixture with the output of the processed TWN.
    """
    df_input = pd.DataFrame(
        {
            "Analyse_taxonnaam": [
                "Soort 1",
                "Campanulina johnstoni",
                "Acentria nivea",
                "Annelida",
            ]
        }
    )
    df_output = pd.DataFrame(
        {
            "Analyse_taxonnaam": [
                "Soort 1",
                "Campanulina johnstoni",
                "Acentria nivea",
                "Annelida",
            ],
            "Status": ["unknown", "invalid", "synonym", "valid"],
            "Synonymname": [np.nan, np.nan, "Acentria ephemerella", np.nan],
        }
    )
    result = process_twn.get_twn_validity(twn_corrected, df_input)
    pd.testing.assert_frame_equal(result, df_output)
