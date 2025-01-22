"""Tests reading the system configurations."""

import logging
import os

import pandas as pd
import pytest


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))

from preparation import read_system_config


logger = logging.getLogger(__name__)


def test_read_yaml_aquadesk_url() -> None:
    """Tests reading the aquadesk url from the aquadesk configuration."""
    config_yaml = "aquadesk.yaml"
    assert (
        read_system_config.read_yaml_configuration("aquadesk_url", config_yaml)
        == "https://ddecoapi.aquadesk.nl/v2/"
    )


def test_read_yaml_apikey() -> None:
    """Tests reading the api key from the aquadesk configuration."""
    config_yaml = "aquadesk.yaml"
    assert isinstance(
        read_system_config.read_yaml_configuration("api_key", config_yaml), str
    )


def test_read_yaml_measurements_query_url() -> None:
    """Tests reading the query url from the aquadesk configuration file."""
    config_yaml = "aquadesk.yaml"
    assert (
        read_system_config.read_yaml_configuration(
            "measurements.query_url", config_yaml
        )
        == "measurements"
    )


def test_read_yaml_measurements_query_filter() -> None:
    """Tests reading the query filter from the aquadesk configuration file."""
    config_yaml = "aquadesk.yaml"
    string = (
        'organisation:eq:"RWS"; collectiondate:ge:"1999-01-01"; '
        'measurementpackage:in:["ME.KG","ME.AB","ME.MS","ME.BD"]; '
        'quantity:in:["VOLME","OPPVTE","BEMSRAPRT","SUBSMTRAL","AANTL","MASSA","BEDKG"];'
    )
    assert (
        read_system_config.read_yaml_configuration(
            "measurements.query_filter", config_yaml
        )
        == string
    )


def test_read_yaml_measurements_page_size() -> None:
    """Tests reading the page size from the aquadesk configuration file."""
    config_yaml = "aquadesk.yaml"
    assert (
        read_system_config.read_yaml_configuration(
            "measurements.page_size", config_yaml
        )
        == 10000
    )


def test_read_yaml_plot_title() -> None:
    """Tests reading the plot_title from the global_variables file."""
    config_yaml = "global_variables.yaml"

    assert read_system_config.read_yaml_configuration(
        "plot_config.titles.Dichtheid_Aantal", config_yaml
    ) == {
        "plot_title": "Gemiddelde dichtheid aantal",
        "y_title": "Gemiddelde dichtheid (n/m²)",
    }


def test_read_yaml_measurements_project() -> None:
    """Tests reading the selection of project from the global_variables config."""
    config_yaml = "global_variables.yaml"
    assert (
        read_system_config.read_yaml_configuration("selection_projects", config_yaml)
        == ".//input//selectie_project.txt"
    )


def test_read_csv_file() -> None:
    """Tests reading the locations from the csv configuration file."""
    configfile = "./configs/locations.csv"
    df = read_system_config.read_csv_file(configfile)
    assert isinstance(df, pd.DataFrame)


def test_read_location_list_exists(mocker: pd.DataFrame) -> None:
    """Tests reading the location list as system configuration.

    Args:
        mocker (pd.DataFrame): the result of read_location_config.
    """
    lst = ["NRDZE_0137", "NRDZE_0305", "NRDZE_0305"]
    lst2 = ["Noordzee", "Noordzee", "Noordzee"]
    df = pd.DataFrame(list(zip(lst, lst2)), columns=["Meetobject_Code", "Waterlichaam"])

    mocker.patch(
        "preparation.read_system_config.read_locations_config", return_value=df
    )

    meetobjecten = read_system_config.read_meetobject_codes([], [])

    assert isinstance(meetobjecten, list)
    assert len(meetobjecten) == len(set(meetobjecten))
    assert set(meetobjecten) == set(["NRDZE_0137", "NRDZE_0305"])


def test_read_location_list_not_exists() -> None:
    """Tests the error for reading locations configuration with wrong input."""
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        read_system_config.read_locations_config(["Noordzeeee"], ["MWTL_MZB"])
        assert pytest_wrapped_e.type == SystemExit


def test_read_skipped_columns() -> None:
    """Tests reading the skipped columns."""
    result = read_system_config.read_skipped_columns()
    assert isinstance(result, str)
    assert result != ""


def test_read_meetobject_codes() -> None:
    """Tests reading the meetobject codes."""
    result = read_system_config.read_meetobject_codes(["Beneden Maas"], ["MWTL_MACEV"])
    assert isinstance(result, list)
    assert len(result) > 0


def test_read_sample_properties() -> None:
    """Tests reading the sample properties."""
    result_script_name = read_system_config.read_sample_properties("script_name")
    result_analysis_name = read_system_config.read_sample_properties("analysis_name")
    assert isinstance(result_script_name, list)
    assert len(result_script_name) > 0
    assert isinstance(result_analysis_name, list)
    assert len(result_analysis_name) > 0
