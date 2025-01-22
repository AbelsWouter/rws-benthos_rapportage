"""Figures like scatterplots and barplots will be generated."""

"""
# File: eunis.py
# Author(s): M. Japink (m.japink@waardenburg.eco) & J. Haringa (j.haringa@waardenburg.eco)
# Creation date: 21-01-2023
# Last modification: 20-02-2024
# Python v3.12.1
"""

import logging
import os

import pandas as pd


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))

from analysis import plotter
from preparation import log_decorator
from preparation import read_system_config


logger = logging.getLogger(__name__)


@log_decorator.log_factory(__name__)
def calculate_eunis_coverage(df_eunis: pd.DataFrame, variable: str) -> pd.DataFrame:
    """Creates a species barplot for each EUNIS area.

    Args:
        df (pd.DataFrame): dataframe with the coverage for EUNIS.
        variable (str): the aggregation column.

    Returns:
        pd.DataFrame: the calculated EUNIS coverage.
    """
    # filter Bedekking not is na and add Azoisch column
    df_eunis = df_eunis[df_eunis[variable].notnull()]
    df_eunis["Is_Azoisch"] = df_eunis["Analyse_taxonnaam"] == "Azoisch"

    # groupby to get the mean for each sample
    df_bedek_sample = df_eunis.groupby(
        ["Collectie_Referentie", "Groep"],
        dropna=False,
        as_index=False,
    )[variable].sum()

    # get the unique groups and samples.
    trend_group = df_eunis["Trendgroep"].unique()
    df_trend_group = read_system_config.read_groups_config(trend_group)
    df_unique_samples = df_eunis[
        ["Collectie_Referentie", "Ecotoop_EUNIS", "Trendgroep", "Monsterjaar_cluster"]
    ].drop_duplicates()

    # create a cross section of the samples and all the groups
    merged_df = pd.merge(df_unique_samples, df_trend_group, how="left", on="Trendgroep")
    df_bedek_groups_sample = pd.merge(
        merged_df, df_bedek_sample, how="left", on=["Collectie_Referentie", "Groep"]
    )

    # fill nodata with 0
    df_bedek_groups_sample[variable].fillna(0, inplace=True)

    # calculate the mean for each group
    df_bedek_groups = df_bedek_groups_sample.groupby(
        ["Monsterjaar_cluster", "Groep", "Groepkleur", "Ecotoop_EUNIS"],
        dropna=False,
        as_index=False,
    )[variable].mean()
    return df_bedek_groups


@log_decorator.log_factory(__name__)
def eunis_plot(
    df_eunis: pd.DataFrame, variable: str, output_path: str = ".//output"
) -> None:
    """Creates the plot for the EUNIS bedekking.

    Args:
        df_eunis (pd.DataFrame): the data with the EUNIS coverage.
        variable (str): column name to plot.
        output_path (str, optional): the path to write the plot to. Defaults to ".//output".
    """
    #  check if the EUNIS area has coverage
    eunis = df_eunis["Ecotoop_EUNIS"][0]

    plotter.PlotCreator(
        df=df_eunis,
        variable=variable,
        waterbody=eunis,
        output_folder=output_path,
        plot_style="bar",
        scale_column="Waterlichaam",
    ).create_bar_plot()
