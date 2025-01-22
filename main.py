"""__________________DEEL-C MACROZOÖBENTHOS SCRIPT__________________"""

"""
# File: Main.py
# Author(s): M. Japink (m.japink@waardenburg.eco) & J. Haringa (j.haringa@waardenburg.eco)
# Creation date: 21-01-2023
# Last modification: 20-02-2024
# Python v3.12.1
"""

# IMPORT THE NECESSARY PACKAGES
from analysis import BISI
from analysis import analysis_tree
from checks import check_config
from preparation import benthos_data


# GENERATE INPUT DATA
check_config.main_check_configuration()
data = benthos_data.main_benthos_data()

# GENERATE TABLES
analysis_tree.analysis_main(data)
BISI.main_bisi(data, year=2015)