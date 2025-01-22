"""Tests checking the configuration files."""

import pandas as pd
import pytest
from pytest import LogCaptureFixture
import pytest_mock

from checks import check_config
from preparation import read_system_config


def test_check_waterbody_configuration_files(mocker: pytest_mock.MockerFixture) -> None:
    """Tests checking the waterbody configuration files.

    Args:
        mocker (pytest_mock.MockerFixture): fixing the result of read_yaml_configuration function.
    """
    waterbodies = ["Noordzee", "Waddenzee", "Boven en Beneden Merwede"]
    locations = ["NRDZE_0001", "WDZE_0001", "BNMW_0001"]
    methodes = ["BOXCR", "BOXCR", "BOXCR"]

    waterbody_system_cols = read_system_config.read_yaml_configuration(
        "exp_waterbody_columns", "global_variables.yaml"
    )
    waterbody_user_cols = read_system_config.read_yaml_configuration(
        "exp_location_columns", "global_variables.yaml"
    )

    wl_system = pd.DataFrame(
        columns=waterbody_system_cols,
        index=range(3),
    )
    wl_system["Waterlichaam"] = waterbodies
    wl_system["Heeft_Seizoen"] = True
    wl_system["Trendgroep"] = ["zout", "zout", "zoet"]
    wl_system["Determinatie_protocol"] = "zoet"
    wl_system["Startjaar"] = 1999
    wl_user = pd.DataFrame(waterbodies, columns=["Waterlichaam"])

    wl_loc = pd.DataFrame(columns=waterbody_user_cols, index=range(3))
    wl_loc["Waterlichaam"] = waterbodies
    wl_loc["Meetobject_Code"] = locations
    wl_loc["Methode"] = methodes
    wl_loc["Methode"] = "MWTL_MZB"

    mocker.patch(
        "checks.check_config.read_waterbody_configuration_files",
        return_value=(wl_system, wl_user, wl_loc),
    )
    result = check_config.check_waterbody_configuration_files()
    assert result is True

    waterbodies_user_non_unique = [
        "Noordzee",
        "Noordzee",
        "Waddenzee",
        "Boven en Beneden Merwede",
    ]
    wl_user = pd.DataFrame(waterbodies_user_non_unique, columns=["Waterlichaam"])
    mocker.patch(
        "checks.check_config.read_waterbody_configuration_files",
        return_value=(wl_system, wl_user, wl_loc),
    )
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        check_config.check_waterbody_configuration_files()
        assert pytest_wrapped_e.type == SystemExit


def test_read_waterbody_configuration_files() -> None:
    """Tests reading the waterbody configuration files."""
    wl_system, wl_user, wl_loc = check_config.read_waterbody_configuration_files()

    assert isinstance(wl_system, pd.DataFrame)
    assert isinstance(wl_user, pd.DataFrame)
    assert isinstance(wl_loc, pd.DataFrame)
    assert len(wl_system.index) > 0
    assert len(wl_user.index) > 0
    assert len(wl_loc.index) > 0


def test_check_waterbody_equality(mocker: pytest_mock.MockerFixture) -> None:
    """Tests checking whether the waterbodies from user, system and location config are equal.

    Args:
        mocker (pytest_mock.MockerFixture): fixed output of the read_waterbody_configuration_files.
    """
    waterbodies_system = ["Noordzee", "Waddenzee", "Boven en Beneden Merwede"]
    waterbodies_user = ["Noordzee", "Waddenzee", "Boven en Beneden Merwede"]
    waterbodies_loc = ["Noordzee", "Waddenzee", "Boven en Beneden Merwede"]
    locations = ["NRDZE_0001", "WDZE_0001", "BNMW_0001"]
    methodes = ["BOXCR", "BOXCR", "BOXCR"]

    wl_system = pd.DataFrame(waterbodies_system, columns=["Waterlichaam"])
    wl_user = pd.DataFrame(waterbodies_user, columns=["Waterlichaam"])
    wl_loc = pd.DataFrame(
        list(zip(waterbodies_loc, locations, methodes)),
        columns=["Waterlichaam", "Meetobject_Code", "Methode"],
    )

    mocker.patch(
        "checks.check_config.read_waterbody_configuration_files",
        return_value=(wl_system, wl_user, wl_loc),
    )

    result = check_config.check_waterbody_equality(wl_system, wl_user, wl_loc)
    assert result is True


def test_check_waterbody_equality_invalid(mocker: pytest_mock.MockerFixture) -> None:
    """Tests the error of checking whether the waterbodies from user, system and location config are equal.

    Args:
        mocker (pytest_mock.MockerFixture): fixed output of the read_waterbody_configuration_files.
    """
    waterbodies_system = ["Foute naam", "Waddenzee", "Boven en Beneden Merwede"]
    waterbodies_user = ["Noordzee", "Waddenzee", "Boven en Beneden Merwede"]
    waterbodies_loc = ["Noordzee", "Waddenzee", "Boven en Beneden Merwede"]
    locations = ["NRDZE_0001", "WDZE_0001", "BNMW_0001"]
    methodes = ["BOXCR", "BOXCR", "BOXCR"]

    wl_system = pd.DataFrame(waterbodies_system, columns=["Waterlichaam"])
    wl_user = pd.DataFrame(waterbodies_user, columns=["Waterlichaam"])
    wl_loc = pd.DataFrame(
        list(zip(waterbodies_loc, locations, methodes)),
        columns=["Waterlichaam", "Meetobject_Code", "Methode"],
    )

    mocker.patch(
        "checks.check_config.read_waterbody_configuration_files",
        return_value=(wl_system, wl_user, wl_loc),
    )

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        check_config.check_waterbody_equality(wl_system, wl_user, wl_loc)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code is None


def test_check_bisi_area_equality() -> None:
    """Tests checking whether the BISI areas are qual."""
    bisi_config = pd.DataFrame({"BISI_indeling": ["Doggersbank HR", "Diep zand"]})
    locations = pd.DataFrame(
        {
            "Meetobject_Code": ["MP1", "MP2"],
            "BISI_gebied": ["Doggersbank HR", "Diep zand"],
            "BISI_custom": ["Doggersbank HR", "Diep zand"],
        }
    )

    result = check_config.check_bisi_area_equality(bisi_config, locations)
    assert result is True


def test_check_bisi_area_equality_invalid() -> None:
    """Tests the error when checking the BISI areas which are not equal."""
    bisi_config = pd.DataFrame({"BISI_indeling": ["Doggersbank HR", "Diep zand"]})
    locations = pd.DataFrame(
        {
            "Meetobject_Code": ["MP1", "MP2"],
            "BISI_gebied": ["Doggersbank HR area", "Diep zandig"],
            "BISI_custom": ["Doggersbank HR", "Diep zand"],
        }
    )

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        check_config.check_bisi_area_equality(bisi_config, locations)
    assert pytest_wrapped_e.type == SystemExit


def test_check_bisi_cols_in_locations() -> None:
    """Tests checking whether the BISI columns are in the locations."""
    locations = pd.DataFrame(columns=["BISI_1", "BISI_2", "BISI_3", "BISI_4"])
    assert check_config.check_bisi_cols_in_locations(locations) == True

    locations = pd.DataFrame(
        columns=[
            "BISI_1",
            "BISI_2",
            "BISI_3",
            "BISI_4",
            "BISI_5",
            "BISI_6",
            "BISI_7",
            "BISI_8",
            "BISI_9",
        ]
    )
    assert check_config.check_bisi_cols_in_locations(locations) == True


def test_check_bisi_cols_in_location_invalid() -> None:
    """Tests the error when checking whether the BISI columns are in the locations."""
    locations = pd.DataFrame(columns=["BISIE_1", "BIZI_2"])
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        check_config.check_bisi_cols_in_locations(locations) == True
    assert pytest_wrapped_e.type == SystemExit


def test_check_bisi_configuration_files(mocker: pytest_mock.MockerFixture) -> None:
    """Tests checking the BISI configuration files.

    Args:
        mocker (pytest_mock.MockerFixture): the fixed result of read_csv_file for BISI config.
    """
    bisi_config = pd.DataFrame({"BISI_indeling": ["Doggersbank HR", "Diep zand"]})
    locations = pd.DataFrame(
        {
            "Meetobject_Code": ["MP1", "MP2"],
            "BISI_gebied": ["Doggersbank HR", "Diep zand"],
            "BISI_custom": ["Doggersbank HR", "Diep zand"],
        }
    )

    mocker.patch(
        "preparation.read_system_config.read_bisi_config",
        return_value=bisi_config,
    )
    mocker.patch(
        "preparation.read_system_config.read_csv_file",
        return_value=locations,
    )
    result = check_config.check_bisi_configuration_files()
    assert result is True


def test_check_bisi_configuration_files_invalid(
    mocker: pytest_mock.MockerFixture,
) -> None:
    """Tests checking the BISI configuration files.

    Args:
        mocker (pytest_mock.MockerFixture): the fixed result of read_csv_file for BISI config.
        caplog (LogCaptureFixture): the logging message and level.
    """
    bisi_config = pd.DataFrame({"BISI_indeling": ["Doggersbank HR", "Diep zand"]})
    locations = pd.DataFrame(
        {
            "Meetobject_Code": ["MP1", "MP2"],
            "BISI_gebied": ["Doggersbank (HR-area)", "Diep zand"],
            "BISI_custom": ["Doggersbank HR", "Diep zand"],
        }
    )

    mocker.patch(
        "preparation.read_system_config.read_bisi_config",
        return_value=bisi_config,
    )
    mocker.patch(
        "preparation.read_system_config.read_csv_file",
        return_value=locations,
    )

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        check_config.check_bisi_configuration_files()
    assert pytest_wrapped_e.type == SystemExit


def test_read_groups_config() -> None:
    """Tests reading the groups from the configuration file."""
    groups = read_system_config.read_groups_config(["overgang"])
    assert isinstance(groups, pd.DataFrame)
    assert len(groups.index) > 0


def test_read_bisi_config() -> None:
    """Tests reading the BISI configuration file."""
    bisi_config = read_system_config.read_bisi_config()
    assert isinstance(bisi_config, pd.DataFrame)
    assert len(bisi_config.index) > 0


def test_read_column_mapping() -> None:
    """Tests reading the columns for mapping from the data_model config."""
    column_mapping = read_system_config.read_column_mapping()
    assert isinstance(column_mapping, pd.DataFrame)
    assert len(column_mapping.index) > 0


def test_read_analysis_names() -> None:
    """Tests reading the analysis names from the data_model configuration."""
    analysis_names = read_system_config.read_analysis_names()
    assert isinstance(analysis_names, pd.DataFrame)
    assert len(analysis_names.index) > 0


def test_read_skipped_columns() -> None:
    """Tests reading the skipped columns from the data_model configuration."""
    skipped_columns = read_system_config.read_skipped_columns()
    assert isinstance(skipped_columns, str)
    assert len(skipped_columns) > 0


def test_read_waterbodies_config() -> None:
    """Tests reading the waterbodies configuration file."""
    waterbodies_config = read_system_config.read_waterbodies_config(["Volkerak"])
    assert isinstance(waterbodies_config, pd.DataFrame)
    assert len(waterbodies_config.index) > 0


def test_read_locations_config_error(caplog: LogCaptureFixture) -> None:
    """Tests the error when reading location configuration file with error.

    Args:
        caplog (LogCaptureFixture): the error message and level as log.
    """
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        read_system_config.read_locations_config(["Volkerak"], ["MWTL_MZB"])
    assert pytest_wrapped_e.type == SystemExit

    expected_loglevel = "ERROR"
    expected_message = (
        "Er zijn geen locaties bekend voor de combinatie ['Volkerak'] en ['MWTL_MZB']."
    )
    assert caplog.text.find(expected_loglevel) != -1
    assert caplog.text.find(expected_message) != -1


def test_read_locations_config() -> None:
    """Tests reading the location configuration file."""
    locations_config = read_system_config.read_locations_config(
        ["Volkerak"], ["MWTL_MACEV"]
    )
    assert isinstance(locations_config, pd.DataFrame)
    assert len(locations_config.index) > 0


def test_check_taxon_groups_unique(mocker: pytest_mock.MockerFixture) -> None:
    """Tests checking the taxon group classification.
    colors for each group are unique."""

    group_colors = pd.DataFrame(
        {
            "Trendgroep": 5 * ["zout"],
            "Groep": ["Bivalvia", "Bivalvia", "Gastropoda", "Gastropoda", "Polychaeta"],
            "Groepkleur": ["#000000", "#000000", "#111111", "#111111", "#333333"],
        }
    )

    mocker.patch(
        "preparation.read_system_config.read_csv_file",
        return_value=group_colors,
    )
    has_NA, is_unique = check_config.check_taxon_groups()
    assert has_NA is False
    assert is_unique


def test_check_taxon_groups_non_unique(
    mocker: pytest_mock.MockerFixture, caplog: LogCaptureFixture
) -> None:
    """Tests checking the taxon group classification.
    colors for each group are unique."""

    groups = pd.DataFrame(
        {
            "Trendgroep": 5 * ["zout"],
            "Groep": ["Bivalvia", "Bivalvia", "Gastropoda", "Gastropoda", "Polychaeta"],
            "Groepkleur": ["#000000", "#000000", "#111111", "#222222", "#333333"],
        }
    )

    mocker.patch(
        "preparation.read_system_config.read_csv_file",
        return_value=groups,
    )

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        check_config.check_taxon_groups()
    assert pytest_wrapped_e.type == SystemExit

    expected_loglevel = "ERROR"
    exp_message = "De combinatie van kolommen ['Trendgroep', 'Groep'] in de Taxon_groups.csv data is 2x niet uniek voor"
    assert caplog.text.find(expected_loglevel) != -1
    assert exp_message in caplog.text
