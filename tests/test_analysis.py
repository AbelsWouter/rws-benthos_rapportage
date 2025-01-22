"""Tests the analysis of the benthos data."""

import logging
import os

import pandas as pd
from pytest import LogCaptureFixture
import pytest_mock

from analysis import analysis_tree
from tests import conftest


logger = logging.getLogger(__name__)


def test_analysis_tree_no_data(caplog: LogCaptureFixture) -> None:
    """Test the analysis tree with no data as input.

    Args:
        caplog (LogCaptureFixture): _description_
    """
    df_input = pd.DataFrame(
        {"Gebruik": ["overig"], "Waterlichaam": ["Rijn"], "Support_Eenheid": ["m2"]}
    )
    analysis_tree.analysis_tree(df_input, None, None)
    assert (
        "Er is voor het waterlichaam 'Rijn' geen trend data beschikbaar." in caplog.text
    )


def test_analysis_tree_path_without_seasons() -> None:
    """Tests the creation of the tree paths with data without season."""
    df_input = pd.DataFrame(
        {
            "Gebruik": ["trend"] * 4,
            "Waterlichaam": ["Rijn"] * 4,
            "Heeft_Seizoen": [False] * 4,
            "Monsterjaar": [2019, 2020, 2021, 2022],
            "Seizoen": ["najaar"] * 3 + ["voorjaar"],
            "Gebied": [pd.NA] * 4,
            "Strata": [pd.NA] * 4,
            "Ecotoop_Codes": [pd.NA] * 4,
            "Ecotoop_ZES1": [pd.NA] * 4,
            "Support_Eenheid": ["m2"] * 4,
        }
    )
    conftest.remove_folder("./output/Rijn/voorjaar")
    conftest.remove_folder("./output/Rijn/najaar")

    analysis_tree.analysis_tree(df_input, None, None)

    # check that only folder Rijn is created in ./output
    assert os.path.exists("./output/Rijn")
    assert not os.path.exists("./output/Rijn/voorjaar")
    assert not os.path.exists("./output/Rijn/najaar")

    conftest.remove_folder("./output/Rijn/voorjaar")
    conftest.remove_folder("./output/Rijn/najaar")


def test_analysis_tree_path_with_seasons() -> None:
    """Tests the creation of the tree paths with data with seasons."""
    df_input = pd.DataFrame(
        {
            "Gebruik": ["trend", "trend", "trend", "trend"],
            "Waterlichaam": ["Rijn"] * 4,
            "Heeft_Seizoen": [True] * 4,
            "Seizoen": ["najaar"] * 3 + ["voorjaar"],
            "Gebied": [pd.NA] * 4,
            "Strata": [pd.NA] * 4,
            "Ecotoop_Codes": [pd.NA] * 4,
            "Ecotoop_ZES1": [pd.NA] * 4,
            "Support_Eenheid": ["m2"] * 4,
        }
    )

    analysis_tree.analysis_tree(df_input, None, None)

    # check that seasonal childfolders are created in ./output/Rijn
    assert os.path.exists("./output/Rijn/voorjaar")
    assert os.path.exists("./output/Rijn/najaar")


def test_analysis_tree_path_with_areas() -> None:
    """Tests the analysis tree path with multiple diversity levels."""
    df_input = pd.DataFrame(
        {
            "Gebruik": ["trend", "trend", "trend", "trend"],
            "Waterlichaam": ["Rijn"] * 4,
            "Heeft_Seizoen": [False] * 4,
            "Seizoen": ["najaar"] * 3 + ["voorjaar"],
            "Gebied": ["gebied 1", "gebied 2", "gebied 3", "gebied 4"],
            "Strata": ["stratum 1", "stratum 2", "stratum 3", "stratum 4"],
            "Ecotoop_Codes": [pd.NA] * 4,
            "Ecotoop_ZES1": [pd.NA] * 4,
            "Support_Eenheid": ["m2"] * 4,
        }
    )
    analysis_tree.analysis_tree(df_input, None, None)

    # check that the area folders are created in ./output/Rijn
    assert os.path.exists("./output/Rijn/Gebied")
    assert os.path.exists("./output/Rijn/Strata")
    assert os.path.exists("./output/Rijn/Strata_Gebied")
    assert not os.path.exists("./output/Rijn/Ecotoop")
    assert not os.path.exists("./output/Rijn/Ecotoop_Codes_Gebied")


def test_analysis_main(
    input_analysis_main: pd.DataFrame,
    habitat_species: pd.DataFrame,
    mocker: pytest_mock.MockerFixture,
) -> None:
    """Tests the integration of the analysis benthos data script.

    Args:
        input_analysis_main (pd.DataFrame): the input benthos data for the analysis phase.
        habitat_species (pd.DataFrame): the HR-species from the configuration global_variables.yaml.
        mocker (pytest_mock.MockerFixture): the result of the check_habitat_n2000_species_conform_twn
    """
    mocker.patch(
        "checks.check_tables.check_habitat_n2000_species_conform_twn",
        return_value=habitat_species,
    )

    analysis_tree.analysis_main(input_analysis_main)

    assert os.path.exists("./output/Zandmaas/Gebied")
    assert os.path.exists("./output/Zandmaas/Zandmaas - Dichtheid_Aantal.png")
    assert os.path.exists("./output/Zandmaas/Zandmaas - Dichtheid_Massa.png")
    assert os.path.exists("./output/Zandmaas/Zandmaas - Shannon.png")
    assert os.path.exists("./output/Zandmaas/Zandmaas - Shannon_Monster.png")
    assert os.path.exists(
        "./output/Zandmaas/Gebied/Zandmaas - Dichtheid_Aantal - Gebied.png"
    )
    assert os.path.exists(
        "./output/Zandmaas/Gebied/Zandmaas - Dichtheid_Massa - Gebied.png"
    )
