"""Performs checks for the tables."""

"""
# File: check_tables.py
# Author(s): M. Japink (m.japink@waardenburg.eco) & J. Haringa (j.haringa@waardenburg.eco)
# Creation date: 8-11-2023
# Last modification: 20-02-2024
# Python v3.12.1
"""

import logging
import logging.config
import os

import pandas as pd

from preparation import process_twn
from preparation import read_system_config


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))

logger = logging.getLogger(__name__)


def check_habitat_n2000_species_conform_twn() -> pd.DataFrame:
    """Checks whether the configuration file with the typical species for each
    habitat type are conform the latested downloaded version of the TWN.

    Returns:
        pd.DataFrame: dataframe with the habitat species configuration data.
    """
    twn_corrected = read_system_config.read_csv_file(
        read_system_config.read_yaml_configuration(
            "twn_corrected", "global_variables.yaml"
        )
    )
    habitat_species = read_system_config.read_csv_file(
        read_system_config.read_yaml_configuration(
            "config_hr_species", "global_variables.yaml"
        )
    )
    twn_synonyms = process_twn.has_synonym(twn_corrected, habitat_species)
    if not habitat_species["Analyse_taxonnaam"].isin(twn_synonyms).all():
        syn_twn_not_present = habitat_species[
            ~habitat_species["Analyse_taxonnaam"].isin(twn_synonyms)
        ]["Analyse_taxonnaam"]
        logger.warning(
            "De taxa in de typische habitat soorten tabel zijn niet conform de twn en "
            "zullen niet worden meegenomen. Verbeter deze conform de twn. "
            "Deze soorten zijn: \n"
            f"{syn_twn_not_present}"
        )
    return habitat_species
