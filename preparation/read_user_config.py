"""Script to read the configurations files."""

"""
# File: read_user_config.py
# Author(s): M. Japink (m.japink@waardenburg.eco) & J. Haringa (j.haringa@waardenburg.eco)
# Creation date: 21-01-2023
# Last modification: 20-02-2024
# Python v3.12.1
"""

import logging
import os
from typing import List
from typing import Optional


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))

from preparation import log_decorator
from preparation import read_system_config
from preparation import utility


logger = logging.getLogger(__name__)


@log_decorator.log_factory(__name__)
def read_txt_file(filename: str) -> Optional[str]:
    """Reads the content of an user configuration file.

    Args:
        filename (str): the filename.

    Returns:
        str: content of the file.
    """

    content = ""
    try:
        file = open(filename, mode="r")
        content = file.read()
        file.close()
    except FileNotFoundError:
        logger.error(f"Bestand {filename} niet gevonden.")
        utility.stop_script()  # type: ignore
    except IOError:
        logger.error(f"Error lezen bestand {filename}.")
        utility.stop_script()  # type: ignore
    return content


@log_decorator.log_factory(__name__)
def parse_user_configuration(file_content: str) -> List[str]:
    """Parses the userconfig file content. Filters only selected projects and waterbodies and returns a list.

    Args:
        file_content (str): the content of a file.

    Returns:
        list: with uncommented project codes or waterbodies.
    """

    content_list = []
    content = file_content.split("\n")
    for line in content:
        if line == "":
            break
        if not line.startswith("#"):
            content_list.append(line)
    content_list = list(set(content_list))  # remove duplicates
    return content_list


@log_decorator.log_factory(__name__)
def check_user_configuration(uncommented_list: List[str], filename: str) -> List[str]:
    """Checks if the user has uncommented any configuration lines.

    Args:
        uncommented_list (list): a list of uncommented items from the file.
        filename (str): the filename.

    Returns:
        list: configuration list.
    """

    if not uncommented_list:
        logger.error(f"Er zijn geen {filename[:-4]} geselecteerd.")
        utility.stop_script()

    return uncommented_list


@log_decorator.log_factory(__name__)
def read_user_configuration(filename: str) -> List[str]:
    """Reads and formats the content of a user configuration file.

    Args:
        filename (str): the filename.

    Returns:
        list: a list representing the user configuration.
    """
    content = read_txt_file(filename)
    uncommented_list = parse_user_configuration(content)
    configuration_list = check_user_configuration(uncommented_list, filename)
    return configuration_list


@log_decorator.log_factory(__name__)
def read_required_waterbodies() -> List[str]:
    """Function reads the user configured waterbodies in the input folder.

    Args:
       None

    Returns: (List[str]): list with waterbodies.
    """

    waterbodies = read_user_configuration(
        read_system_config.read_yaml_configuration(
            "selection_waterbodies", "global_variables.yaml"
        )
    )
    return waterbodies


@log_decorator.log_factory(__name__)
def read_required_projects() -> List[str]:
    """Function reads the user configured projects in the input folder.

    Args:
       None

    Returns: (list): list with projects.
    """

    projects = read_user_configuration(
        read_system_config.read_yaml_configuration(
            "selection_projects", "global_variables.yaml"
        )
    )
    return projects
