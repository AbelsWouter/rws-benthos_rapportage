"""Configuration file with fixtures used as input for the tests."""

import os
import shutil
from typing import Any
from typing import List

from numpy import int32
import pandas as pd
import pytest

from checks import check_config
from preparation import benthos_data
from preparation import read_system_config


# Assuming your output folder is named 'output_folder'
OUTPUT_FOLDER = "./output"

###########################################################################################
## SETUP / TEARDOWN #######################################################################
###########################################################################################


def clean_output_folder(path: str) -> None:
    """Cleans the output folder if it exists.

    Args:
        path (str): the path to the folder.
    """
    if os.path.exists(path):
        if os.path.exists(path):
            shutil.rmtree(path)

        os.makedirs(path)


@pytest.fixture(scope="function", autouse=False)
def empty_output_folder():
    """Fixture that cleans the output folder."""
    # Set up: Cleaning the output folder before the test
    output_folder_path = OUTPUT_FOLDER

    # Setup
    clean_output_folder(output_folder_path)

    yield

    # Teardown: Cleaning the output folder after the test
    clean_output_folder(output_folder_path)


def remove_folder(folder_path: str) -> None:
    """Removes a folder if it exists.

    Args:
        folder_path (str): The path to the folder.
    """
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)


###########################################################################################
## DEFAULTS ###############################################################################
###########################################################################################


@pytest.fixture()
def year_column_types() -> dict:
    """Fixture that gives a dict with the column data types.

    Returns:
        dict: dictionary with the column data types.
    """
    return {
        "Gebied": object,
        "Strata": object,
        "Waterlichaam": object,
        "Ecotoop_Codes": object,
        "Gebruik": object,
        "Meetobject_Code": object,
        "1999": float,
        "2000": float,
        "2001": float,
        "2002": float,
        "2003": float,
        "2004": float,
        "2005": float,
        "2006": float,
        "2007": float,
        "2008": float,
        "2009": float,
        "2010": float,
        "2011": float,
        "2012": float,
        "2013": float,
        "2014": float,
        "2015": float,
        "2016": float,
        "2017": float,
        "2018": float,
        "2019": float,
        "2020": float,
        "2021": float,
        "2022": float,
    }


@pytest.fixture
def filepath_global_var() -> Any:
    """Fixture that gives the path to the data.

    Returns:
        str: the path to the input data.
    """
    path = read_system_config.read_yaml_configuration(
        "data_path", "global_variables.yaml"
    )
    return path


@pytest.fixture
def filepath_data() -> Any:
    """Fixture that gives the path to the data as a check.

    Returns:
        str: the path to the input data.
    """
    path = check_config.read_system_config.read_yaml_configuration(
        "data_path", "global_variables.yaml"
    )
    return path


###########################################################################################
## TWN ####################################################################################
###########################################################################################


@pytest.fixture()
def twn() -> pd.DataFrame:
    """Fixture that provides the twn file.

    Returns:
        pd.DataFrame: the Pandas DataFrame with the twn downloaded.
    """
    df = pd.read_csv("./tests/fixtures/twn/twn.csv", sep=";")
    return df


@pytest.fixture()
def twn_corrected() -> pd.DataFrame:
    """
    Fixture that loads the 'twn_corrected.csv' file.

    Returns:
    pd.DataFrame: A pandas DataFrame containing the data from 'twn_corrected.csv'.
    """

    df = pd.read_csv("./tests/fixtures/twn/twn_corrected.csv", sep=";")
    return df


@pytest.fixture()
def valid_twn(twn: pd.DataFrame) -> pd.DataFrame:
    """
    Fixture that filters the 'twn' DataFrame to include only rows with 'Statuscode' 10 or 80.

    Args:
    twn (pd.DataFrame): The input DataFrame.

    Returns:
    pd.DataFrame: A filtered DataFrame containing only rows with 'Statuscode' 10 or 80.
    """

    return twn[twn["Statuscode"].isin([10, 80])]


@pytest.fixture()
def usefull_twn(twn_corrected: pd.DataFrame) -> pd.DataFrame:
    """
    Fixture that filters the 'twn_corrected' DataFrame based on specific conditions.

    Args:
    twn_corrected (pd.DataFrame): The input DataFrame.

    Returns:
    pd.DataFrame: A filtered DataFrame based on conditions related to 'Statuscode' and 'Synonymname'.
    """

    return twn_corrected[
        (twn_corrected["Statuscode"].isin([10, 80]))
        | (~twn_corrected["Synonymname"].isna())
    ]


@pytest.fixture()
def mapping_twn(valid_twn: pd.DataFrame) -> pd.DataFrame:
    """
    Fixture that selects specific columns from the 'valid_twn' DataFrame.

    Args:
    valid_twn (pd.DataFrame): The input DataFrame.

    Returns:
    pd.DataFrame: A DataFrame containing only the 'Name', 'Parentname', and 'Statuscode' columns.
    """

    return valid_twn[["Name", "Parentname", "Statuscode"]]


@pytest.fixture
def twn_mapping() -> pd.DataFrame:
    """
    Fixture that loads the 'twn_mapping.csv' file from the './tests/fixtures/twn/' directory.

    Returns:
    pd.DataFrame: A pandas DataFrame containing the data from 'twn_mapping.csv'.
    """

    df = pd.read_csv("./tests/fixtures/twn/twn_mapping.csv", sep=";")
    return df


@pytest.fixture
def habitat_species() -> pd.DataFrame:
    """
    Fixture that loads habitat species data from a CSV file specified in the system configuration.

    Returns:
    pd.DataFrame: A pandas DataFrame containing habitat species data.
    """

    habitat_species = read_system_config.read_csv_file(
        read_system_config.read_yaml_configuration(
            "config_hr_species", "global_variables.yaml"
        )
    )
    return habitat_species


###########################################################################################
## MAPPINGS ###############################################################################
###########################################################################################
# ------------------------------------------------------------------------------------------
# protocol_mapping


@pytest.fixture
def output_integration_protocol_mapping() -> pd.DataFrame:
    """
    Fixture that loads the 'output_integration_protocol_mapping.csv'.

    Returns:
    pd.DataFrame: A pandas DataFrame containing the data from 'output_integration_protocol_mapping.csv'.
    """
    df = pd.read_csv(
        "./tests/fixtures/protocol_mapping/output_integration_protocol_mapping.csv",
        sep=";",
    )
    return df


@pytest.fixture
def expected_aquadesk_mapped_columns() -> list[str]:
    """Fixtures that gives the expected Aquadesk columns.

    Returns:
        list[str]: the expected columns for aquadesk.
    """
    expected_columns = [
        "Parameter_Specificatie",
        "Determinatie_protocol",
        "Biomassa_protocol",
        "Zoutprotocol_biomassa",
        "Overrule_subspeciesname",
        "Hierarchie",
        "Order",
        "Combi",
        "Analyse_taxonnaam",
        "IsPresentie_Protocol",
    ]
    return expected_columns


# ------------------------------------------------------------------------------------------
# taxa_mapping


@pytest.fixture
def output_integration_taxa_mapping() -> pd.DataFrame:
    """
    Fixture with expected output for the integration of the taxa mapping.

    Returns:
    pd.DataFrame: A pandas DataFrame containing the data from 'output_integration_taxa_mapping.csv'.
    """
    df = pd.read_csv(
        "./tests/fixtures/taxa_mapping/output_integration_taxa_mapping.csv", sep=";"
    )
    return df


@pytest.fixture
def twn_taxonomy() -> pd.DataFrame:
    """
    Fixture that loads the 'twn_taxonomy.csv' file.

    Returns:
    pd.DataFrame: A pandas DataFrame containing the taxonomy data from 'twn_taxonomy.csv'.
    """
    df = pd.read_csv("./tests/fixtures/taxa_mapping/twn_taxonomy.csv", sep=";")
    return df


@pytest.fixture
def twn_recoded_subspecies() -> pd.DataFrame:
    """
    Fixture that loads the 'twn_recoded_subspecies.csv' file.

    Returns:
    pd.DataFrame: A pandas DataFrame containing recoded subspecies data from 'twn_recoded_subspecies.csv'.
    """
    df = pd.read_csv(
        "./tests/fixtures/taxa_mapping/twn_recoded_subspecies.csv", sep=";"
    )
    return df


@pytest.fixture
def output_glue_hierarchie() -> pd.DataFrame:
    """
    Fixture with expected output for glueing the hierarchie

    Returns:
    pd.DataFrame: A pandas DataFrame containing data from 'output_glue_hierarchie.csv'.
    """
    df = pd.read_csv(
        "./tests/fixtures/taxa_mapping/output_glue_hierarchie.csv", sep=";"
    )
    return df


@pytest.fixture
def input_split_combined_taxa() -> pd.DataFrame:
    """
    Fixture that loads the 'input_split_combined_taxa.csv' file.

    Returns:
    pd.DataFrame: A pandas DataFrame containing input data from 'input_split_combined_taxa.csv'.
    """
    df = pd.read_csv(
        "./tests/fixtures/taxa_mapping/input_split_combined_taxa.csv", sep=";"
    )
    return df


@pytest.fixture
def output_split_speciescombi() -> pd.DataFrame:
    """
    Fixture that loads the 'output_split_speciescombi.csv' file.

    Returns:
    pd.DataFrame: A pandas DataFrame containing output data from 'output_split_speciescombi.csv'.
    """
    df = pd.read_csv(
        "./tests/fixtures/taxa_mapping/output_split_speciescombi.csv", sep=";"
    )
    return df


@pytest.fixture
def output_split_genuscombi() -> pd.DataFrame:
    """
    Fixture that loads the 'output_split_genuscombi.csv' file.

    Returns:
    pd.DataFrame: A pandas DataFrame containing output data from 'output_split_genuscombi.csv'.
    """
    df = pd.read_csv(
        "./tests/fixtures/taxa_mapping/output_split_genuscombi.csv", sep=";"
    )
    return df


# ------------------------------------------------------------------------------------------
## add mapping


@pytest.fixture
def input_integration_add_mapping() -> pd.DataFrame:
    """
    Fixture that loads the 'input_integration_add_mapping.csv' file.

    Returns:
    pd.DataFrame: A pandas DataFrame containing output data from 'input_integration_add_mapping.csv'.
    """
    df = pd.read_csv(
        "./tests/fixtures/add_mapping/input_integration_add_mapping.csv", sep=";"
    )
    return df


@pytest.fixture
def output_integration_add_mapping() -> pd.DataFrame:
    """
    Fixture that loads the 'output_integration_add_mapping.csv' file.

    Returns:
    pd.DataFrame: A pandas DataFrame containing output data from 'output_integration_add_mapping.csv'.
    """
    df = pd.read_csv(
        "./tests/fixtures/add_mapping/output_integration_add_mapping.csv", sep=";"
    )
    return df


@pytest.fixture
def input_add_valid_taxonnames() -> pd.DataFrame:
    """
    Fixture that loads the 'input_add_vaild_taxonnames.csv' file.

    Returns:
    pd.DataFrame: A pandas DataFrame containing output data from 'input_add_vaild_taxonnames.csv'.
    """
    df = pd.read_csv(
        "./tests/fixtures/add_mapping/input_add_vaild_taxonnames.csv", sep=";"
    )
    return df


@pytest.fixture
def input_add_protocol() -> pd.DataFrame:
    """
    Fixture that loads the 'input_add_protocol.csv' file.

    Returns:
    pd.DataFrame: A pandas DataFrame containing output data from 'input_add_protocol.csv'.
    """
    df = pd.read_csv("./tests/fixtures/add_mapping/input_add_protocol.csv", sep=";")
    return df


@pytest.fixture
def input_add_taxa() -> pd.DataFrame:
    """
    Fixture that loads the 'input_add_taxa.csv' file.

    Returns:
    pd.DataFrame: A pandas DataFrame containing output data from 'input_add_taxa.csv'.
    """
    df = pd.read_csv("./tests/fixtures/add_mapping/input_add_taxa.csv", sep=";")
    return df


@pytest.fixture
def input_add_twn() -> pd.DataFrame:
    """
    Fixture that loads the 'input_add_twn.csv' file.

    Returns:
    pd.DataFrame: A pandas DataFrame containing output data from 'input_add_twn.csv'.
    """
    df = pd.read_csv("./tests/fixtures/add_mapping/input_add_twn.csv", sep=";")
    return df


@pytest.fixture
def output_add_twn() -> pd.DataFrame:
    """
    Fixture that loads the 'output_add_twn.csv' file.

    Returns:
    pd.DataFrame: A pandas DataFrame containing output data from 'output_add_twn.csv'.
    """
    df = pd.read_csv("./tests/fixtures/add_mapping/output_add_twn.csv", sep=";")
    return df


@pytest.fixture
def input_add_groups() -> pd.DataFrame:
    """
    Fixture that loads the 'input_add_groups.csv' file.

    Returns:
    pd.DataFrame: A pandas DataFrame containing output data from 'input_add_groups.csv'.
    """
    df = pd.read_csv("./tests/fixtures/add_mapping/input_add_groups.csv", sep=";")
    return df


@pytest.fixture
def input_add_hierarchical_groups() -> pd.DataFrame:
    """
    Fixture that loads the 'input_add_hierarchical_groups.csv' file.

    Returns:
    pd.DataFrame: A pandas DataFrame containing output data from 'input_add_hierarchical_groups.csv'.
    """
    df = pd.read_csv(
        "./tests/fixtures/add_mapping/input_add_hierarchical_groups.csv", sep=";"
    )
    return df


@pytest.fixture
def input_add_twn_hierarchical_groups() -> pd.DataFrame:
    """
    Fixture that loads the 'input_add_twn_hierarchical_groups.csv' file.

    Returns:
    pd.DataFrame: A pandas DataFrame containing output data from 'input_add_twn_hierarchical_groups.csv'.
    """
    df = pd.read_csv(
        "./tests/fixtures/add_mapping/input_add_twn_hierarchical_groups.csv", sep=";"
    )
    return df


@pytest.fixture
def output_add_hierarchical_groups() -> pd.DataFrame:
    """
    Fixture that loads the 'output_add_hierarchical_groups.csv' file.

    Returns:
    pd.DataFrame: A pandas DataFrame containing output data from 'output_add_hierarchical_groups.csv'.
    """
    df = pd.read_csv(
        "./tests/fixtures/add_mapping/output_add_hierarchical_groups.csv", sep=";"
    )
    return df


###########################################################################################
## BENTHOS DATA ###########################################################################
###########################################################################################


@pytest.fixture
def req_columns_script() -> pd.Series:
    """Reads the script name columns from the data_model configuration file.

    Returns:
        pd.Series: the columns for the script.
    """
    req_columns = read_system_config.read_column_mapping()
    req_columns_script = req_columns["script_name"]
    return req_columns_script


@pytest.fixture
def benthos_read_df(filepath_data: str) -> pd.DataFrame:
    """Reads the benthos data.

    Args:
        filepath_data (str): the path to the benthos data.

    Returns:
        pd.DataFrame: the read benthos data.
    """
    df = benthos_data.read_benthos_data(filepath_data)
    return df


@pytest.fixture
def benthos_req_col(req_columns_script: pd.Series, filepath_data: str) -> pd.DataFrame:
    """Reads and filters the required columns of the benthos data.

    Args:
        req_columns_script (pd.Series): the required columns.
        filepath_data (str): the path to the benthos data.

    Returns:
        pd.DataFrame: the benthos data with the required columns.
    """
    df = benthos_data.read_benthos_data(filepath_data)
    benthos_req_col = benthos_data.get_required_columns(df, req_columns_script)
    return benthos_req_col


@pytest.fixture
def req_columns_not_null() -> pd.Series:
    """The required columns which should not be null.

    Returns:
        pd.Series: the required columns not be be null.
    """
    req_columns = read_system_config.read_column_mapping()
    req_columns_not_null = req_columns.loc[req_columns["not_null"]]["script_name"]
    return req_columns_not_null


@pytest.fixture
def req_analysis_names() -> pd.Series:
    """Reads the required analysis columns.

    Returns:
        pd.Series: the required analysis columns.
    """
    exp_col = read_system_config.read_analysis_names()
    exp_total_col = exp_col["analysis_name"]
    return exp_total_col


@pytest.fixture
def benthos_data_end() -> pd.DataFrame:
    """Reads the fixture with the output for the benthos data script.

    Returns:
        pd.DataFrame: the benthos data.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/benthos_data_end.csv", sep=";", decimal="."
    )
    return df


@pytest.fixture
def benthos_data_inbetween() -> pd.DataFrame:
    """The benthos data with the expected columns.

    Returns:
        pd.DataFrame: the benthos data with the expected columns before the file output.
    """
    df = pd.read_csv("./tests/fixtures/benthos_data/benthos_exp_columns.csv", sep=";")
    return df


@pytest.fixture
def input_aggregate_analysis_taxa() -> pd.DataFrame:
    """The input for the aggregation of the analysis taxa.

    Returns:
        pd.DataFrame: the data for aggregating the taxa.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/input_aggregate_analysis_taxa.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def output_aggregate_analysis_taxa() -> pd.DataFrame:
    """The output after aggregating the analysis taxa.

    Returns:
        pd.DataFrame: the aggregated analysis taxa.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/output_aggregate_analysis_taxa.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def input_aggregate_analysis_taxa_error() -> pd.DataFrame:
    """The input for testing the aggregation with error in it.

    Returns:
        pd.DataFrame: fixture with error in the input data.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/input_aggregate_analysis_taxa_error.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def input_sample_device_to_column() -> pd.DataFrame:
    """Input data for converting the device to column.

    Returns:
        pd.DataFrame: input with sample device as row.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/input_sample_device_to_column.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def output_sample_device_to_column() -> pd.DataFrame:
    """Fixture with expected output with sample device as column.

    Returns:
        pd.DataFrame: the sample device in columns.
    """
    dtype_mapping = {"Classificatie_Code": object}
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/output_sample_device_to_column.csv",
        sep=";",
        decimal=".",
        dtype=dtype_mapping,
    )
    return df


@pytest.fixture
def input_support_to_column() -> pd.DataFrame:
    """Reads the fixture for support to column.

    Returns:
        pd.DataFrame: the input for converting support to column.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/input_support_to_column.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def output_support_to_column() -> pd.DataFrame:
    """Fixture with expected output after converting the support (unit) to column.

    Returns:
        pd.DataFrame: expected output for the function support_to_column.
    """
    dtype_mapping = {"Classificatie_Code": object}
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/output_support_to_column.csv",
        sep=";",
        decimal=".",
        dtype=dtype_mapping,
    )
    return df


@pytest.fixture
def input_filter_required_rows() -> pd.DataFrame:
    """Input for testing filtering required row.

    Returns:
        pd.DataFrame: fixture with the input for filtering rows.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/input_filter_required_rows.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def output_filter_required_rows() -> pd.DataFrame:
    """Fixture with expected output for filtering required rows.

    Returns:
        pd.DataFrame: fixture with the output for the filtering required rows.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/output_filter_required_rows.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def input_add_location_data() -> pd.DataFrame:
    """Input for testing adding location to the data.

    Returns:
        pd.DataFrame: fixture with input for adding location data.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/input_add_location_data.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def output_add_location_data() -> pd.DataFrame:
    """Fixture with the expected output for adding locations.

    Returns:
        pd.DataFrame: expected output for adding locations.
    """
    dtype_mapping = {
        "Strata": object,
        "Gebied": object,
        "BISI_gebied": object,
        "BISI_deelgebied": object,
        "BISI_Eunis": object,
        "BISI_Eunis_asev": object,
        "BISI_Habitat": object,
        "Margalef": object,
        "Gebruik": object,
    }
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/output_add_location_data.csv",
        sep=";",
        decimal=".",
        dtype=dtype_mapping,
    )
    return df


@pytest.fixture
def input_add_waterbody_data() -> pd.DataFrame:
    """Input for tests adding waterbody data.

    Returns:
        pd.DataFrame: benthos data without waterbody data.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/input_add_waterbody_data.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def output_add_waterbody_data() -> pd.DataFrame:
    """Fixture with expected output for tests for adding waterbody data.

    Returns:
        pd.DataFrame: benthos data with waterbody data added.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/output_add_waterbody_data.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def input_filter_waterbodies() -> pd.DataFrame:
    """Input for tests of filtering waterbodies.

    Returns:
        pd.DataFrame: input for tests of filtering waterbodies.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/input_filter_waterbodies.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def output_filter_waterbodies() -> pd.DataFrame:
    """Fixture with expected output for filtering data.

    Returns:
        pd.DataFrame: filtered benthos data on waterbodies.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/output_filter_waterbodies.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def input_check_season() -> pd.DataFrame:
    """Input for testing checking the season.

    Returns:
        pd.DataFrame: benthos data as input for test checking seasons.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/input_check_season.csv", sep=";", decimal="."
    )
    return df


@pytest.fixture
def output_check_season() -> pd.DataFrame:
    """Fixture with expected output for checking the season.

    Returns:
        pd.DataFrame: the expected output for the check function.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/output_check_season.csv", sep=";", decimal="."
    )
    return df


@pytest.fixture
def input_check_season_no_spring() -> pd.DataFrame:
    """Input for testing check season without spring as season.

    Returns:
        pd.DataFrame: the input without spring as season.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/input_check_season_no_spring.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def output_check_season_no_spring() -> pd.DataFrame:
    """Fixture with expected output for check season without spring.

    Returns:
        pd.DataFrame: expected output for check without spring.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/output_check_season_no_spring.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def input_check_season_no_autumn() -> pd.DataFrame:
    """Input for testing checking season without autumn.

    Returns:
        pd.DataFrame: input of check without autumn.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/input_check_season_no_autumn.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def output_check_season_no_autumn() -> pd.DataFrame:
    """Fixture with expected output for check season without autumn.

    Returns:
        pd.DataFrame: expected output for check without autumn.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/output_check_season_no_autumn.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def input_aggregate_taxa() -> pd.DataFrame:
    """Fixture with the input for aggregating the taxa.

    Returns:
        pd.DataFrame: non-aggregated benthos taxa.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/input_aggregate_taxa.csv", sep=";", decimal="."
    )
    return df


@pytest.fixture
def output_aggregate_taxa() -> pd.DataFrame:
    """Fixture with expected output for aggregating taxa.

    Returns:
        pd.DataFrame: aggregated taxa.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/output_aggregate_taxa.csv", sep=";", decimal="."
    )
    return df


@pytest.fixture
def input_taxa_quantities_to_columns() -> pd.DataFrame:
    """Input for converting the quantities to columns.

    Returns:
        pd.DataFrame: benthos data with quantities in rows.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/input_taxa_quantities_to_columns.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def output_taxa_quantities_to_columns() -> pd.DataFrame:
    """Fixture with expected output for converting quantities to columns.

    Returns:
        pd.DataFrame: quantities of taxa in columns.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/output_taxa_quantities_to_columns.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def input_benthos_data_integration() -> pd.DataFrame:
    """Input of testing the integration of the benthos data script.

    Returns:
        pd.DataFrame: the input for the benthos data script.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/input_benthos_data_integration.csv", sep=";"
    )
    return df


@pytest.fixture
def input_benthos_data_integration_location() -> pd.DataFrame:
    """Fixture with expected output for reading locations in the integration test of the benthos data script.

    Returns:
        pd.DataFrame: the expected output out read_locations_config.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/input_benthos_data_integration_location.csv",
        sep=";",
    )
    return df


@pytest.fixture
def output_benthos_data_integration() -> pd.DataFrame:
    """Fixture with expected output for testing the integration of the benthos data script.

    Returns:
        pd.DataFrame: the expected output for the benthos data script.
    """
    dtype_mapping = {"Combi": object, "Monsterjaar": int32, "Monsterjaar_cluster": str}
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/output_benthos_data_integration.csv",
        sep=";",
        dtype=dtype_mapping,
    )
    return df


@pytest.fixture
def input_benthos_density() -> pd.DataFrame:
    """Fixture with input data for testing calculating the density.

    Returns:
        pd.DataFrame: input benthos data.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/input_benthos_density.csv",
        sep=";",
    )
    return df


@pytest.fixture
def output_benthos_density_aantal() -> pd.DataFrame:
    """Fixture with expected output for calculating the benthos data densities.

    Returns:
        pd.DataFrame: the calculated densities.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/output_benthos_density_aantal.csv",
        sep=";",
    )
    return df


@pytest.fixture
def output_benthos_density_massa() -> pd.DataFrame:
    """The output for calculating the density for mass.

    Returns:
        pd.DataFrame: the expected output for the test.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/output_benthos_density_massa.csv",
        sep=";",
    )
    return df


@pytest.fixture
def input_usage_samples() -> pd.DataFrame:
    """Fixture with the input data for usage based on the nr of samples.

    Returns:
        pd.DataFrame: the input for testing the usage.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/input_usage_samples.csv",
        sep=";",
    )
    return df


@pytest.fixture
def output_usage_samples() -> pd.DataFrame:
    """Fixture with expected output for testing the usage of samples.

    Returns:
        pd.DataFrame: expected output for testing the usage of samples.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/output_usage_samples.csv",
        sep=";",
    )
    return df


@pytest.fixture
def input_cluster_samples() -> pd.DataFrame:
    """Input for testing the clustering of sample years.

    Returns:
        pd.DataFrame: benthos data with samples from different years.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/input_cluster_sample_year.csv",
        sep=";",
    )
    return df


@pytest.fixture
def output_cluster_samples() -> pd.DataFrame:
    """Fixture with expected output for testing the clustering of sample years.

    Returns:
        pd.DataFrame: benthos data with samples clustered.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/output_cluster_sample_year.csv",
        sep=";",
        dtype={"Monsterjaar_cluster": str},
    )
    return df


@pytest.fixture
def input_add_group_color() -> pd.DataFrame:
    """Input for testing the clustering of sample years.

    Returns:
        pd.DataFrame: benthos data with samples from different years.
    """
    df = pd.read_csv("./tests/fixtures/benthos_data/input_add_group_color.csv", sep=";")
    return df


@pytest.fixture
def output_add_group_color() -> pd.DataFrame:
    """Fixture with expected output for testing the clustering of sample years.

    Returns:
        pd.DataFrame: benthos data with samples clustered.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/output_add_group_color.csv", sep=";"
    )
    return df


@pytest.fixture
def input_abundance_to_presence() -> pd.DataFrame:
    """Input for testing the abundance to presence.

    Returns:
        pd.DataFrame: benthos data with some abundance data and protocol info.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/input_abundance_to_presence.csv", sep=";"
    )
    return df


@pytest.fixture
def output_abundance_to_presence() -> pd.DataFrame:
    """Fixture with expected output for testing the abundance to presence logic.

    Returns:
        pd.DataFrame: benthos data with corrected presence.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/output_abundance_to_presence.csv", sep=";"
    )
    return df


@pytest.fixture
def input_presence_to_abundance() -> pd.DataFrame:
    """Input for testing the presence to abundance logic.
    The limit symbol and Azoisch should be taken in account

    Returns:
        pd.DataFrame: benthos data with some presence data and protocol info.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/input_presence_to_abundance.csv", sep=";"
    )
    return df


@pytest.fixture
def output_presence_to_abundance() -> pd.DataFrame:
    """Fixture with expected output testing the presence to abundance logic.

    Returns:
        pd.DataFrame: benthos data with corrected presence.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/output_presence_to_abundance.csv", sep=";"
    )
    return df


@pytest.fixture
def input_biomass_to_missing() -> pd.DataFrame:
    """Input for testing the biomass to missing value logic.

    Returns:
        pd.DataFrame: benthos data with biomass data and protocol info.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/input_biomass_to_missing.csv", sep=";"
    )
    return df


@pytest.fixture
def output_biomass_to_missing() -> pd.DataFrame:
    """Fixture with expected output for testing the biomass to missing value logic.

    Returns:
        pd.DataFrame: benthos data removed biomass values.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/output_biomass_to_missing.csv", sep=";"
    )
    return df


@pytest.fixture
def input_extract_ecotoop_code() -> pd.DataFrame:
    """Input for testing the extraction of ecotoop-codes.

    Returns:
        pd.DataFrame: benthos data with biomass data and protocol info.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/input_extract_ecotoop_code.csv", sep=";"
    )
    return df


@pytest.fixture
def output_extract_ecotoop_code() -> pd.DataFrame:
    """Fixture with expected output for testing the extraction of ecotoop-codes.

    Returns:
        pd.DataFrame: benthos data with biomass data and protocol info.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/output_extract_ecotoop_code.csv", sep=";"
    )
    return df


@pytest.fixture
def input_extract_ecotoop_code_empty() -> pd.DataFrame:
    """Input for testing the extraction of ecotoop-codes when column is empty.

    Returns:
        pd.DataFrame: benthos data with biomass data and protocol info.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/input_extract_ecotoop_code_empty.csv", sep=";"
    )
    return df


@pytest.fixture
def output_extract_ecotoop_code_empty() -> pd.DataFrame:
    """Fixture with expected output for testing the extraction of ecotoop-codes when column is empty.

    Returns:
        pd.DataFrame: benthos data with biomass data and protocol info.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/output_extract_ecotoop_code_empty.csv", sep=";"
    )
    return df


@pytest.fixture
def input_extract_ecotoop_code_mixed() -> pd.DataFrame:
    """Fixture with expected output for testing the extraction of ecotoop-codes when
    column is mixed with 2 different ecotoops.

    Returns:
        pd.DataFrame: benthos data with biomass data and protocol info.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/input_extract_ecotoop_code_mixed.csv", sep=";"
    )
    return df


@pytest.fixture
def output_extract_ecotoop_code_mixed() -> pd.DataFrame:
    """Fixture with expected output for testing the extraction of ecotoop-codes when
    column is mixed with 2 different ecotoops.

    Returns:
        pd.DataFrame: benthos data with biomass data and protocol info.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/output_extract_ecotoop_code_mixed.csv", sep=";"
    )
    return df


@pytest.fixture
def input_extract_ecotoop_code_multi() -> pd.DataFrame:
    """Input for testing the extraction of ecotoop-codes when more then 2 ecotoop codes are given.

    Returns:
        pd.DataFrame: benthos data with biomass data and protocol info.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/input_extract_ecotoop_code_multi.csv", sep=";"
    )
    return df


@pytest.fixture
def output_extract_ecotoop_code_multi() -> pd.DataFrame:
    """Fixture with expected output for testing the extraction of ecotoop-codes when
    more then 2 ecotoop codes are given.

    Returns:
        pd.DataFrame: benthos data with biomass data and protocol info.
    """
    df = pd.read_csv(
        "./tests/fixtures/benthos_data/output_extract_ecotoop_code_multi.csv", sep=";"
    )
    return df


###########################################################################################
## CHECKS #################################################################################
###########################################################################################


@pytest.fixture
def input_required_columns_script() -> pd.DataFrame:
    """Fixture with input for testing the required columns.

    Returns:
        pd.DataFrame: the required columns.
    """
    df = pd.DataFrame(
        columns=[
            "Collectie_Referentie",
            "Collectie_DatumTijd",
            "Meetobject_Code",
            "Meetpakket_Code",
            "Project_Code",
            "Verrichting_Methoden",
            "Compartiment_Code",
            "Grootheid_Code",
            "Parameter_Specificatie",
            "Limiet_Symbool",
            "Waarde_Berekend",
            "Eenheid_Berekend",
            "Classificatie_Code",
            "Ecotoop_Codes",
        ]
    )
    return df


@pytest.fixture
def input_required_columns_analyse() -> pd.DataFrame:
    """Fixture with input for the rquired columns for analysis.

    Returns:
        pd.DataFrame: the required analysis columns.
    """
    df = pd.DataFrame(
        columns=[
            "Collectie_DatumTijd",
            "Collectie_Referentie",
            "Meetobject_Code",
            "Bemonsteringsapp",
            "Support",
            "Support_Eenheid",
            "Determinatie_protocol",
            "Biomassa_protocol",
            "BISI_deelgebied",
            "BISI_Eunis",
            "BISI_Eunis_asev",
            "BISI_gebied",
            "BISI_Habitat",
            "Compartiment_Code",
            "Margalef",
            "Dichtheid_Aantal",
            "Dichtheid_Massa",
            "Gebied",
            "Strata",
            "Waterlichaam",
            "Ecotoop_Codes",
            "Ecotoop_ZES1",
            "Ecotoop_EUNIS",
            "Gebruik",
            "Trendgroep",
            "Min_trend_monsters",
            "Hierarchie",
            "Analyse_taxonnaam",
            "Groep",
            "Heeft_Seizoen",
            "Monsterjaar",
            "Seizoen",
            "Startjaar",
            "Aantal",
            "Massa",
            "Bedekking",
            "IsBiomassa_Protocol",
            "IsPresentie_Protocol",
            "IsSoort_Gebied",
            "IsSoort_Monster",
            "IsSoort_Waterlichaam",
            "nm2_Soort_Gebied",
            "nm2_Soort_Monster",
            "nm2_Soort_Waterlichaam",
            "Taxongroup_code",
            "Taxonrank",
            "Taxontype",
            "Statuscode",
            "Verrichting_Methoden",
            "Project_Code",
        ]
    )
    return df


@pytest.fixture
def input_check_has_taxa() -> pd.DataFrame:
    """Fixture with input for checking whether there are taxa.

    Returns:
        pd.DataFrame: input data with taxa.
    """
    df = pd.read_csv(
        "./tests/fixtures/checks/input_check_has_taxa.csv", sep=";", decimal="."
    )
    return df


###########################################################################################
## DIVERSITY ##############################################################################
###########################################################################################


@pytest.fixture
def diversity_levels() -> dict[str, List[str]]:
    """Reads the diversity levels from the configuration global_variables.

    Returns:
        dict[str, List[str]]: the diversity levels.
    """
    diversity_levels = read_system_config.read_yaml_configuration(
        "diversity_levels", "global_variables.yaml"
    )
    return diversity_levels


@pytest.fixture
def input_mark_diversity() -> pd.DataFrame:
    """Fixture with input for testing marking the diversity.

    Returns:
        pd.DataFrame: input for marking the diversity.
    """
    df = pd.read_csv("./tests/fixtures/diversity/input_mark_diversity.csv", sep=";")
    return df


@pytest.fixture
def output_mark_diversity() -> pd.DataFrame:
    """Fixture with expected output for testing marking the diversity.

    Returns:
        pd.DataFrame: output with marked diversity.
    """
    df = pd.read_csv("./tests/fixtures/diversity/output_mark_diversity.csv", sep=";")
    return df


@pytest.fixture
def input_mark_diversity_species_uncounted() -> pd.DataFrame:
    """Fixture with input for testing marking diversity with uncounted species.

    Returns:
        pd.DataFrame: input with uncounted species.
    """
    df = pd.read_csv(
        "./tests/fixtures/diversity/input_mark_diversity_species_uncounted.csv", sep=";"
    )
    return df


@pytest.fixture
def output_mark_diversity_species_uncounted() -> pd.DataFrame:
    """Fixture with expected output for testing marking diversity with uncounted species.

    Returns:
        pd.DataFrame: expected output for marking with uncounted species.
    """
    df = pd.read_csv(
        "./tests/fixtures/diversity/output_mark_diversity_species_uncounted.csv",
        sep=";",
    )
    return df


@pytest.fixture
def input_distribute_abunances() -> pd.DataFrame:
    """Fixture with input for testing distributing the abundance.

    Returns:
        pd.DataFrame: input with undistributed abundances.
    """
    df = pd.read_csv(
        "./tests/fixtures/diversity/input_distribute_abunances.csv", sep=";"
    )
    return df


@pytest.fixture
def output_distribute_n() -> pd.DataFrame:
    """Fixture with expected output for testing distributing the abundance.

    Returns:
        pd.DataFrame: expected output with distributed count.
    """
    df = pd.read_csv("./tests/fixtures/diversity/output_distribute_n.csv", sep=";")
    return df


@pytest.fixture
def output_distribute_density() -> pd.DataFrame:
    """Fixture with expected output for testing distributing the abundance.

    Returns:
        pd.DataFrame: expected output with distributed densities.
    """
    df = pd.read_csv(
        "./tests/fixtures/diversity/output_distribute_density.csv", sep=";"
    )
    return df


@pytest.fixture
def input_distribute_density_species_uncounted() -> pd.DataFrame:
    """Fixture with input of testing distributing taxa with uncounted species.

    Returns:
        pd.DataFrame: input for distributing taxa with uncounted species.
    """
    df = pd.read_csv(
        "./tests/fixtures/diversity/input_distribute_density_species_uncounted.csv",
        sep=";",
    )
    return df


@pytest.fixture
def output_distribute_density_species_uncounted() -> pd.DataFrame:
    """Fixture with expected output for testing distributing taxa with uncounted species.

    Returns:
        pd.DataFrame: expected output for distributing taxa with uncounted species.
    """
    df = pd.read_csv(
        "./tests/fixtures/diversity/output_distribute_density_species_uncounted.csv",
        sep=";",
    )
    return df


###########################################################################################
## SPECICES RICHNESS ######################################################################
###########################################################################################


@pytest.fixture
def input_species_richness() -> pd.DataFrame:
    """Fixture with the input for testing the species richness.

    Returns:
        pd.DataFrame: the input for the species richness.
    """
    df = pd.read_csv(
        "./tests/fixtures/species_richness/input_species_richness.csv", sep=";"
    )
    return df


@pytest.fixture
def output_species_rich_area() -> pd.DataFrame:
    """Fixture with the output for testing the species richnesss.

    Returns:
        pd.DataFrame: the species richness over waterbody.
    """
    df = pd.read_csv(
        "./tests/fixtures/species_richness/output_species_rich_area.csv", sep=";"
    )
    return df


@pytest.fixture
def output_species_rich_sample() -> pd.DataFrame:
    """Fixture with the output for testing the species richness.

    Returns:
        pd.DataFrame: the species richness over sample.
    """
    df = pd.read_csv(
        "./tests/fixtures/species_richness/output_species_rich_sample.csv", sep=";"
    )
    return df


###########################################################################################
## DENSITY ################################################################################
###########################################################################################


@pytest.fixture
def input_prepare_density() -> pd.DataFrame:
    """Input for testing preparing the density function.

    Returns:
        pd.DataFrame: input for preparing density calculations.
    """
    df = pd.read_csv("./tests/fixtures/density/input_prepare_density.csv", sep=";")
    return df


@pytest.fixture
def output_prepare_density() -> pd.DataFrame:
    """Fixture with expected output for preparing densities.

    Returns:
        pd.DataFrame: prepared densities.
    """
    df = pd.read_csv("./tests/fixtures/density/output_prepare_density.csv", sep=";")
    return df


@pytest.fixture
def input_aggregate_density() -> pd.DataFrame:
    """Fixture with input for aggregating the densities.

    Returns:
        pd.DataFrame: input for aggregating densities.
    """
    df = pd.read_csv(
        "./tests/fixtures/density/input_aggregate_density.csv", sep=";", decimal="."
    )
    return df


@pytest.fixture
def output_aggregate_density_waterbody_group() -> pd.DataFrame:
    """Fixture with expected output for aggregated densities by waterbody and groups.

    Returns:
        pd.DataFrame: aggregated densities by waterbody and groups.
    """
    df = pd.read_csv(
        "./tests/fixtures/density/output_aggregate_density_waterbody_group.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def output_aggregate_density_waterbody_no_group() -> pd.DataFrame:
    """Fixture with expected output for aggregated densities by waterbody.

    Returns:
        pd.DataFrame: aggregated densities by waterbody.
    """
    df = pd.read_csv(
        "./tests/fixtures/density/output_aggregate_density_waterbody_no_group.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def output_aggregate_density_area_group() -> pd.DataFrame:
    """Fixture with expected output for aggregated densities by area and groups.

    Returns:
        pd.DataFrame: aggregated densities by area and groups.
    """
    df = pd.read_csv(
        "./tests/fixtures/density/output_aggregate_density_area_group.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def output_aggregate_density_area_no_group() -> pd.DataFrame:
    """Fixture with expected output for aggregated densities by area.

    Returns:
        pd.DataFrame: aggregated densities by area.
    """
    df = pd.read_csv(
        "./tests/fixtures/density/output_aggregate_density_area_no_group.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def output_aggregate_density_stratum_area_group() -> pd.DataFrame:
    """Fixture with expected output for aggregated densities by stratum, area and group.

    Returns:
        pd.DataFrame: aggregated densities by stratrum, area and group.
    """
    df = pd.read_csv(
        "./tests/fixtures/density/output_aggregate_density_stratum_area_group.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def output_aggregate_density_stratum_area_no_group() -> pd.DataFrame:
    """Fixture with expected output for aggregated densities by stratum and area.

    Returns:
        pd.DataFrame: aggregated densities by stratum and group.
    """
    df = pd.read_csv(
        "./tests/fixtures/density/output_aggregate_density_stratum_area_no_group.csv",
        sep=";",
        decimal=".",
    )
    return df


###########################################################################################
## NEW DISAPPEARED RETURNED SPECIES #######################################################
###########################################################################################


@pytest.fixture
def input_no_exotic() -> pd.DataFrame:
    """Fixture with input for testing exotics without exotics.

    Returns:
        pd.DataFrame: data with no exotic species.
    """
    df = pd.read_csv(
        "./tests/fixtures/new_disappeared_returned/input_no_exotic.csv",
        sep=";",
    )
    return df


@pytest.fixture
def output_no_exotic() -> pd.DataFrame:
    """Fixture with expected output by marking exotics without exotics.

    Returns:
        pd.DataFrame: output without exotics marked.
    """
    df = pd.read_csv(
        "./tests/fixtures/new_disappeared_returned/output_no_exotic.csv",
        sep=";",
    )
    return df


@pytest.fixture
def input_exotic() -> pd.DataFrame:
    """Fixture with input for testing exotics with exotics.

    Returns:
        pd.DataFrame: data with exotic species.
    """
    df = pd.read_csv(
        "./tests/fixtures/new_disappeared_returned/input_exotic.csv",
        sep=";",
    )
    return df


@pytest.fixture
def output_exotic() -> pd.DataFrame:
    """Fixture with expected output by marking exotics.

    Returns:
        pd.DataFrame: output with exotic species marked.
    """
    df = pd.read_csv(
        "./tests/fixtures/new_disappeared_returned/output_exotic.csv",
        sep=";",
    )
    return df


@pytest.fixture
def input_merge_NDR() -> pd.DataFrame:
    """Fixture with input data for merging the new, disappeared, returned (NDR) species.

    Returns:
        pd.DataFrame: input for merging NDR species.
    """
    df = pd.read_csv(
        "./tests/fixtures/new_disappeared_returned/input_merge_NDR.csv",
        sep=";",
    )
    return df


@pytest.fixture
def output_merge_sample(year_column_types: dict) -> pd.DataFrame:
    """Fixture csv with expected output for samples after merging.

    Args:
        year_column_types (dict): the years for which the samples are merged.

    Returns:
        pd.DataFrame: the merged samples.
    """
    df = pd.read_csv(
        "./tests/fixtures/new_disappeared_returned/output_merge_sample.csv",
        sep=";",
        dtype=year_column_types,
    )
    return df


@pytest.fixture
def output_merge_new() -> pd.DataFrame:
    """Fixture csv with expected output for new species after merging.

    Args:
        year_column_types (dict): the years for which the new species are merged.

    Returns:
        pd.DataFrame: the new species.
    """
    df = pd.read_csv(
        "./tests/fixtures/new_disappeared_returned/output_merge_new.csv",
        sep=";",
    )
    return df


@pytest.fixture
def output_merge_returned() -> pd.DataFrame:
    """Fixture csv with expected output for returned species after merging.

    Args:
        year_column_types (dict): the years for which the returned species are merged.

    Returns:
        pd.DataFrame: the returned species.
    """
    df = pd.read_csv(
        "./tests/fixtures/new_disappeared_returned/output_merge_returned.csv",
        sep=";",
    )
    return df


@pytest.fixture
def output_merge_disappeared() -> pd.DataFrame:
    """Fixture csv with expected output for disappeared species after merging.

    Args:
        year_column_types (dict): the years for which the disappeared species are merged.

    Returns:
        pd.DataFrame: the disappeared species.
    """
    df = pd.read_csv(
        "./tests/fixtures/new_disappeared_returned/output_merge_disappeared.csv",
        sep=";",
    )
    return df


@pytest.fixture
def input_main_NDR() -> pd.DataFrame:
    """Fixture with input data for the integration test of new, disappeared
    and returned species.

    Returns:
        pd.DataFrame: input data with taxa.

    """
    df = pd.read_csv(
        "./tests/fixtures/new_disappeared_returned/input_main_NDR.csv",
        sep=";",
    )
    return df


###########################################################################################
## TABLES #################################################################################
###########################################################################################


@pytest.fixture
def input_create_pivot_table() -> pd.DataFrame:
    """Fixture with input for testing the creation of a pivot table.

    Returns:
        pd.DataFrame: input for a pivot table creation.
    """
    df = pd.read_csv(
        "./tests/fixtures/tables/input_create_pivot_table.csv", sep=";", decimal="."
    )
    return df


@pytest.fixture
def output_create_pivot_table() -> pd.DataFrame:
    """Fixture with the expected output as pivot table.

    Returns:
        pd.DataFrame: a pivot table.
    """
    df = pd.read_csv(
        "./tests/fixtures/tables/output_create_pivot_table.csv", sep=";", decimal="."
    )
    return df


@pytest.fixture
def input_sample_a_year() -> pd.DataFrame:
    """Fixture with input for calculating how many samples there are a year.

    Returns:
        pd.DataFrame: input for calculating the samples a year.
    """
    df = pd.read_csv(
        "./tests/fixtures/tables/input_sample_a_year.csv", sep=";", decimal="."
    )
    return df


@pytest.fixture
def output_sample_a_year(year_column_types: dict) -> pd.DataFrame:
    """Fixture with expected output for calculating the sample a year.

    Args:
        year_column_types (dict): the years for calculating.

    Returns:
        pd.DataFrame: the samples a year.
    """
    df = pd.read_csv(
        "./tests/fixtures/tables/output_sample_a_year.csv",
        sep=";",
        decimal=".",
        dtype=year_column_types,
    )
    return df


@pytest.fixture
def output_analysis_sample_a_year(year_column_types: dict) -> pd.DataFrame:
    """Fixture with expected output for calculating the sample a year
    for analysis data.

    Args:
        year_column_types (dict): the years for calculating.

    Returns:
        pd.DataFrame: the samples a year.
    """
    df = pd.read_csv(
        "./tests/fixtures/analysis/output_analysis_sample_a_year.csv",
        sep=";",
        decimal=".",
        dtype=year_column_types,
    )
    return df


@pytest.fixture
def input_species_list_wadkust() -> pd.DataFrame:
    """Fixture with input for creating the species list for the Waddenzee.

    Returns:
        pd.DataFrame: taxa of the Waddenzee.
    """
    df = pd.read_csv(
        "./tests/fixtures/tables/input_species_list_wadkust.csv", sep=";", decimal="."
    )
    return df


@pytest.fixture
def input_species_list_noordzee() -> pd.DataFrame:
    """Fixture with input for creating the species list for the Noordzee.

    Returns:
        pd.DataFrame: taxa of the Noordzee.
    """
    df = pd.read_csv(
        "./tests/fixtures/tables/input_species_list_noordzee.csv", sep=";", decimal="."
    )
    return df


@pytest.fixture
def output_species_list_wadkust() -> pd.DataFrame:
    """Fixture with expected output for the species list of the Waddenzee.

    Returns:
        pd.DataFrame: species list of the Waddenzee.
    """
    cols = {
        "Monsterjaar": "int64",
        "Waterlichaam": "object",
        "Gebied": object,
        "Analyse_taxonnaam": object,
        "Habitattype_Waterlichaam": object,
        "N2000-gebied_Waterlichaam": object,
        "Habitattype_Gebied": object,
        "N2000-gebied_Gebied": object,
    }

    df = pd.read_csv(
        "./tests/fixtures/tables/output_species_list_wadkust.csv",
        sep=";",
        decimal=".",
        dtype=cols,
    )

    return df


@pytest.fixture
def output_species_list_noordzee() -> pd.DataFrame:
    """Fixture with expected output for the species list of the Noordzee.

    Returns:
        pd.DataFrame: species list of the Noordzee.
    """
    cols = {
        "Monsterjaar": "int64",
        "Waterlichaam": "object",
        "Gebied": object,
        "Analyse_taxonnaam": object,
        "Habitattype_Waterlichaam": object,
        "N2000-gebied_Waterlichaam": object,
        "Habitattype_Gebied": object,
        "N2000-gebied_Gebied": object,
    }
    df = pd.read_csv(
        "./tests/fixtures/tables/output_species_list_noordzee.csv",
        sep=";",
        decimal=".",
        dtype=cols,
    )
    return df


###########################################################################################
## SHANNON ################################################################################
###########################################################################################


@pytest.fixture
def input_shannon() -> pd.DataFrame:
    """Fixture with input for calculating the shannon index.

    Returns:
        pd.DataFrame: benthos analysis data.
    """
    df = pd.read_csv("./tests/fixtures/shannon/input_shannon.csv", sep=";", decimal=".")
    return df


@pytest.fixture
def output_shannon_sample() -> pd.DataFrame:
    """Fixture with expected output for calculating the shannon index.

    Returns:
        pd.DataFrame: the calculated shannon index.
    """
    df = pd.read_csv(
        "./tests/fixtures/shannon/output_shannon_sample.csv", sep=";", decimal="."
    )
    return df


@pytest.fixture
def output_shannon_area() -> pd.DataFrame:
    """Fixture with expected output for calculating the shannon index by area.

    Returns:
        pd.DataFrame: the calculated shannon index by area.
    """
    df = pd.read_csv(
        "./tests/fixtures/shannon/output_shannon_area.csv", sep=";", decimal="."
    )
    return df


###########################################################################################
## MARGALEF ###############################################################################
###########################################################################################


@pytest.fixture
def input_margalef() -> pd.DataFrame:
    """The input for calculating the margalefs index.

    Returns:
        pd.DataFrame: the input benthos data.
    """
    df = pd.read_csv(
        "./tests/fixtures/margalef/input_margalef.csv", sep=";", decimal="."
    )
    return df


###########################################################################################
## BISI ###################################################################################
###########################################################################################


@pytest.fixture
def input_check_required_area() -> pd.DataFrame:
    """Fixture with input for testing checking required BISI area.

    Returns:
        pd.DataFrame: the input for checking the required BISI area.
    """
    df = pd.read_csv(
        "./tests/fixtures/bisi/input_check_required_area.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def input_check_required_area_invalid() -> pd.DataFrame:
    """Fixture with input for testing checking required BISI area as invalid.

    Returns:
        pd.DataFrame: the input for checking the required BISI area as invalid.
    """
    df = pd.read_csv(
        "./tests/fixtures/bisi/input_check_required_area_invalid.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def input_bisi_main() -> pd.DataFrame:
    """Fixture with input for testing the main BISI functionality.

    Returns:
        pd.DataFrame: input for calculating the BISI.
    """
    df = pd.read_csv(
        "./tests/fixtures/bisi/input_bisi_main.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def output_bisi_main_COM_KRM() -> pd.DataFrame:
    """Fixture with expected output for BISI data for Centrale Oestergronden (KRM-area).

    Returns:
        pd.DataFrame: BISI data for Centrale Oestergronden (KRM-area).
    """
    df = pd.read_csv(
        "./tests/fixtures/bisi/output_bisi_main_COM_KRM.csv",
        sep=";",
        decimal=".",
        dtype={"Position": "int64"},  # prevent panda's from interpret as range
    )
    return df


@pytest.fixture
def output_bisi_main_BB_KRM() -> pd.DataFrame:
    """Fixture with expected output for BISI data for Bruine Bank (KRM-area).

    Returns:
        pd.DataFrame: BISI data for Bruine Bank (KRM-area).
    """
    df = pd.read_csv(
        "./tests/fixtures/bisi/output_bisi_main_BB_KRM.csv",
        sep=";",
        decimal=".",
        dtype={"Position": "int64"},  # prevent panda's from interpret as range
    )
    return df


@pytest.fixture
def input_indicator_species() -> pd.DataFrame:
    """Fixture with input data for the indicator species for the BISI area.

    Returns:
        pd.DataFrame: input indicator species.
    """
    df = pd.read_csv(
        "./tests/fixtures/bisi/input_indicator_species.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def input_check_samples() -> pd.DataFrame:
    """Fixture with input for testing checking the samples.

    Returns:
        pd.DataFrame: checking the samples.
    """
    df = pd.read_csv(
        "./tests/fixtures/bisi/input_check_samples.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def input_bisi_calculations() -> pd.DataFrame:
    """Fixture with input for testing the BISI calculations.

    Returns:
        pd.DataFrame: input for calculating the BISI.
    """
    df = pd.read_csv(
        "./tests/fixtures/bisi/input_bisi_calculations.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def input_bisi_criteria() -> pd.DataFrame:
    """Fixture with input for testing the BISI criteria.

    Returns:
        pd.DataFrame: input for the BISI criteria.
    """
    df = pd.read_csv(
        "./tests/fixtures/bisi/input_bisi_criteria.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def output_bisi_calculations() -> pd.DataFrame:
    """Fixture with expected output for calculating the BISI.

    Returns:
        pd.DataFrame: output for calculating the BISI.
    """
    df = pd.read_csv(
        "./tests/fixtures/bisi/output_bisi_calculations.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def input_map_taxa_to_bisi() -> pd.DataFrame:
    """Fixture with input for mapping the taxa to the BISI species.

    Returns:
        pd.DataFrame: the taxa for the BISI.
    """
    df = pd.read_csv(
        "./tests/fixtures/bisi/input_map_taxa_to_bisi.csv",
        sep=";",
        decimal=".",
    )
    return df


@pytest.fixture
def output_map_taxa_to_bisi() -> pd.DataFrame:
    """Fixture with expected output for mapping taxa to BISI species.

    Returns:
        pd.DataFrame: taxa mapped to the BISI species.
    """
    df = pd.read_csv(
        "./tests/fixtures/bisi/output_map_taxa_to_bisi.csv",
        sep=";",
        decimal=".",
    )
    return df


###########################################################################################
## EUNIS ##################################################################################
###########################################################################################


@pytest.fixture
def input_eunis() -> pd.DataFrame:
    """Fixture with the input for testing the EUNIS calculations.

    Returns:
        pd.DataFrame: the input for the EUNIS.
    """
    df = pd.read_csv("./tests/fixtures/eunis/input_eunis.csv", sep=";")
    return df


@pytest.fixture
def output_eunis() -> pd.DataFrame:
    """Fixture with the output for testing the EUNIS calculations.

    Returns:
        pd.DataFrame: the EUNIS calculations.
    """
    df = pd.read_csv("./tests/fixtures/eunis/output_eunis.csv", sep=";")
    return df


###########################################################################################
## ANALYSIS ###############################################################################
###########################################################################################


@pytest.fixture
def input_analysis_main() -> pd.DataFrame:
    """Fixture with input for testing the integration of the analysis script.

    Returns:
        pd.DataFrame: benthos data for the analysis phase.
    """
    df = pd.read_csv(
        "./tests/fixtures/analysis/input_analysis_main.csv",
        sep=";",
        decimal=".",
    )
    return df


###########################################################################################
## GRAPHS #################################################################################
###########################################################################################


@pytest.fixture
def input_scatterplot_dichtheid_aantal() -> pd.DataFrame:
    """Fixture with input for creating the scatterplot based on densities (n).

    Returns:
        pd.DataFrame: input data for the scatterplot with densities (n).
    """
    df = pd.read_csv(
        "./tests/fixtures/plot/input_scatterplot_dichtheid_aantal.csv", sep=";"
    )
    return df


@pytest.fixture
def input_barplot_dichtheid_aantal() -> pd.DataFrame:
    """Fixture with input data for the barplot for density (n).

    Returns:
        pd.DataFrame: input with densities (n).
    """
    df = pd.read_csv(
        "./tests/fixtures/plot/input_barplot_dichtheid_aantal.csv", sep=";"
    )
    return df


@pytest.fixture
def output_barplot_fill_missing_years() -> pd.DataFrame:
    """Fixture with output data missing years are filled for all groups.

    Returns:
        pd.DataFrame: input with densities (n).
    """
    df = pd.read_csv(
        "./tests/fixtures/plot/output_barplot_fill_missing_years.csv", sep=";"
    )
    return df


@pytest.fixture
def output_barplot_no_fill_missing_years() -> pd.DataFrame:
    """Fixture with output data missing years are not filled for all groups.

    Returns:
        pd.DataFrame: input with densities (n).
    """
    df = pd.read_csv(
        "./tests/fixtures/plot/output_barplot_no_fill_missing_years.csv", sep=";"
    )
    return df
