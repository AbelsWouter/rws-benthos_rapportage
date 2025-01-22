"""Tests the aquadesk download and remove file."""

import os

import pytest_mock

from preparation import aquadesk
from preparation import ddecoapi_data_parser
from preparation import read_system_config


def test_aquadesk_result_to_excel(mocker: pytest_mock.MockerFixture) -> None:
    """Tests whether the aquadesk downloads and the download is present.

    Args:
        mocker (pytest_mock.MockerFixture): the ddecoapi from the dataparser.
    """
    ddecoapi = ddecoapi_data_parser.dataparser(
        aquadesk_url="https://ddecoapi.aquadesk.nl/v2/",
        api_key=read_system_config.read_yaml_configuration("api_key", "aquadesk.yaml"),
        query_url="measurements",
        query_filter='organisation:eq:"RWS";',
        skip_properties="""
            changedate,measuredunit,
            measuredvalue,measurementdate,
            measurementpurpose,organisation,
            samplingcontext,status,
            measurementsetnumber,externalkey,
            id,sourcesystem,
            taxontypetaxongroup,organisationnumericcode,
            suppliernumericcode,measurementgeography.coordinates,
            measurementgeography.type,measurementgeography.srid,
            samplingdevicecodes""",
        page_size=1000,
    )

    mocker.patch("preparation.aquadesk.build_request", return_value=ddecoapi)

    assert aquadesk.aquadesk_download(["MWTL_MACEV"], ["BNMWD_0001"]) == True
    assert os.path.isfile("./input/aquadesk_download.xlsx")


def test_remove_file() -> None:
    """Tests whether the input file and path is removed."""
    assert os.path.exists("./input/testing") is False
    with open("./input/testing", "w") as fp:
        assert os.path.exists("./input/testing") is True
    aquadesk.remove_file("./input/testing")
    assert os.path.exists("./input/testing") is False
