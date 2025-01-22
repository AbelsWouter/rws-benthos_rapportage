"""Tests the preparation on the Benthos data."""

import numpy as np
import pandas as pd
import pytest
from pytest import LogCaptureFixture
import pytest_mock

from preparation import benthos_data
from preparation import read_system_config


def test_read_benthos_data(filepath_global_var: str) -> None:
    """Test whether reading the benthos data returns a DataFrame.

    Args:
        filepath_global_var (str): the path to the benthos data.
    """
    test_df = benthos_data.read_benthos_data(filepath_global_var)
    assert isinstance(test_df, pd.DataFrame)


def test_initial_column_names(
    filepath_global_var: str, req_columns_script: pd.Series
) -> None:
    """This function checks whether the expected column names are equal to the actual column names.

    Args:
        filepath_global_var (str): the location of the data file to be checked.
        expected_col_names (List): the expected column names.
    """
    df = benthos_data.read_benthos_data(filepath_global_var)
    actual_col_names = list(df.columns)
    assert set(req_columns_script).issubset(actual_col_names)


def test_filter_required_rows(
    input_filter_required_rows: pd.DataFrame, output_filter_required_rows: pd.DataFrame
) -> None:
    """Tests filtering the required rows.

    Args:
        input_filter_required_rows (pd.DataFrame): input for testing.
        output_filter_required_rows (pd.DataFrame): expected output with required rows.
    """
    result = benthos_data.filter_required_rows(input_filter_required_rows)
    pd.testing.assert_frame_equal(
        result.reset_index(drop=True),
        output_filter_required_rows.reset_index(drop=True),
    )


def test_correct_aquadesk_taxa(mocker: pytest_mock.MockerFixture) -> None:
    """Tests correcting the Aquadesk taxa.

    Args:
        mocker (pytest_mock.MockerFixture): the return value from reading the system config.
    """
    data = pd.DataFrame({"Parameter_Specificatie": ["Laonome calida", "Abra alba"]})
    expected = pd.DataFrame({"Parameter_Specificatie": ["Laonome", "Abra alba"]})

    mocker.patch(
        "preparation.read_system_config.read_yaml_configuration",
        return_value={"Laonome calida": "Laonome"},
    )
    result = benthos_data.correct_aquadesk_taxa(data.copy())
    pd.testing.assert_frame_equal(result, expected)


def test_col_bemsraprt(benthos_data_end: pd.DataFrame) -> None:
    """Tests whether the sampling device is in the column.

    Args:
        benthos_data_end (pd.DataFrame): the fixture with the benthos data at the
        end of the preparation phase.
    """
    assert "Bemonsteringsapp" in benthos_data_end.columns


def test_col_opp(benthos_data_end: pd.DataFrame) -> None:
    """Tests whether the area is in the column.

    Args:
        benthos_data_end (pd.DataFrame): the fixture with the benthos data at the
        end of the preparation phase.
    """
    assert "Support" in benthos_data_end.columns


def test_add_sample_year() -> None:
    """Tests adding the sample year"""
    input_df = pd.DataFrame({"Collectie_DatumTijd": ["2022-08-20 12:00:00"]})
    expected = pd.DataFrame(
        {"Collectie_DatumTijd": ["2022-08-20 12:00:00"], "Monsterjaar": [2022]}
    )
    expected["Monsterjaar"] = expected["Monsterjaar"].astype("int32")
    result = benthos_data.add_sample_year(input_df)
    pd.testing.assert_frame_equal(result, expected)

    input_df = pd.DataFrame({"Collectie_DatumTijd": ["2022-08-20 12:00"]})
    expected = pd.DataFrame(
        {"Collectie_DatumTijd": ["2022-08-20 12:00"], "Monsterjaar": [2022]}
    )
    expected["Monsterjaar"] = expected["Monsterjaar"].astype("int32")
    result = benthos_data.add_sample_year(input_df)
    pd.testing.assert_frame_equal(result, expected)

    input_df = pd.DataFrame({"Collectie_DatumTijd": ["2022-08-20"]})
    expected = pd.DataFrame(
        {"Collectie_DatumTijd": ["2022-08-20"], "Monsterjaar": [2022]}
    )
    expected["Monsterjaar"] = expected["Monsterjaar"].astype("int32")
    result = benthos_data.add_sample_year(input_df)
    pd.testing.assert_frame_equal(result, expected)

    input_df = pd.DataFrame({"Collectie_DatumTijd": ["2022/08/20 12:00"]})
    expected = pd.DataFrame(
        {"Collectie_DatumTijd": ["2022/08/20 12:00"], "Monsterjaar": [2022]}
    )
    expected["Monsterjaar"] = expected["Monsterjaar"].astype("int32")
    result = benthos_data.add_sample_year(input_df)
    pd.testing.assert_frame_equal(result, expected)

    input_df = pd.DataFrame({"Collectie_DatumTijd": ["20/08/2022 12:00"]})
    expected = pd.DataFrame(
        {"Collectie_DatumTijd": ["20/08/2022 12:00"], "Monsterjaar": [2022]}
    )
    expected["Monsterjaar"] = expected["Monsterjaar"].astype("int32")
    result = benthos_data.add_sample_year(input_df)
    pd.testing.assert_frame_equal(result, expected)

    # text Aquadesk website input
    input_df = pd.DataFrame({"Collectie_DatumTijd": ["20/08/2022 12:00"]})
    input_df["Collectie_DatumTijd"] = pd.to_datetime(
        input_df["Collectie_DatumTijd"], format="%d/%m/%Y %H:%M", utc=True
    )

    expected = pd.DataFrame(
        {"Collectie_DatumTijd": ["2022-08-20 12:00:00+00:00"], "Monsterjaar": [2022]}
    )
    expected["Monsterjaar"] = expected["Monsterjaar"].astype("int32")
    result = benthos_data.add_sample_year(input_df)
    pd.testing.assert_frame_equal(result, expected)


def test_mark_clustered_sample_year(
    mocker: pytest_mock.MockerFixture,
    input_cluster_samples: pd.DataFrame,
    output_cluster_samples: pd.DataFrame,
) -> None:
    """Tests aggregating the year"""
    cluster_config = [[2018, 2019], [2021, 2022]]
    mocker.patch(
        "preparation.read_system_config.read_yaml_configuration",
        return_value=cluster_config,
    )
    result = benthos_data.mark_cluster_sample_years(input_cluster_samples)
    pd.testing.assert_frame_equal(result, output_cluster_samples)


def test_calculate_density_aantal(
    input_benthos_density: pd.DataFrame, output_benthos_density_aantal: pd.DataFrame
) -> None:
    """Tests calculating the density for count.

    Args:
        input_benthos_density (pd.DataFrame): Fixture with the input for calculations.
        output_benthos_density_aantal (pd.DataFrame): Fixture with the expected count densities.
    """
    result = benthos_data.calculate_density(input_benthos_density, "Aantal")
    pd.testing.assert_frame_equal(result, output_benthos_density_aantal)


def test_calculate_density_massa(
    input_benthos_density: pd.DataFrame, output_benthos_density_massa: pd.DataFrame
) -> None:
    """Tests calculating the density for mass.

    Args:
        input_benthos_density (pd.DataFrame): Fixture with the input for calculations.
        output_benthos_density_aantal (pd.DataFrame): Fixture with the expected mass densities.
    """
    result = benthos_data.calculate_density(input_benthos_density, "Massa")
    pd.testing.assert_frame_equal(result, output_benthos_density_massa)


def test_append_multiple_season(
    df_multiple_season: pd.DataFrame = pd.DataFrame(
        {
            "Collectie_Referentie": [1, 1, 2, 2, 3, 3],
            "Collectie_DatumTijd": [
                "2023-11-20",
                "2023-11-20",
                "2023-06-20",
                "2023-06-20",
                "2023-01-20",
                "2023-01-20",
            ],
            "Monsterjaar": [2023, 2023, 2023, 2023, 2023, 2023],
            "Waterlichaam": ["w", "w", "w", "w", "w", "w"],
        }
    ),
    expected_result: pd.DataFrame = pd.DataFrame(
        {
            "Collectie_Referentie": [1, 1, 2, 2, 3, 3],
            "Collectie_DatumTijd": [
                "2023-11-20",
                "2023-11-20",
                "2023-06-20",
                "2023-06-20",
                "2023-01-20",
                "2023-01-20",
            ],
            "Monsterjaar": [2023, 2023, 2023, 2023, 2023, 2023],
            "Waterlichaam": ["w", "w", "w", "w", "w", "w"],
            "Seizoen": [
                "najaar",
                "najaar",
                "voorjaar",
                "voorjaar",
                "voorjaar",
                "voorjaar",
            ],
        }
    ),
) -> None:
    """Tests adding multiple seasons to the benthos data.

    Args:
        df_multiple_season (pd.DataFrame): data with multiple seasons. Defaults to a pd.DataFrame (see above).
        expected_result (pd.DataFrame): expected seasons added. Defaults to pd.DataFrame (see above).
    """
    df_new = benthos_data.add_season(df_multiple_season)
    assert df_new.equals(expected_result)


def test_append_single_season(
    df_single_season: pd.DataFrame = pd.DataFrame(
        {
            "Collectie_Referentie": [1, 1, 2, 2, 3, 3],
            "Collectie_DatumTijd": [
                "2023-08-20",
                "2023-08-20",
                "2023-09-20",
                "2023-09-20",
                "2023-07-20",
                "2023-07-20",
            ],
            "Monsterjaar": [2023, 2023, 2023, 2023, 2023, 2023],
            "Waterlichaam": ["w", "w", "w", "w", "w", "w"],
        }
    ),
    expected_result: pd.DataFrame = pd.DataFrame(
        {
            "Collectie_Referentie": [1, 1, 2, 2, 3, 3],
            "Collectie_DatumTijd": [
                "2023-08-20",
                "2023-08-20",
                "2023-09-20",
                "2023-09-20",
                "2023-07-20",
                "2023-07-20",
            ],
            "Monsterjaar": [2023, 2023, 2023, 2023, 2023, 2023],
            "Waterlichaam": ["w", "w", "w", "w", "w", "w"],
            "Seizoen": ["najaar", "najaar", "najaar", "najaar", "najaar", "najaar"],
        }
    ),
) -> None:
    """Tests adding a single season to the data.

    Args:
        df_single_season (pd.DataFrame): data with one single season. Defaults to pd.DataFrame (see above).
        expected_result (pd.DataFrame): expected seasons added. Defaults to pd.DataFrame (see above).
    """
    df_new = benthos_data.add_season(df_single_season)
    assert df_new.equals(expected_result)


def test_check_season_error_types(
    input_check_season: pd.DataFrame, output_check_season: pd.DataFrame
) -> None:
    """Tests checking if multiple seasons are present and allowed.

    Args:
        input_check_season (pd.DataFrame): fixture with input data for checking.
        output_check_season (pd.DataFrame): fixture with expected checked seasons.
    """
    result = benthos_data.check_season(input_check_season)
    pd.testing.assert_frame_equal(
        result.reset_index(drop=True), output_check_season.reset_index(drop=True)
    )


def test_check_season_no_spring(
    input_check_season_no_spring: pd.DataFrame,
    output_check_season_no_spring: pd.DataFrame,
) -> None:
    """Tests checking seasons with no spring.

    Args:
        input_check_season_no_spring (pd.DataFrame): fixture with data but no spring.
        output_check_season_no_spring (pd.DataFrame): fixture with expected output.
    """
    result = benthos_data.check_season(input_check_season_no_spring)
    pd.testing.assert_frame_equal(
        result.reset_index(drop=True),
        output_check_season_no_spring.reset_index(drop=True),
    )


def test_check_season_no_autumn(
    input_check_season_no_autumn: pd.DataFrame,
    output_check_season_no_autumn: pd.DataFrame,
) -> None:
    """Tests checking seasons with no autumn.

    Args:
        input_check_season_no_autumn (pd.DataFrame): fixture with data but no autumns.
        output_check_season_no_autumn (pd.DataFrame): fixture with expected output.
    """
    result = benthos_data.check_season(input_check_season_no_autumn)
    pd.testing.assert_frame_equal(
        result.reset_index(drop=True),
        output_check_season_no_autumn.reset_index(drop=True),
    )


def test_mark_azoisch(
    df_input: pd.DataFrame = pd.DataFrame(
        {
            "Analyse_taxonnaam": ["Animalia", "Animalia", "Animalia"],
            "Waarde_Berekend": [1, 0, 0],
            "Limiet_Symbool": [None, ">", None],
        }
    ),
    df_expected: pd.DataFrame = pd.DataFrame(
        {
            "Analyse_taxonnaam": ["Animalia", "Animalia", "Azoisch"],
            "Waarde_Berekend": [1, 0, 0],
            "Limiet_Symbool": [None, ">", None],
        }
    ),
) -> None:
    """Tests marking taxa as azoisch

    Args:
        df_input (pd.DataFrame): the input for marking azosich. Defaults to pd.DataFrame (see above).
        df_expected (pd.DataFrame): the expected output. Defaults to pd.DataFrame (see above).
    """

    result = benthos_data.mark_azoisch(df_input)
    pd.testing.assert_frame_equal(result, df_expected)


def test_presence_to_abundance(
    input_presence_to_abundance: pd.DataFrame,
    output_presence_to_abundance: pd.DataFrame,
) -> None:
    """Tests setting the presence to abundance for the taxa which should be counted.
    Only taxa that should be counted (screening) are set to 1, the rest stays 0 (bryozoa etc.).

    Args:
        df_input (pd.DataFrame): the input with presences.
        df_expected (pd.DataFrame): the expected output with corrrected abundances.
    """
    result = benthos_data.presence_to_abundance(input_presence_to_abundance)
    pd.testing.assert_frame_equal(result, output_presence_to_abundance)


def test_abundance_to_presence(
    input_abundance_to_presence: pd.DataFrame,
    output_abundance_to_presence: pd.DataFrame,
) -> None:
    """Tests setting the abundance to presence for the taxa which not should be counted.

    Args:
        input_biomass_to_missing (pd.DataFrame): the input with abundance data.
        df_expected (pd.DataFrame): the expected output with corrected presence.
    """
    result = benthos_data.abundance_to_presence(input_abundance_to_presence)
    pd.testing.assert_frame_equal(result, output_abundance_to_presence)


def test_biomass_to_missing(
    input_biomass_to_missing: pd.DataFrame, output_biomass_to_missing: pd.DataFrame
) -> None:
    """Tests setting the biomass to missing for the taxa which not should be weighted.

    Args:
        input_biomass_to_missing (pd.DataFrame): the input with biomass data.
        df_expected (pd.DataFrame): the expected with corrected biomasses.
    """
    result = benthos_data.biomass_to_missing(input_biomass_to_missing)
    pd.testing.assert_frame_equal(result, output_biomass_to_missing)


def test_aggregate_taxa(
    input_aggregate_taxa: pd.DataFrame, output_aggregate_taxa: pd.DataFrame
) -> None:
    """Tests aggregating benthos taxa.

    Args:
        input_aggregate_taxa (pd.DataFrame): Fixture with the input for aggregation.
        output_aggregate_taxa (pd.DataFrame): Fixture with the expected aggregated taxa.
    """
    result = benthos_data.aggregate_taxa(input_aggregate_taxa)
    pd.testing.assert_frame_equal(result, output_aggregate_taxa)


def test_aggregate_analysis_taxa(
    input_aggregate_analysis_taxa: pd.DataFrame,
    output_aggregate_analysis_taxa: pd.DataFrame,
) -> None:
    """Tests aggregating analysis benthos taxa.

    Args:
        input_aggregate_taxa (pd.DataFrame): Fixture with the input for aggregation analysis taxa.
        output_aggregate_taxa (pd.DataFrame): Fixture with the expected aggregated analysis taxa.
    """
    result = benthos_data.aggregate_analysis_taxa(input_aggregate_analysis_taxa)
    pd.testing.assert_frame_equal(result, output_aggregate_analysis_taxa)


def test_aggregate_analysis_taxa_error(
    input_aggregate_analysis_taxa_error: pd.DataFrame,
    caplog: LogCaptureFixture,
) -> None:
    """Tests the error message for aggregating analysis taxa.

    Args:
        input_aggregate_analysis_taxa_error (pd.DataFrame): analysis taxa with error.
        caplog (LogCaptureFixture): the log message and level.
    """
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        benthos_data.aggregate_analysis_taxa(input_aggregate_analysis_taxa_error)
    assert pytest_wrapped_e.type == SystemExit
    expected_loglevel = "CRITICAL"
    expected_message = "In de volgende monsters is Analyse_taxonnaam niet uniek:"
    assert caplog.text.find(expected_loglevel) != -1
    assert caplog.text.find(expected_message) != -1


def test_sample_device_to_column(
    input_sample_device_to_column: pd.DataFrame,
    output_sample_device_to_column: pd.DataFrame,
) -> None:
    """Tests converting the sampling device to a column.

    Args:
        input_sample_device_to_column (pd.DataFrame): Fixture with sampling devices as rows.
        output_sample_device_to_column (pd.DataFrame): Fixture with expected output with devices in column.
    """
    result = benthos_data.sample_device_to_column(input_sample_device_to_column)
    pd.testing.assert_frame_equal(
        result.reset_index(drop=True),
        output_sample_device_to_column.reset_index(drop=True),
    )


def test_support_to_column(
    input_support_to_column: pd.DataFrame, output_support_to_column: pd.DataFrame
) -> None:
    """Tests writing the support unit to a column.

    Args:
        input_support_to_column (pd.DataFrame): Fixture with support as rows.
        output_support_to_column (pd.DataFrame): Fixture with expected output with support as column.
    """
    result = benthos_data.support_to_column(input_support_to_column)
    pd.testing.assert_frame_equal(
        result.reset_index(drop=True), output_support_to_column.reset_index(drop=True)
    )


def test_add_location_data(
    input_add_location_data: pd.DataFrame,
    output_add_location_data: pd.DataFrame,
    location_data: pd.DataFrame = pd.DataFrame(
        {
            "Meetobject_Code": ["NRDZE_0001", "NRDZE_0001", "NRDZE_0001"],
            "Project_Code": ["MWTL_MZB_Boxcorer", "MWTL_MZB", "MWTL_MZB_Schaaf"],
            "Methode": ["BOXCRR", "BOXCRR", "BODSF"],
            "Waterlichaam": ["Noordzee", "Noordzee", "Noordzee"],
            "Strata": [np.nan] * 3,
            "Gebied": [np.nan] * 3,
            "BISI_gebied": [np.nan] * 3,
            "BISI_deelgebied": [np.nan] * 3,
            "BISI_Eunis": [np.nan] * 3,
            "BISI_Eunis_asev": [np.nan] * 3,
            "BISI_Habitat": [np.nan] * 3,
            "Margalef": [np.nan] * 3,
            "Gebruik": [np.nan] * 3,
        }
    ),
) -> None:
    """Tests adding the location data to the benthos data.

    Args:
        input_add_location_data (pd.DataFrame): Fixture with input benthos data.
        output_add_location_data (pd.DataFrame): Fixture with location data added as expected.
        location_data (pd.DataFrame): the location data as configuration with a default pd.DataFrame.
    """

    # convert all columns to object to avoid errors
    location_data = location_data.astype(object)

    result = benthos_data.add_location_data(input_add_location_data, location_data)
    pd.testing.assert_frame_equal(
        result.reset_index(drop=True), output_add_location_data.reset_index(drop=True)
    )


def test_add_waterbody_data(
    input_add_waterbody_data: pd.DataFrame, output_add_waterbody_data: pd.DataFrame
) -> None:
    """Tests adding the waterbody data from the configuration.

    Args:
        input_add_waterbody_data (pd.DataFrame): Fixture with input benthos data.
        output_add_waterbody_data (pd.DataFrame):  Fixture with waterbody data added as expected.
    """
    waterbody_data = read_system_config.read_waterbodies_config(
        ["Noordzee-overig", "Waddenzee"]
    )

    result = benthos_data.add_waterbody_data(input_add_waterbody_data, waterbody_data)
    pd.testing.assert_frame_equal(
        result.reset_index(drop=True), output_add_waterbody_data.reset_index(drop=True)
    )


def test_add_waterbody_data_invalid(input_add_waterbody_data: pd.DataFrame) -> None:
    """Tests the error when adding the waterbody data which is invalid.

    Args:
        input_add_waterbody_data (pd.DataFrame): Fixture with input benthos data.
    """
    waterbody_data = pd.DataFrame(
        {
            "Waterlichaam": ["Noordzee", "Waddenzee", "Waddenzee"],
            "Heeft_Seizoen": [True, True, True],
            "Trendgroep": ["marien", "marien", "zoet"],
            "Determinatie_protocol": ["zout", "zout", "zoet"],
            "Biomassa_protocol": ["zout", "zout", "zoet"],
            "Startjaar": [1970, 1980, 1979],
            "Min_trend_monsters": [3, 3, 3],
        }
    )

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        benthos_data.add_waterbody_data(input_add_waterbody_data, waterbody_data)
        assert pytest_wrapped_e.type == SystemExit


def test_taxa_quantities_to_columns(
    input_taxa_quantities_to_columns: pd.DataFrame,
    output_taxa_quantities_to_columns: pd.DataFrame,
) -> None:
    """Tests converting taxa quantities to columns.

    Args:
        input_taxa_quantities_to_columns (pd.DataFrame): Fixture with input data with taxa quantities.
        output_taxa_quantities_to_columns (pd.DataFrame): Fixture with expected quantities in columns.
    """
    result = benthos_data.taxa_quantities_to_columns(input_taxa_quantities_to_columns)
    pd.testing.assert_frame_equal(result, output_taxa_quantities_to_columns)


def test_filter_waterbodies(
    input_filter_waterbodies: pd.DataFrame, output_filter_waterbodies: pd.DataFrame
) -> None:
    """Tests filtering waterbodies in the data.

    Args:
        input_filter_waterbodies (pd.DataFrame): Fixture with the input data.
        output_filter_waterbodies (pd.DataFrame): Fixture with the expected filtered data.
    """
    result = benthos_data.filter_waterbodies(input_filter_waterbodies, ["Noordzee"])
    pd.testing.assert_frame_equal(
        result.reset_index(drop=True), output_filter_waterbodies.reset_index(drop=True)
    )


def test_usage_based_on_samples(
    input_usage_samples: pd.DataFrame, output_usage_samples: pd.DataFrame
) -> None:
    """Tests usage based on sample numbers.

    Args:
        input_usage_samples (pd.DataFrame): Fixture with the samples as input.
        output_usage_samples (pd.DataFrame): Fixture with the expected usage added.
    """
    result = benthos_data.usage_based_on_samples(input_usage_samples)
    pd.testing.assert_frame_equal(
        result.reset_index(drop=True), output_usage_samples.reset_index(drop=True)
    )


def test_extract_ecotoop_code_empty(
    input_extract_ecotoop_code_empty: pd.DataFrame,
    output_extract_ecotoop_code_empty: pd.DataFrame,
) -> None:
    """Test the extraction of ecotoop codes from the Ecotoop_Codes column when the column is empty.

    Args:
        input_extract_ecotoop_code_empty (pd.DataFrame): input dataframe with no ecotoop defined.
        output_extract_ecotoop_code_empty (pd.DataFrame): expected output dataframe.
    """

    result_df = benthos_data.extract_ecotoop_code(
        input_extract_ecotoop_code_empty, "ZES.1"
    )
    pd.testing.assert_frame_equal(result_df, output_extract_ecotoop_code_empty)


def test_extract_ecotoop_code(
    input_extract_ecotoop_code: pd.DataFrame, output_extract_ecotoop_code: pd.DataFrame
) -> None:
    """Test the extraction of ecotoop codes from the Ecotoop_Codes column.

    Args:
        input_extract_ecotoop_code (pd.DataFrame): input dataframe with a single ecotoop given.
        output_extract_ecotoop_code (pd.DataFrame): expected output dataframe.
    """

    result_df = benthos_data.extract_ecotoop_code(input_extract_ecotoop_code, "ZES.1")
    pd.testing.assert_frame_equal(result_df, output_extract_ecotoop_code)


def test_extract_ecotoop_code_mixed(
    input_extract_ecotoop_code_mixed: pd.DataFrame,
    output_extract_ecotoop_code_mixed: pd.DataFrame,
) -> None:
    """Test the extraction of ecotoop codes from the Ecotoop_Codes column when multiple ecotoops are defined.

    Args:
        input_extract_ecotoop_code_mixed (pd.DataFrame): input dataframe with multiple ecotoops defined.
        output_extract_ecotoop_code_mixed (pd.DataFrame): expected output dataframe.
    """

    result = benthos_data.extract_ecotoop_code(
        input_extract_ecotoop_code_mixed, "ZES.1"
    )
    result = benthos_data.extract_ecotoop_code(result, "EUNIS")

    # fill NaN with empty string, for comparison
    result = result.fillna("")
    expected = output_extract_ecotoop_code_mixed.fillna("")

    pd.testing.assert_frame_equal(result, expected)


def test_extract_ecotoop_code_multi(
    input_extract_ecotoop_code_multi: pd.DataFrame,
    output_extract_ecotoop_code_multi: pd.DataFrame,
) -> None:
    """Test the extraction of ecotoop codes from the Ecotoop_Codes column when more then 2 ecotoops are defined.

    Args:
        input_extract_ecotoop_code_multi (pd.DataFrame): input dataframe with multiple ecotoops defined.
        output_extract_ecotoop_code_multi (pd.DataFrame): expected output dataframe.
    """

    result = benthos_data.extract_ecotoop_code(
        input_extract_ecotoop_code_multi, "ZES.1"
    )
    result = benthos_data.extract_ecotoop_code(result, "EUNIS")

    # fill NaN with empty string, for comparison
    result = result.fillna("")
    expected = output_extract_ecotoop_code_multi.fillna("")

    pd.testing.assert_frame_equal(result, expected)


def test_benthos_main(
    input_benthos_data_integration: pd.DataFrame,
    input_benthos_data_integration_location: pd.DataFrame,
    output_benthos_data_integration: pd.DataFrame,
    mocker: pytest_mock.MockerFixture,
) -> None:
    """Tests the integration of the benthos data preparation phase.

    Args:
        input_benthos_data_integration (pd.DataFrame): Fixture with the input for the preparation phase.
        input_benthos_data_integration_location (pd.DataFrame): Fixture with the input location data.
        output_benthos_data_integration (pd.DataFrame): Fixture with the expected output benthos data.
        mocker (pytest_mock.MockerFixture): return value of functions.
    """
    mocker.patch(
        "checks.check_config.check_empty_input_folder",
        return_value=False,
    )
    mocker.patch(
        "preparation.benthos_data.read_benthos_data",
        return_value=input_benthos_data_integration,
    )

    mocker.patch(
        "preparation.benthos_data.read_system_config.read_locations_config",
        return_value=input_benthos_data_integration_location,
    )

    mocker.patch(
        "preparation.read_user_config.read_required_waterbodies",
        return_value=["Veerse Meer"],
    )

    result = benthos_data.main_benthos_data()
    result = result.astype(object)
    output_benthos_data_integration = output_benthos_data_integration.astype(object)

    pd.testing.assert_frame_equal(
        result.reset_index(drop=True),
        output_benthos_data_integration.reset_index(drop=True),
    )
    assert isinstance(result, pd.DataFrame)
