"""The density of species per area will be calculated."""

"""
# File: utility.py
# Author(s): M. Japink (m.japink@waardenburg.eco) & J. Haringa (j.haringa@waardenburg.eco)
# Creation date: 21-07-2023
# Last modification: 20-02-2024
# Python v3.12.1
"""

import logging
import os
import platform
import sys
import typing
from typing import Union

import numpy as np
import pandas as pd


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))


from preparation import log_decorator


logger = logging.getLogger(__name__)


@log_decorator.log_factory(__name__)
def stop_script():
    """Standard exit routine

    Args:
        None

    Returns:
        Print an default exit message to the screen.
    """

    # https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
    FAIL = "\033[91m"
    ENDC = "\033[0m"

    print(
        f"{FAIL} \n\nHet script is gestopt vanwege een verwerkingsfout. Controleer de logfile op errors en warnings. \n"
        f"Zie de gebruikershandleiding voor hulp bij het oplossen van het probleem.\n\n {ENDC}"
    )
    # raise Exception(f"verwerkingsfout")
    sys.exit()


@log_decorator.log_factory(__name__)
def coalesce(
    *args: Union[int, float, str, bool, None, pd.NA, np.nan]
) -> Union[int, float, str, bool, np.nan]:
    """Return the first non-NA(/nan/None) value or np.nan if all values are NA.

    Args:
        *values (any): comma separated values.

    Returns:
        any: the fist non None occurence or None.
    """
    for arg in args:
        if pd.notna(arg):
            return arg
    return np.nan


@log_decorator.log_factory(__name__)
def replace_values(
    df: pd.DataFrame,
    replace_dict: dict[str, typing.Any],
    find_field: str,
    replace_field: str,
    datasetname: str = None,
) -> pd.DataFrame:
    """Replaces values in pandas dataframe.

    Args:
        df (pd.DataFrame): the datafram to replace values in
        replace_dict (dictionary): a dictionary with keys as the values to look for and values as values to replace
        find_field (str): the field to look for
        replace_field (str): the field to replace
        datasetname (str, optional): the name of the dataset to be logged

    Returns:
        pd.DataFrame: a Pandas DataFrame with the new twn.
    """

    if replace_dict:
        for key, value in replace_dict.items():
            check = df.loc[df[find_field] == key]
            if len(check) > 0:
                msg = f"In de {datasetname}-data is" if datasetname else ""
                if replace_field == find_field:
                    msg = f"{msg} {find_field}: '{key}' vervangen door '{value}'"
                else:
                    msg = f"{msg} op basis van {find_field}: '{key}' de {replace_field} vervangen door: '{value}'"
                logger.info(msg)

            df.loc[df[find_field] == key, replace_field] = coalesce(value, None)
    return df


def export_df(df: pd.DataFrame, filepath: str) -> pd.DataFrame:
    """Writes any dataframe to given filepath

    Args:
        df (pd.DataFrame): the datafram to write
        filepath (str): the filepath (location + name)
    """
    extention = os.path.splitext(filepath)[1]

    filepath = valid_path(filepath)

    try:
        if extention == ".csv":
            df.to_csv(filepath, index=False, sep=";")
        elif extention == ".xlsx":
            df.to_excel(filepath, index=False)
        else:
            logger.error("Extentie kan niet naar temp directorie worden geexporteerd.")
            stop_script()
    except Exception as e:
        logger.error(f"Vermoedelijk staat {filepath} nog open.")
        logger.debug(f"{e} with %s", "arguments", exc_info=True)
        stop_script()


def export_temp_file(df: pd.DataFrame, filepath: str) -> None:
    """Writes any dataframe to the systems temp folder.

    Args:
        df (pd.DataFrame): the datafram to write
        filepath (str): the filepath (location + name)
    """
    export = True

    extention = os.path.splitext(filepath)[1]

    if not export:
        return

    filepath = valid_path(filepath)

    if platform.system() == "Windows":
        temppath = "C:/temp"
    elif platform.system() == "Linux" or platform.system() == "Darwin":
        temppath = "/tmp"
    else:
        raise Exception("The os is unknown.")

    tempfilepath = os.path.join(temppath, filepath)
    try:
        if extention == ".csv":
            df.to_csv(tempfilepath, index=False, sep=";")
        elif extention == ".xlsx":
            df.to_excel(tempfilepath, index=False)
        else:
            logger.error("Extentie kan niet naar temp directorie worden geexporteerd.")
            stop_script()
    except Exception as e:
        logger.error(f"Vermoedelijk staat {tempfilepath} nog open.")
        logger.debug(f"{e} with %s", "arguments", exc_info=True)
        stop_script()


def add_prefix_suffix(value: str | int) -> str:
    """Postfix and prefix a strings with "-". If the string is divided by pipes, all separate values are prefixed.

    Args:
        value (str): the string to prefix

    Returns:
        str: returns a string with all values prefixed
    """

    values = str(value).split("|")
    modified_values = ["-{}-".format(v) for v in values]
    return "|".join(modified_values)


@log_decorator.log_factory(__name__)
def get_file_name(data_folder: str) -> typing.Optional[str]:
    """Retrieves the file name from a data folder.

    Args:
        data_folder (str): the name of the folder.

    Returns:
        str: the filenames in the folder.
    """
    filename = ""
    try:
        for filename in os.listdir(data_folder):
            if filename.endswith(".csv") or filename.endswith(".xlsx"):
                return filename

    except Exception as e:
        logger.error(
            f"Kan het bestand niet vinden en/of het type betand niet bepalen, omdat {e}"
        )
        stop_script()
    return None


def check_and_make_output_subfolder(path: str) -> None:
    """Checks whether output folder exists, if not it creates one.

    Args:
        path (str): the path to the output folder.

    Raises:
        Exception: if the output folder can not be created.
    """
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except Exception as e:
            raise Exception(
                f"Kan de folder {path} outputfolder niet aanmaken, omdat {e}"
            )


def valid_path(path: str) -> str:
    """Removes all invalid characters from a filename.

    Args:
        filename (str): the filename to clean.

    Returns:
        str: the cleaned filename.
    """
    invalid_chars = [":", "*", "?", '"', "|"]
    for char in invalid_chars:
        path = path.replace(char, " ")

    # replace < with 'kd' and'>' with 'gd'
    path = path.replace("<", "kd")
    path = path.replace(">", "gd")

    # remove trailing spaces
    path = path.strip()

    ### remove dots in the name but not in the extention ###
    extention = os.path.splitext(path)[1]
    if extention == ".":
        extention = ""
    path = os.path.splitext(path)[0]

    # get beginning dot from path if present
    dot = ""
    if path.startswith("."):
        dot = path[0]
        path = path[1:]

    path = path.replace(".", " ")
    new_path = "".join([dot, path, extention])
    return new_path
