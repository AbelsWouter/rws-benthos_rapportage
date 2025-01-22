"""Tests calculating the BISI indices."""

import logging

import pandas as pd
from pytest import LogCaptureFixture
import pytest_mock

from analysis import BISI


logger = logging.getLogger(__name__)


def test_read_bisi_criteria() -> None:
    """Tests reading the BISI criteria."""
    df_bisi_criteria = BISI.read_bisi_criteria(".//configs//BISI.xlsx", "COE v3", 3)
    assert df_bisi_criteria.shape[0] == 20


def test_add_missing_space_before() -> None:
    """Tests adding missing spaces before a specified character if not already there."""
    input_string = "Dredge 20 m2"
    expected = "Dredge 20 m2"
    assert BISI.add_missing_space_before(input_string, "m2") == expected

    input_string = "Dredge 20m2"
    expected = "Dredge 20 m2"
    assert BISI.add_missing_space_before(input_string, "m2") == expected

    input_string = "Boxcore/Hamon (0,078-0,09 m2"
    expected = "Boxcore/Hamon (0,078-0,09 m2"
    assert BISI.add_missing_space_before(input_string, "m2") == expected

    input_string = "Boxcore/Hamon (0,078-0,09m2"
    expected = "Boxcore/Hamon (0,078-0,09 m2"
    assert BISI.add_missing_space_before(input_string, "m2") == expected


def test_map_sampling_device_to_bisi(
    df_input: pd.DataFrame = pd.DataFrame({"Bemonsteringsapp": ["BODSF", "BOXCRR"]}),
    expected: pd.DataFrame = pd.DataFrame(
        {"Bemonsteringsapp": ["Dredge (20 m2)", "Boxcore (0,078 m2)"]}
    ),
    sampling_devices_config: dict = {
        "Dredge (20 m2)": "BODSF",
        "Boxcore (0,078 m2)": "BOXCRR",
    },
) -> None:
    """Tests mapping the sampling device to the BISI.

    Args:
        df_input (pd.DataFrame) the input for mapping. Defaults to pd.DataFrame({
            "Bemonsteringsapp": ["BODSF", "BOXCRR"]}).
        expected (pd.DataFrame ): the expected output. Defaults to pd.DataFrame( {
            "Bemonsteringsapp": ["Dredge (20 m2)", "Boxcore (0,078 m2)"]} ).
        sampling_devices_config (dict): the sampling devices. Defaults to {
            "Dredge (20 m2)": "BODSF", "Boxcore (0,078 m2)": "BOXCRR", }.
    """
    result = BISI.map_sampling_device_to_bisi(df_input, sampling_devices_config)
    pd.testing.assert_frame_equal(result, expected)


def test_map_sampling_device_to_bisi_combined(
    df_input: pd.DataFrame = pd.DataFrame(
        {"Bemonsteringsapp": ["BODSF", "BOXCRR", "HAMHPR", "VIDOCMRA"]}
    ),
    expected: pd.DataFrame = pd.DataFrame(
        {
            "Bemonsteringsapp": [
                "Dredge/Video (20 or 240 m2)",
                "Boxcore/Hamon (0,078-0,09 m2)",
                "Boxcore/Hamon (0,078-0,09 m2)",
                "Dredge/Video (20 or 240 m2)",
            ]
        }
    ),
    sampling_devices_config: dict = {
        "Boxcore/Hamon (0,078-0,09 m2)": "BOXCRR/HAMHPR",
        "Dredge/Video (20 or 240 m2)": "BODSF/VIDOCMRA",
    },
) -> None:
    """Tests mapping the combined sampling devices to the BISI data.

    Args:
        df_input (pd.DataFrame): the data to be mapped. Defaults to pd.DataFrame( {
            "Bemonsteringsapp": ["BODSF", "BOXCRR", "HAMHPR", "VIDOCMRA"]} ).
        expected (pd.DataFrame): the expected sampling devices. Defaults to pd.DataFrame(see above).
        sampling_devices_config (dict): the sampling devices. Defaults to {
            "Boxcore/Hamon (0,078-0,09 m2)": "BOXCRR/HAMHPR", "Dredge/Video (20 or 240 m2)": "BODSF/VIDOCMRA", }.
    """
    result = BISI.map_sampling_device_to_bisi(df_input, sampling_devices_config)
    pd.testing.assert_frame_equal(result, expected)


def test_fix_abbreviated_genus_names() -> None:
    """Tests fixing the abbreviated genus names to match the input data."""
    result = BISI.fix_abbreviated_genus_names("Magelona johnstoni + M. filiformis")
    assert result == "Magelona johnstoni + Magelona filiformis"
    result = BISI.fix_abbreviated_genus_names("Magelona johnstoni / M. filiformis")
    assert result == "Magelona johnstoni / Magelona filiformis"
    result = BISI.fix_abbreviated_genus_names("Magelona johnstoni+M. filiformis")
    assert result == "Magelona johnstoni+Magelona filiformis"
    result = BISI.fix_abbreviated_genus_names("Magelona johnstoni/M. filiformis")
    assert result == "Magelona johnstoni/Magelona filiformis"
    result = BISI.fix_abbreviated_genus_names("Magelona johnstoni")
    assert result == "Magelona johnstoni"


def test_remove_taxa_postfixes() -> None:
    """Tests removing the postfixes in the taxa to match the input data."""
    result = BISI.remove_taxa_postfixes("Upogebia deltaura*")
    assert result == "Upogebia deltaura"
    result = BISI.remove_taxa_postfixes("Upogebia stellata**")
    assert result == "Upogebia stellata"
    result = BISI.remove_taxa_postfixes("Terebellides spp.")
    assert result == "Terebellides"


def test_map_taxa_to_bisi(
    input_map_taxa_to_bisi: pd.DataFrame,
    input_indicator_species: pd.DataFrame,
    output_map_taxa_to_bisi: pd.DataFrame,
) -> None:
    """Tests mapping the taxa to the BISI calculation.

    Args:
        input_map_taxa_to_bisi (pd.DataFrame): Fixture with the input for the BISI.
        input_indicator_species (pd.DataFrame): Fixture with the BISI indicator species.
        output_map_taxa_to_bisi (pd.DataFrame): Fixture with the mapped taxa.
    """
    result = BISI.map_taxa_to_bisi(input_map_taxa_to_bisi, input_indicator_species)
    pd.testing.assert_frame_equal(result, output_map_taxa_to_bisi)


def test_check_bisi_taxa(
    twn_corrected: pd.DataFrame, mocker: pytest_mock.MockerFixture
) -> None:
    """Tests checking the BISI taxa for invalid twn or synonym.

    Args:
        twn_corrected (pd.DataFrame): the corrected TWN data.
        mocker (pytest_mock.MockerFixture): fixed result of reading the corrected twn.
    """
    mocker.patch(
        "preparation.read_system_config.read_csv_file",
        return_value=twn_corrected,
    )
    df_input = pd.DataFrame({"Analyse_taxonnaam": ["Ablabesmyia"]})
    bisi_area = "BISI_gebied"
    result = BISI.check_bisi_taxa(df_input, bisi_area)
    assert result is True


def test_check_bisi_taxa_combined(
    twn_corrected: pd.DataFrame, mocker: pytest_mock.MockerFixture
) -> None:
    """Tests checking the BISI taxa with combined (+) taxa.

    Args:
        twn_corrected (pd.DataFrame): the corrected TWN data.
        mocker (pytest_mock.MockerFixture): fixed result of reading the corrected twn.
    """
    mocker.patch(
        "preparation.read_system_config.read_csv_file",
        return_value=twn_corrected,
    )
    df_input = pd.DataFrame({"Analyse_taxonnaam": ["Ablabesmyia + A."]})
    bisi_area = "BISI_gebied"
    result = BISI.check_bisi_taxa(df_input, bisi_area)
    assert result is True


def test_check_bisi_taxa_invalid(
    twn_corrected: pd.DataFrame,
    mocker: pytest_mock.MockerFixture,
    caplog: LogCaptureFixture,
) -> None:
    """Tests the error when checking the BISI taxa with invalid taxa.

    Args:
        twn_corrected (pd.DataFrame): the corrected TWN data.
        mocker (pytest_mock.MockerFixture): fixed result of reading the corrected twn.
        caplog (LogCaptureFixture): the logging message and level.
    """
    mocker.patch(
        "preparation.read_system_config.read_csv_file",
        return_value=twn_corrected,
    )
    df_input = pd.DataFrame({"Analyse_taxonnaam": ["Campanulina johnstoni"]})
    bisi_area = "BISI_gebied"
    result = BISI.check_bisi_taxa(df_input, bisi_area)
    expected_loglevel = "WARNING"
    expected_message = (
        "zijn de volgende taxa in de BISI tabel onbekend of ongeldig in de TWN."
    )
    assert caplog.text.find(expected_loglevel) != -1
    assert caplog.text.find(expected_message) != -1
    assert result is False


def test_check_sample_species(input_check_samples: pd.DataFrame) -> None:
    """Tests checking the sample species.

    Args:
        input_check_samples (pd.DataFrame): the input samples for the BISI.
    """
    df_bisi_criteria = pd.DataFrame(
        {
            "Analyse_taxonnaam": ["Acanthocardia echinata", "Amphiura filiformis"],
            "Bemonsteringsapp": ["Dredge (20 m2)", "Boxcore (0,078 m2)"],
            "Expected_n": [2, 2],
        }
    )
    bisi_col = "BISI_gebied"

    expected = pd.DataFrame(
        {
            "Monsterjaar": [2019, 2019],
            "BISI_gebied": ["Centrale Oestergronden", "Centrale Oestergronden"],
            "Bemonsteringsapp": ["Boxcore (0,078 m2)", "Dredge (20 m2)"],
            "Nmonsters": [2, 2],
        },
        index=[0, 1],
    )

    result = BISI.check_sample_species(input_check_samples, df_bisi_criteria, bisi_col)
    pd.testing.assert_frame_equal(result[["Monsterjaar"]], expected[["Monsterjaar"]])


def test_check_sample_species_less_samples(
    input_check_samples: pd.DataFrame, caplog: LogCaptureFixture
) -> None:
    """Tests checking the samples if there are not enough samples.

    Args:
        input_check_samples (pd.DataFrame): input samples with not enough samples.
        caplog (LogCaptureFixture): the logging message and level.
    """
    df_bisi_criteria = pd.DataFrame(
        {
            "Analyse_taxonnaam": ["Acanthocardia echinata", "Amphiura filiformis"],
            "Bemonsteringsapp": ["Dredge (20 m2)", "Boxcore (0,078 m2)"],
            "Expected_n": [3, 8],
        }
    )
    bisi_col = "BISI_gebied"
    expected = pd.DataFrame(
        {
            "Monsterjaar": [2019, 2019],
            "BISI_gebied": ["Centrale Oestergronden", "Centrale Oestergronden"],
            "Bemonsteringsapp": ["Boxcore (0,078 m2)", "Dredge (20 m2)"],
            "Nmonsters": [2, 2],
        },
        index=[0, 1],
    )
    expected_loglevel = "WARNING"
    expected_message = "Het aantal monsters"
    result = BISI.check_sample_species(input_check_samples, df_bisi_criteria, bisi_col)
    assert caplog.text.find(expected_loglevel) != -1
    assert caplog.text.find(expected_message) != -1
    pd.testing.assert_frame_equal(result[["Monsterjaar"]], expected[["Monsterjaar"]])


def test_check_sample_species_less_species(
    input_check_samples: pd.DataFrame, caplog: LogCaptureFixture
) -> None:
    """Tests checking the samples when there are not enough species.

    Args:
        input_check_samples (pd.DataFrame): the input with not enough BISI species.
        caplog (LogCaptureFixture): the logging message and level.
    """
    df_bisi_criteria = pd.DataFrame(
        {
            "Analyse_taxonnaam": [
                "Acanthocardia echinata",
                "Amphiura filiformis",
                "Euspira nitida",
            ],
            "Bemonsteringsapp": [
                "Dredge (20 m2)",
                "Boxcore (0,078 m2)",
                "Boxcore (0,078 m2)",
            ],
            "Expected_n": [2, 2, 2],
        }
    )
    bisi_col = "BISI_gebied"
    expected = pd.DataFrame(
        {
            "Monsterjaar": [2019, 2019],
            "BISI_gebied": ["Centrale Oestergronden", "Centrale Oestergronden"],
            "Bemonsteringsapp": ["Boxcore (0,078 m2)", "Dredge (20 m2)"],
            "Nmonsters": [2, 2],
        },
        index=[0, 1],
    )
    expected_loglevel = "WARNING"
    expected_message = (
        "Niet alle BISI-taxa zijn aanwezig voor ['Centrale Oestergronden']"
    )
    result = BISI.check_sample_species(input_check_samples, df_bisi_criteria, bisi_col)
    assert caplog.text.find(expected_loglevel) != -1
    assert caplog.text.find(expected_message) != -1
    pd.testing.assert_frame_equal(result[["Monsterjaar"]], expected[["Monsterjaar"]])


def test_check_bisi_taxa_unknown(
    twn_corrected: pd.DataFrame,
    mocker: pytest_mock.MockerFixture,
    caplog: LogCaptureFixture,
) -> None:
    """Tests checking the taxa when there are unknown taxa.

    Args:
        twn_corrected (pd.DataFrame):  the corrected TWN data.
        mocker (pytest_mock.MockerFixture): the fixed output of read_csv_file of twn.
        caplog (LogCaptureFixture): the logging message and level.
    """
    mocker.patch(
        "preparation.read_system_config.read_csv_file",
        return_value=twn_corrected,
    )
    df_input = pd.DataFrame({"Analyse_taxonnaam": ["Soort 1"]})
    bisi_area = "BISI_gebied"
    result = BISI.check_bisi_taxa(df_input, bisi_area)
    expected_loglevel = "WARNING"
    expected_message = (
        "zijn de volgende taxa in de BISI tabel onbekend of ongeldig in de TWN."
    )
    assert caplog.text.find(expected_loglevel) != -1
    assert caplog.text.find(expected_message) != -1
    assert result is False


def test_check_bisi_taxa_synonym(
    twn_corrected: pd.DataFrame,
    mocker: pytest_mock.MockerFixture,
    caplog: LogCaptureFixture,
) -> None:
    """Tests checking the taxa for synonymns.

    Args:
        twn_corrected (pd.DataFrame):  the corrected TWN data.
        mocker (pytest_mock.MockerFixture): the fixed output of read_csv_file of twn.
        caplog (LogCaptureFixture): the logging message and level.
    """
    mocker.patch(
        "preparation.read_system_config.read_csv_file",
        return_value=twn_corrected,
    )
    df_input = pd.DataFrame(
        {"Analyse_taxonnaam": ["Turritella communis", "Limecola balthica"]}
    )
    bisi_area = "BISI_gebied"
    result = BISI.check_bisi_taxa(df_input, bisi_area)
    expected_loglevel = "WARNING"
    expected_message = (
        "zijn de volgende taxa in de BISI tabel onbekend of ongeldig in de TWN."
    )
    assert caplog.text.find(expected_loglevel) != -1
    assert caplog.text.find(expected_message) != -1
    assert result is False


def test_check_required_area(input_check_required_area: pd.DataFrame) -> None:
    """Tests checking the required area for the BISI calculation.

    Args:
        input_check_required_area (pd.DataFrame): Fixture with input for the check.
    """
    bisi_area = "BISI_gebied"
    result = BISI.check_required_area(input_check_required_area, bisi_area)
    assert result is True


def test_check_required_area_invalid(
    input_check_required_area_invalid: pd.DataFrame, caplog: LogCaptureFixture
) -> None:
    """Tests the error message when checking the required area when invalid.

    Args:
        input_check_required_area_invalid (pd.DataFrame): Fixture with the invalid area.
        caplog (LogCaptureFixture): the logging message and level.
    """
    bisi_area = "BISI_gebied"
    BISI.check_required_area(input_check_required_area_invalid, bisi_area)
    expected_loglevel = "WARNING"
    expected_message = "De bemonsterde oppervlaktes in de BISI rekensheet en de data zijn niet gelijk in BISI_"
    assert expected_loglevel in caplog.text
    assert expected_message in caplog.text


def test_bisi_calculations(
    input_bisi_calculations: pd.DataFrame,
    input_bisi_criteria: pd.DataFrame,
    output_bisi_calculations: pd.DataFrame,
) -> None:
    """Tests calculating the BISI scores.

    Args:
        input_bisi_calculations (pd.DataFrame): Fixture with the input data.
        input_bisi_criteria (pd.DataFrame): Fixture with the BISI criteria.
        output_bisi_calculations (pd.DataFrame): Fixture with the calculated BISI scores.
    """
    result = BISI.bisi_calculations(input_bisi_calculations, input_bisi_criteria)
    pd.testing.assert_frame_equal(result, output_bisi_calculations)


def test_bisi_main_COM_KRM(
    input_bisi_main: pd.DataFrame,
    output_bisi_main_COM_KRM: pd.DataFrame,
    mocker: pytest_mock.MockerFixture,
) -> None:
    """Tests the integration of calculating the BISI scores for
    Centrale Oestergronden en KRM-Area.

    Args:
        input_bisi_main (pd.DataFrame): Fixture with the input for the BISI script.
        output_bisi_main_COM_KRM (pd.DataFrame): Fixture with the expected output for the BISI.
        mocker (pytest_mock.MockerFixture): fixed result of the check_bisi_taxa function.
    """
    # exclude the twn check, existence of twn_corrected isn't garenteed
    mocker.patch("analysis.BISI.check_bisi_taxa", return_value=None)

    df_input = input_bisi_main[
        (~input_bisi_main["BISI_gebied"].isna())
        & (input_bisi_main["BISI_gebied"].str.contains("Centrale Oestergronden KRM"))
    ]

    result = BISI.main_bisi(df_input)
    pd.testing.assert_frame_equal(
        result.reset_index(drop=True), output_bisi_main_COM_KRM.reset_index(drop=True)
    )


def test_bisi_main_BB_KRM(
    input_bisi_main: pd.DataFrame,
    output_bisi_main_BB_KRM: pd.DataFrame,
    mocker: pytest_mock.MockerFixture,
) -> None:
    """Tests the integration of calculating the BISI scores for
    the Bruine Bank en KRM-Area.

    Args:
        input_bisi_main (pd.DataFrame): Fixture with the input for the BISI script.
        output_bisi_main_BB_KRM (pd.DataFrame): Fixture with the expected output for the BISI.
        mocker (pytest_mock.MockerFixture): Fixed result of the check_bisi_taxa function.
    """
    # exclude the twn check, existence of twn_corrected isn't garenteed
    mocker.patch("analysis.BISI.check_bisi_taxa", return_value=None)

    df_input = input_bisi_main[
        (~input_bisi_main["BISI_gebied"].isna())
        & (input_bisi_main["BISI_gebied"].str.contains("Bruine Bank KRM"))
    ]

    result = BISI.main_bisi(df_input)
    pd.testing.assert_frame_equal(
        result.reset_index(drop=True), output_bisi_main_BB_KRM.reset_index(drop=True)
    )


def test_bisi_main(
    input_bisi_main: pd.DataFrame, mocker: pytest_mock.MockerFixture
) -> None:
    """Tests the integration of the BISI calculations.

    Args:
        input_bisi_main (pd.DataFrame): Fixture with the input for the BISI.
        mocker (pytest_mock.MockerFixture): Fixed output for the check_bisi_taxa.
    """
    # exclude the twn check, existence of twn_corrected isn't garenteed
    mocker.patch("analysis.BISI.check_bisi_taxa", return_value=None)

    df_input = input_bisi_main

    BISI.main_bisi(df_input)
    # LET OP: controleer de gegenereerde BISI tabel handmatig of alle waarden zijn ingevuld
    assert True
