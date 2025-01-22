"""Tests the user configuration functions."""

from typing import List

import pytest

from preparation import read_user_config


def test_read_txt_file() -> None:
    """Tests the type of reading the project configuration text file."""
    assert isinstance(
        read_user_config.read_txt_file("./input/selectie_project.txt"), str
    )


def test_parse_user_configuration() -> None:
    """Tests parsing through the user project configuration."""
    content = """### ### lijst van rws-projecten die het benthosscript kan verwerken.
### door het verwijderen van een hekje (#) kan een project actief gemaakt worden.
MWTL_MACEV
MWTL_MZB
MWTL_MZB_Schaaf
#MWTL_MZB_Boxcorer
#MWTL_MZB_Hamon
#MWTL_MZB_Video
"""
    result = read_user_config.parse_user_configuration(content)

    assert len(result) == len(set(result))
    assert set(result) == set(["MWTL_MACEV", "MWTL_MZB", "MWTL_MZB_Schaaf"])


def test_check_user_configuration() -> None:
    """Tests the selection of a project in the projects configuration."""
    project_list = ["Noordzee"]
    assert read_user_config.check_user_configuration(project_list, "projecten.txt") == [
        "Noordzee"
    ]


def test_check_user_configuration_Beneden_Maas() -> None:
    """Tests the selection of a project with a space in the projects configuration."""
    project_list = ["Beneden Maas"]
    assert read_user_config.check_user_configuration(project_list, "projecten.txt") == [
        "Beneden Maas"
    ]


def test_incomplete_user_configuration() -> None:
    """Tests whether checking gives an error with incomplete user configuration."""
    project_list: List = []
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        read_user_config.check_user_configuration(project_list, "projecten.txt")
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code is None


def test_read_required_waterbodies() -> None:
    """Tests reading the required waterbodies, including the datatypes."""
    assert isinstance(read_user_config.read_required_waterbodies(), list)
    assert len(read_user_config.read_required_waterbodies()) > 0
    assert isinstance(read_user_config.read_required_waterbodies()[0], str)


def test_read_required_projects() -> None:
    """Tests reading the required projects, including the datatypes."""
    assert isinstance(read_user_config.read_required_projects(), list)
    assert len(read_user_config.read_required_projects()) > 0
    assert isinstance(read_user_config.read_required_projects()[0], str)
