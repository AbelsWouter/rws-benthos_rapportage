"""Tests the checks performed during the script."""

import logging

import numpy as np
import pandas as pd
import pytest
from pytest import LogCaptureFixture
from pytest_lazyfixture import lazy_fixture

from checks import check_data


logger = logging.getLogger(__name__)


def test_check_rows_have_data(benthos_req_col: pd.DataFrame) -> None:
    """Tests whether the dataframe contains rows of data as expected.

    Args:
        benthos_req_col (pd.DataFrame): the dataframe to be checked whether it contains rows of data.
    """
    actual_boolean = check_data.check_rows_have_data(benthos_req_col)
    assert actual_boolean is True


def test_check_missing_values() -> None:
    """Checks whether the columns with NA are in the expected columns.

    Args:
        df (pd.DataFrame): The dataframe to be checked for columns with NA.
        check_columns (list[str:]): the expected columns not to be nan.
    """

    df = pd.DataFrame(
        {"Collectie_Referentie": [1, 1, 1, 3, 4], "Taxa": ["v", "v", "x", "y", "z"]}
    )
    check_columns: list = ["Collectie_Referentie", "Taxa"]
    source_name: str = "Aquadesk"
    expected: bool = False

    result = check_data.check_missing_values(df, check_columns, source_name)
    assert result is expected


def test_check_missing_values_error(caplog: LogCaptureFixture) -> None:
    """Checks whether the columns with NA are in the expected columns.

    Args:
        df (pd.DataFrame): The dataframe to be checked for columns with NA.
        check_columns (list[str:]): the expected columns not to be nan.
    """
    df = pd.DataFrame(
        {
            "Collectie_Referentie": [1, np.nan, 1, 3, 4],
            "Taxa": ["v", "v", "x", pd.NA, "z"],
        }
    )
    check_columns: list = ["Collectie_Referentie", "Taxa"]
    source_name: str = "Aquadesk"
    log_message: str = "De kolommen ['Collectie_Referentie', 'Taxa'] in \
          de Aquadesk data mogen geen missende waarden hebben."

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        check_data.check_missing_values(df, check_columns, source_name)
        assert log_message in caplog.text
        assert pytest_wrapped_e.type == SystemExit


def test_check_required_col(
    benthos_read_df: pd.DataFrame, req_columns_script: pd.Series
) -> None:
    """Tests the checking of required column presence.

    Args:
        benthos_read_df (pd.DataFrame): the DataFrame to be checked.
        req_columns_script (pd.Series): the list of expected required column names from the function.
    """
    boolean_check_col = check_data.check_required_col(
        benthos_read_df, req_columns_script
    )
    assert boolean_check_col is True


def test_check_unique_distinct() -> None:
    """Tests checking whether there are only unique records."""
    data = pd.DataFrame(
        {
            "veld1": [1, 1, 1, 2, 2],
            "veld2": ["A", "A", "A", "B", "B"],
            "veld3": [1, 1, 1, 1, 1],
        }
    )
    is_unique = check_data.check_unique_distinct(
        data, ["veld1", "veld2", "veld3"], "veld1", "test"
    )
    assert is_unique


def test_check_unique_distinct_invalid() -> None:
    """Tests checking whether there are only unique records with invalid data to produce error."""
    invalid_data = pd.DataFrame(
        {
            "veld1": [1, 1, 1, 2, 2, 1],
            "veld2": ["A", "A", "A", "B", "B", "C"],
            "veld3": [1, 1, 1, 1, 1, 1],
        }
    )
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        check_data.check_unique_distinct(
            invalid_data, ["veld1", "veld2", "veld3"], "veld1", "test"
        )
        assert pytest_wrapped_e.type == SystemExit


def test_check_unique_sample_codes() -> None:
    """Tests for checking unique samples by masking check_unique_distinct."""
    data = pd.DataFrame(
        {
            "Collectie_Referentie": [1, 1, 1, 2, 2],
            "Collectie_DatumTijd": [
                "1999-04-29 05:15:00",
                "1999-04-29 05:15:00",
                "1999-04-29 05:15:00",
                "1999-04-29 05:15:00",
                "1999-04-29 05:15:00",
            ],
            "Meetobject_Code": ["A", "A", "A", "B", "B"],
            "Other Field": [1, 1, 1, 1, 1],
        }
    )
    check_data.check_unique_distinct(
        data,
        ["Collectie_Referentie", "Collectie_DatumTijd", "Meetobject_Code"],
        "Collectie_Referentie",
        "test",
    )


def test_check_unique_sample_codes_invalid() -> None:
    """Tests the error for checking unique samples by masking check_unique_distinct."""
    invalid_data = pd.DataFrame(
        {
            "Collectie_Referentie": [1, 1, 1, 2, 2, 1],
            "Collectie_DatumTijd": [
                "1999-04-29 05:15:00",
                "1999-04-29 05:15:00",
                "1999-04-29 05:15:00",
                "1999-04-29 05:15:00",
                "1999-04-29 05:15:00",
                "1999-04-29 05:15:00",
            ],
            "Meetobject_Code": ["A", "A", "A", "B", "B", "C"],
            "Other Field": [1, 1, 1, 1, 1, 1],
        }
    )
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        check_data.check_unique_distinct(
            invalid_data,
            ["Collectie_Referentie", "Collectie_DatumTijd", "Meetobject_Code"],
            "Collectie_Referentie",
            "Benthos",
        )
        assert pytest_wrapped_e.type == SystemExit


def test_check_unique_taxa(benthos_data_end: pd.DataFrame) -> None:
    """Tests whether there are only unique taxa at the end of preparing the data.

    Args:
        benthos_data_end (pd.DataFrame): Fixture with the data after preparation.
    """
    is_unique = check_data.check_uniqueness(
        benthos_data_end, ["Collectie_Referentie", "Analyse_taxonnaam"], "test"
    )
    assert is_unique


def test_check_unique_taxa_not_unique(benthos_data_end: pd.DataFrame) -> None:
    """Tests the error whether there are only unique taxa at the end of preparing the data.

    Args:
        benthos_data_end (pd.DataFrame): Fixture with the data after preparation.
    """
    invalid_row = pd.DataFrame(
        {"Collectie_Referentie": ["2015BS075"], "Analyse_taxonnaam": ["Echinocardium"]}
    )
    data = pd.concat([benthos_data_end, invalid_row])
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        check_data.check_unique_distinct(
            data,
            ["Collectie_Referentie", "Analyse_taxonnaam"],
            "Analyse_taxonnaam",
            "analysis data",
        )
        assert pytest_wrapped_e.type == SystemExit


@pytest.mark.parametrize(
    ("input_df ,col_list, source_name, expected"),
    [
        (  # three samples unique
            pd.DataFrame(
                {
                    "Taxa": ["a", "x", "y", "b", "a"],
                    "Collectie_Referentie": [1, 1, 1, 3, 4],
                    "Extra": ["v", "v", "x", "y", "z"],
                }
            ),
            ["Taxa", "Collectie_Referentie"],
            "Aquadesk",
            True,
        ),
        (  # one sample a year unique
            pd.DataFrame(
                {
                    "Taxa": ["a", "b", "c", "d", "a"],
                    "Collectie_Referentie": [1, 1, 2, 2, 2],
                    "Year": ["v", "v", "x", "x", "x"],
                }
            ),
            ["Taxa", "Collectie_Referentie", "Year"],
            "Aquadesk",
            True,
        ),
        (  # one sample unique
            pd.DataFrame(
                {
                    "Taxa": ["a", "b", "c", "d", "e"],
                    "Collectie_Referentie": [1, 1, 1, 1, 1],
                    "Extra": ["v", "v", "x", "y", "z"],
                }
            ),
            ["Taxa", "Collectie_Referentie"],
            "Aquadesk",
            True,
        ),
    ],
)
def test_check_uniqueness(
    input_df: pd.DataFrame,
    col_list: list[str],
    source_name: str,
    expected: bool,
) -> None:
    """Tests whether the taxa are unique after aggregation.

    Args:
        input_df (pd.DataFrame): the dataframe as input for checking.
        col_list (list): the columns which should be aggregated on.
        return_col (str): the column to return for unique taxa.
        expected (bool]): the expected bool
    """
    unique = check_data.check_uniqueness(input_df, col_list, source_name)
    assert unique == expected


@pytest.mark.parametrize(
    ("input_df ,col_list, source_name, log_message"),
    [
        (  # three samples, not unique
            pd.DataFrame(
                {
                    "Taxa": ["a", "a", "a", "b", "a"],
                    "Collectie_Referentie": [1, 1, 1, 3, 4],
                    "Extra": ["v", "v", "x", "y", "z"],
                }
            ),
            ["Taxa", "Collectie_Referentie"],
            "Aquadesk",
            "De combinatie van kolommen ['Taxa', 'Collectie_Referentie'] in de Aquadesk data is 3x niet uniek voor:",
        ),
        (  # one sample not unique
            pd.DataFrame(
                {
                    "Taxa": ["a", "a", "a", "b", "b"],
                    "Collectie_Referentie": [1, 1, 1, 1, 1],
                    "Extra": ["v", "v", "x", "y", "z"],
                }
            ),
            ["Taxa", "Collectie_Referentie"],
            "Aquadesk",
            "De combinatie van kolommen ['Taxa', 'Collectie_Referentie'] in de Aquadesk data is 5x niet uniek voor:",
        ),
    ],
)
def test_check_uniqueness_error(
    input_df: pd.DataFrame,
    col_list: list[str],
    source_name: str,
    log_message: str,
    caplog: LogCaptureFixture,
) -> None:
    """Tests whether an error is generated when the taxa are not unique after aggregation.

    Args:
        input_df (pd.DataFrame): the dataframe as input for checking.
        col_list (list): the columns which should be aggregated on.
        return_col (str): the column to return for unique taxa.
        expected (bool]): the expected bool
    """

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        check_data.check_uniqueness(input_df, col_list, source_name)
        assert pytest_wrapped_e.type == SystemExit
        assert log_message in caplog.text


def test_check_has_taxa(input_check_has_taxa: pd.DataFrame) -> None:
    """Tests checking if the dataframe contains counted taxa.

    Args:
        input_check_has_taxa (pd.DataFrame): Fixture with the input taxa for checking.
    """
    result = check_data.check_has_taxa(input_check_has_taxa)
    assert result["Collectie_Referentie"].unique().tolist() == ["monster 1"]
    assert isinstance(result, pd.DataFrame)


def test_required_column_names(
    input_required_columns_analyse: pd.DataFrame, req_analysis_names: pd.Series
) -> None:
    """Tests whether the required columns names are present.

    Args:
        input_required_columns_analyse (pd.DataFrame): Fixture with required columns present.
        req_analysis_names (pd.Series): Fixture with the required analysis names from the configuration.
    """
    result = check_data.check_required_col(
        input_required_columns_analyse, req_analysis_names
    )
    assert result is True


@pytest.mark.parametrize(
    ("df_input, expected_req_col_names"),
    [
        (
            lazy_fixture("input_required_columns_script"),
            lazy_fixture("req_columns_script"),
        ),
        (
            lazy_fixture("input_required_columns_analyse"),
            lazy_fixture("req_analysis_names"),
        ),
    ],
)
def test_required_column_names_false(
    df_input: pd.DataFrame,
    expected_req_col_names: pd.Series,
    caplog: LogCaptureFixture,
) -> None:
    """Tests producing an error with invalid required columns names.

    Args:
        df_input (pd.DataFrame): Fixture with the input benthos data.
        expected_req_col_names (pd.Series): Fixture with the expected required columns names.
        caplog (LogCaptureFixture): Access and control log capturing.
    """
    input_df = df_input.drop(columns=["Collectie_DatumTijd"])

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        check_data.check_required_col(input_df, expected_req_col_names)
        assert pytest_wrapped_e.type == SystemExit

    expected_loglevel = "ERROR"
    expected_message = "De volgende kolommen zijn niet aangetroffen in de data"
    assert caplog.text.find(expected_loglevel) != -1
    assert caplog.text.find(expected_message) != -1


def test_round_numeric_columns() -> None:
    """Tests rouding the numbers in the dataframe to the required number of decimals."""
    input_df = pd.DataFrame(
        {
            "Aantal": [1.1234567890, 1.1234567890, 1.1234567890, 2.123456, 2],
            "nm2_Soort_Stratum": [
                1.123456789,
                1.123456789,
                1.123456789,
                2.123456789,
                2.123456789,
            ],
        }
    )
    expected = pd.DataFrame(
        {
            "Aantal": [1.12345678, 1.12345678, 1.12345678, 2.123456, 2],
            "nm2_Soort_Stratum": [
                1.12345678,
                1.12345678,
                1.12345678,
                2.12345678,
                2.12345678,
            ],
        }
    )

    result = check_data.round_numeric_columns(input_df)
    pd.testing.assert_frame_equal(result, expected)


def test_remove_negative_measurements() -> None:
    """Tests removing negative numbers from a columns."""
    input_df = pd.DataFrame({"Aantal": [12, 12, 12, 2, -2]})
    expected = pd.DataFrame({"Aantal": [12, 12, 12, 2]})
    result = check_data.remove_negative_measurements(input_df, "Aantal")
    pd.testing.assert_frame_equal(result, expected)


@pytest.fixture
def single_sheet_excel(tmp_path: str) -> str:
    """Fixture for a single sheet excel file."""
    file_path = tmp_path / "single_sheet.xlsx"
    df = pd.DataFrame({"data": [1, 2, 3]})
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def multi_sheet_excel(tmp_path: str) -> str:
    """Fixture for a multi sheet excel file."""
    file_path = tmp_path / "multi_sheet.xlsx"
    df1 = pd.DataFrame({"data": [1, 2, 3]})
    df2 = pd.DataFrame({"data": [4, 5, 6]})

    # pylint: disable=abstract-class-instantiated
    with pd.ExcelWriter(file_path) as writer:
        df1.to_excel(writer, sheet_name="Fruits", index=False)
        df2.to_excel(writer, sheet_name="Vegetables", index=False)

    return file_path


def test_single_sheet_excel(single_sheet_excel: str, caplog: LogCaptureFixture) -> None:
    """Tests the check for a single sheet excel."""
    result = check_data.check_number_of_excelsheets(single_sheet_excel)
    assert result
    assert "De aangeboden excel bevat meerdere werkbladen." not in caplog.text


def test_multi_sheet_excel(multi_sheet_excel: str, caplog: LogCaptureFixture) -> None:
    """Tests the check for a multi sheet excel."""
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        check_data.check_number_of_excelsheets(multi_sheet_excel)
        assert pytest_wrapped_e.type == SystemExit
    assert "De aangeboden excel bevat meerdere werkbladen." in caplog.text


def test_nonexistent_file(caplog: LogCaptureFixture) -> None:
    """Tests the check for a nonexistent file."""
    nonexistent_file_path = "nonexistent_file.xlsx"
    check_data.check_number_of_excelsheets(nonexistent_file_path)
    assert (
        f"An unexpected error occurred: [Errno 2] No such file or directory: '{nonexistent_file_path}'"
        in caplog.text
    )
