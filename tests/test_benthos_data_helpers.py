"""Tests the additional function to the benthos data script."""

import pytest_mock

from preparation import benthos_data_helpers


def test_split_query_filter_to_dictionary(mocker: pytest_mock.MockerFixture) -> None:
    """Tests a yaml configuration splitting to a dictionary.

    Args:
        mocker (pytest_mock.MockerFixture): the return value of read_yaml_configuration
    """
    yaml = """organisation:eq:"RWS";
              collectiondate:ge:"1999-01-01";
              measurementpackage:in:["ME.KG","ME.AB","ME.MS"];
              quantity:in:["VOLME","OPPVTE","BEMSRAPRT","SUBSMTRAL","AANTL","MASSA"];"""
    mocker.patch(
        "preparation.read_system_config.read_yaml_configuration", return_value=yaml
    )
    expected = {
        "organisation": ["RWS"],
        "collectiondate": ["1999-01-01"],
        "measurementpackage": ["ME.KG", "ME.AB", "ME.MS"],
        "quantity": ["VOLME", "OPPVTE", "BEMSRAPRT", "SUBSMTRAL", "AANTL", "MASSA"],
    }

    result = benthos_data_helpers.split_query_filter_to_dictionary()
    assert result == expected


def test_rename_query_filter_columns() -> None:
    """Tests renaming the query filtering of columns."""
    query_filter_dict = {
        "organisation": ["RWS"],
        "collectiondate": ["1999-01-01"],
        "measurementpackage": ["ME.KG", "ME.AB", "ME.MS"],
        "quantity": ["VOLME", "OPPVTE", "BEMSRAPRT", "SUBSMTRAL", "AANTL", "MASSA"],
    }
    expected = {
        "organisation": ["RWS"],
        "Collectie_DatumTijd": ["1999-01-01"],
        "Meetpakket_Code": ["ME.KG", "ME.AB", "ME.MS"],
        "Grootheid_Code": [
            "VOLME",
            "OPPVTE",
            "BEMSRAPRT",
            "SUBSMTRAL",
            "AANTL",
            "MASSA",
        ],
    }
    result = benthos_data_helpers.rename_query_filter_columns(query_filter_dict)
    assert result == expected
