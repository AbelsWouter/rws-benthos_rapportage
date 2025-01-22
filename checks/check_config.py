"""Script to perform different checks on configuration."""

# File: check_config.py
# Author(s): M. Japink (m.japink@waardenburg.eco) & J. Haringa (j.haringa@waardenburg.eco)
# Creation date: 21-01-2023
# Last modification: 20-02-2024
# Python v3.12.1


import logging
import logging.config
import os
import sys
from typing import Any
from typing import Tuple

import pandas as pd


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))

from checks import check_data
from preparation import log_decorator
from preparation import read_system_config
from preparation import utility


logger = logging.getLogger(__name__)


@log_decorator.log_factory(__name__)
def check_empty_input_folder() -> bool:
    """Check whether the output and input folder are empty.

    Returns:
        bool: True if the input folder is empty,
              False if there is one file in the input folder.

    """
    foldername = read_system_config.read_yaml_configuration(
        "data_path", "global_variables.yaml"
    )

    file_list = [file for file in os.listdir(foldername) if not file.endswith(".txt")]
    if len(file_list) == 0:
        logger.info(
            "De inputfolder bevat geen bestand, data wordt gedownload uit Aquadesk."
        )
        return True
    if len(file_list) == 1:
        logger.info(
            f"Het bestand '{file_list[0]}' in de inputfolder wordt gebruikt voor de verwerking."
        )
        return False
    logger.error(
        "Er kan maar één bestand met data worden aangeboden controleer de inputfolder."
    )
    utility.stop_script()
    return False


@log_decorator.log_factory(__name__)
def empty_output_folder():
    """Check whether the output folder is empty.

    Raises:
        Exception: If the output folder is not empty.
    """
    output_path = read_system_config.read_yaml_configuration(
        "output_path", "global_variables.yaml"
    )
    drop_files = ["twn_download.csv", "twn_gecorrigeerd.csv", "logfile.log"]
    file_list = os.listdir(output_path)

    # if three or less in the output folder try to drop them
    if len(file_list) <= 3:
        for filename in drop_files:
            file_path = os.path.join(output_path, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                file_list.remove(filename)

    return file_list


@log_decorator.log_factory(__name__)
def check_empty_output_folder():
    """Check whether the output and input folder are empty.

    Raises:
        Exception: If the output folder is not empty.
    """

    # read files in outputfolder
    output_path = read_system_config.read_yaml_configuration(
        "output_path", "global_variables.yaml"
    )
    file_list = os.listdir(output_path)

    # if any files exit script
    if len(file_list) > 0:
        FAIL = "\033[91m"
        ENDC = "\033[0m"

        print(
            f"{FAIL} \nDe outputfolder is niet leeg.\nVerwijder/verplaats de inhoud van de outputfolder.\n\n {ENDC}"
        )
        # raise Exception(f"verwerkingsfout")
        sys.exit()


@log_decorator.log_factory(__name__)
def check_one_input_file() -> None:
    """Checks whether there is only one input file (excl. txt files)."""
    count = 0
    for path in os.scandir(
        read_system_config.read_yaml_configuration("data_path", "global_variables.yaml")
    ):
        if path.is_file() and not path.name.endswith(".txt"):
            count += 1
            logger.debug(f"path= {path}")
    if count > 1:
        logger.error(
            "De folder input bevat meer dan 1 data bestand. Maar 1 input bestand is mogelijk.\n"
            "Misschien staat een bestand nog open? Of verwijder de/het bestand(en) om "
            "maar 1 input bestand over te houden."
        )
        utility.stop_script()


@log_decorator.log_factory(__name__)
def check_required_folders() -> Any:
    """Checks if required folders exists"""
    input_folder = read_system_config.read_yaml_configuration(
        "data_path", "global_variables.yaml"
    )
    if not os.path.exists(input_folder):
        logger.error(
            "Het script is corrupt. De input folder ontbreekt. Download/installeer het script opnieuw."
        )
        utility.stop_script()


@log_decorator.log_factory(__name__)
def check_output_folder_exists() -> None:
    """Checks whether the output folder exists.

    Raises:
        Exception: If the output folder does not exists and could not be created.
    """
    output_folder = read_system_config.read_yaml_configuration(
        "output_path", "global_variables.yaml"
    )
    if not os.path.exists(output_folder):
        logger.info("\nDe outputfolder bestond niet en is opnieuw aangemaakt.")
        try:
            os.makedirs(output_folder)
        except Exception as e:
            raise Exception(f"Kan de folder outputfolder niet aanmaken, omdat {e}")


@log_decorator.log_factory(__name__)
def check_waterbody_configuration_files() -> Any:
    """Check the configuration files for logical errors.
    Delegates specific funtionality to child functions

    Returns:
        bool: True all the checks are correct, else False.

    """

    wl_system, wl_user, wl_loc = read_waterbody_configuration_files()
    is_unique_user = check_data.check_uniqueness(
        wl_user, ["Waterlichaam"], "Waterlichaam.txt"
    )
    is_unique_system = check_data.check_uniqueness(
        wl_system, ["Waterlichaam"], "Waterlichaam.csv"
    )
    is_unique_loc = check_data.check_uniqueness(
        wl_loc,
        ["Waterlichaam", "Meetobject_Code", "Methode", "Project_Code"],
        "Locaties.csv",
    )

    is_equal = check_waterbody_equality(wl_system, wl_user, wl_loc)

    wl_system_cols = pd.Series(
        read_system_config.read_yaml_configuration(
            "exp_waterbody_columns", "global_variables.yaml"
        )
    )
    check_data.check_required_col(wl_system, wl_system_cols)

    wl_loc_cols = pd.Series(
        read_system_config.read_yaml_configuration(
            "exp_location_columns", "global_variables.yaml"
        )
    )
    check_data.check_required_col(wl_loc, wl_loc_cols)

    non_NA_system_waterbody_columns = pd.Series(
        read_system_config.read_yaml_configuration(
            "non_NA_waterbody_columns", "global_variables.yaml"
        )
    )
    check_data.check_missing_values(
        wl_system, non_NA_system_waterbody_columns, "Waterlichaam.csv"
    )

    non_NA_location_columns = pd.Series(
        read_system_config.read_yaml_configuration(
            "non_NA_location_columns", "global_variables.yaml"
        )
    )
    check_data.check_missing_values(
        wl_system, non_NA_location_columns, "Waterlichaam.csv"
    )
    check = is_unique_user and is_unique_system and is_unique_loc and is_equal
    if not check:
        logger.error("Check configuratie is niet correct.")
        utility.stop_script()
    return check


@log_decorator.log_factory(__name__)
def read_waterbody_configuration_files() -> (
    Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
):
    """Reads the waterbodies from the config file.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: the waterbodies from the system, user, and locations.
    """

    wl_system = read_system_config.read_csv_file(
        read_system_config.read_yaml_configuration(
            "config_waterbodies", "global_variables.yaml"
        )
    )

    wl_user = read_system_config.read_csv_file(
        read_system_config.read_yaml_configuration(
            "selection_waterbodies", "global_variables.yaml"
        )
    )
    wl_loc = read_system_config.read_csv_file(
        read_system_config.read_yaml_configuration(
            "config_locations", "global_variables.yaml"
        )
    )

    wl_user = wl_user.iloc[2:, :].drop_duplicates()
    wl_user = wl_user.set_axis(["Waterlichaam"], axis=1)
    return wl_system, wl_user, wl_loc


@log_decorator.log_factory(__name__)
def check_waterbody_equality(
    wl_system: pd.DataFrame, wl_user: pd.DataFrame, wl_loc: pd.DataFrame
) -> bool:
    """Checks whether the waterbodies from user, system and location config are equal.

    Args:
        wl_system (pd.DataFrame): the waterbodies from the waterbody config.
        wl_user (pd.DataFrame): the waterbodies from the user.
        wl_loc (pd.DataFrame): the waterbodies from the location config.

    Returns:
        bool: True if all the waterbodies are equal.
    """
    wl_system = wl_system.Waterlichaam.values.tolist()

    wl_user["Waterlichaam"] = wl_user["Waterlichaam"].str.replace("#", "")
    wl_user = wl_user.Waterlichaam.values.tolist()

    wl_loc = wl_loc.filter(["Waterlichaam"]).drop_duplicates()
    wl_loc = wl_loc.Waterlichaam.values.tolist()

    # check against wl_sys
    wl_user_diff = set(wl_system) ^ set(wl_user)
    wl_loc_diff = set(wl_system) ^ set(wl_loc)
    if len(wl_user_diff) > 0:
        logger.error(
            "De volgende waterlichaamnamen in de gebruikersconfiguratie wijken af: "
            + str(wl_user_diff)
        )
    if len(wl_loc_diff) > 0:
        logger.error(
            "De volgende waterlichaamnamen in de locatie-configuratie wijken af: "
            + str(wl_loc_diff)
        )
    if len(wl_user_diff) > 0 or len(wl_loc_diff) > 0:
        utility.stop_script()

    return True


def check_bisi_configuration_files() -> bool:
    """Check the configuration files for logical errors.
    Delegates specific funtionality to child functions.

    Returns:
        bool: True if both configuration files have been read.
    """
    bisi_config = read_system_config.read_bisi_config()
    locations = read_system_config.read_csv_file(
        read_system_config.read_yaml_configuration(
            "config_locations", "global_variables.yaml"
        )
    )

    check_bisi_cols_in_locations(locations)
    check_bisi_area_equality(bisi_config, locations)
    return True


def check_bisi_cols_in_locations(locations: pd.DataFrame) -> bool:
    """Checks whether the bisi columns are in the locations.

    Args:
        locations (pd.DataFrame): the locations for the bisi.

    Returns:
        bool: True if the columns are present.
    """
    bisi_present = False
    for column in locations.columns:
        if column.startswith("BISI_"):
            bisi_present = True
    if not bisi_present:
        logger.error(
            "De location-configuratie bevat geen kolommen die beginnen met 'BISI_'."
        )
        utility.stop_script()
    return True


def check_bisi_area_equality(
    bisi_config: pd.DataFrame, locations: pd.DataFrame
) -> bool:
    """Check for each bisi column in location config if it's values are in bisi config.

    Args:
        bisi_config (pd.DataFrame): the configuration data for the bisi.
        locations (pd.DataFrame): the locations for the bisi.

    Returns:
        bool: true if all columns in the location configuration.
    """
    for column in locations.columns:
        if column.startswith("BISI_"):
            bisi_areas = bisi_config["BISI_indeling"].dropna().unique().tolist()
            locations_areas = locations[column].dropna().unique().tolist()

            difference = list(set(locations_areas) - set(bisi_areas))
            if len(difference) > 0:
                logger.error(
                    f"De volgende bisi-indeling(en) in de kolom {column} in de locatie-configuratie "
                    f"is/zijn niet opgenomen in de bisi-configuratie: "
                    + f"{difference}"
                )
                utility.stop_script()

    return True


def check_taxon_groups() -> Tuple[bool, bool]:
    """Check the taxon group classification for logical errors.

    Returns:
        bool: True if the classification is correct.
    """
    groups = read_system_config.read_csv_file(
        read_system_config.read_yaml_configuration(
            "config_taxon_groups", "global_variables.yaml"
        )
    )

    # test for missing values in one of the columns
    has_NA = check_data.check_missing_values(
        groups,
        ["Trendgroep", "Taxongroup_code", "Taxongroup", "Groep", "Groepkleur"],
        "Taxon_group.csv",
    )

    # make unique by Trendgroep , Groep and Colour
    groups_colors = groups[["Trendgroep", "Groep", "Groepkleur"]].drop_duplicates()

    # check if Trendgroep and Groep are unique
    is_unique = check_data.check_uniqueness(
        groups_colors, ["Trendgroep", "Groep"], "Taxon_groups.csv"
    )
    return has_NA, is_unique


def check_output_folder():
    """Performs several checks on the output folder."""
    check_output_folder_exists()
    empty_output_folder()
    check_empty_output_folder()


def main_check_configuration():
    """Checks the required folders, one input file and the config files."""
    check_output_folder()
    logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
    check_required_folders()
    check_one_input_file()
    check_waterbody_configuration_files()
    check_bisi_configuration_files()
    check_taxon_groups()
