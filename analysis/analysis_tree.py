"""Figures and tables are written in a nested folder structure based on (sub)-area and season."""

"""
# File: analysis_tree.py
# Author(s): M. Japink (m.japink@waardenburg.eco) & J. Haringa (j.haringa@waardenburg.eco)
# Creation date: 21-01-2023
# Last modification: 20-02-2024
# Python v3.12.1
"""

import logging
import os
from typing import Callable

import pandas as pd


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))

from analysis import density
from analysis import eunis
from analysis import margalef
from analysis import new_disappeared_species
from analysis import plotter
from analysis import shannon
from analysis import species_richness
from analysis import tables
from preparation import log_decorator
from preparation import read_system_config
from preparation import utility


logger = logging.getLogger(__name__)


@log_decorator.log_factory(__name__)
def analysis_tree(
    df: pd.DataFrame,
    func: Callable[[pd.DataFrame, list, str, bool], pd.DataFrame],
    plottype: str = "scatter",
    variable: str = None,
) -> None:
    """Function to create the nested folder structure.
    On every level it calls the given function with the given variable to fill with plots and tables.

    Args:
        df (pd.DataFrame): dataframe with the data.
        func (Callable[[pd.DataFrame, list, str, bool], pd.DataFrame]): function to apply to the data.
        plottype (str, optional): Type of plot to create. Defaults to "scatter".
        variable (str, optional): Variable to analyse. Defaults to None.

    Returns:
        None
    """

    # get output location from config
    output_path = read_system_config.read_yaml_configuration(
        "output_path", "global_variables.yaml"
    )
    # loop through all waterbody's
    for waterbody in df["Waterlichaam"].unique():
        df_wb = df[
            (df["Gebruik"] == "trend") & (df["Waterlichaam"] == waterbody)
        ].copy()

        if len(df_wb) == 0:
            logger.warning(
                f"Er is voor het waterlichaam '{waterbody}' geen trend data beschikbaar."
            )
            continue

        # check if the waterbody has seasons
        has_season = df["Heeft_Seizoen"].iloc[0]
        if not has_season:
            df_wb["Seizoen"] = "geen_seizoenen"

        for season in df_wb["Seizoen"].unique():
            df_wb_season = df_wb[df_wb["Seizoen"] == season]
            if len(df_wb_season) == 0:
                logger.warning(
                    f"Er is voor het waterlichaam '{waterbody}' geen trend data beschikbaar voor seizoen '{season}'."
                )
                continue

            # extend path with waterbody and season if nessesary
            output_path_wb = os.path.join(output_path, waterbody)
            if has_season:
                output_path_wb = os.path.join(output_path_wb, season)
            utility.check_and_make_output_subfolder(output_path_wb)

            # define the remove_columns for the pivotted tables
            remove_cols = None
            if variable == "Dichtheid_Aantal":
                remove_cols = ["Dichtheid_Massa", "Aantal_Monsters"]
            if variable == "Dichtheid_Massa":
                remove_cols = ["Dichtheid_Aantal", "Aantal_Monsters"]

            if variable is not None and func is not None:
                if "scatter" in plottype:
                    # create output for waterbody
                    if variable == "Soortenrijkdom_Monster":
                        result = func(
                            df_wb_season, ["Waterlichaam"], "Waterlichaam", True
                        )
                        if len(result) == 0:
                            continue

                    else:
                        result = func(
                            df_wb_season, ["Waterlichaam"], "Waterlichaam", False
                        )

                    plotter.PlotCreator(
                        df=result,
                        variable=variable,
                        waterbody=waterbody,
                        output_folder=output_path_wb,
                        plot_style="scatter",
                        scale_column="Waterlichaam",
                    ).create_scatter_plot()
                    utility.export_df(
                        result,
                        os.path.join(output_path_wb, f"{waterbody} - {variable} .xlsx"),
                    )
                if "bar" in plottype:
                    result = func(df_wb_season, ["Waterlichaam"], None, True)
                    if len(result) == 0:
                        continue

                    plotter.PlotCreator(
                        df=result,
                        variable=variable,
                        waterbody=waterbody,
                        output_folder=output_path_wb,
                        plot_style="bar",
                        scale_name=waterbody,
                    ).create_bar_plot()

                    utility.export_df(
                        result,
                        os.path.join(
                            output_path_wb, f"{waterbody} - {variable} - groepen.xlsx"
                        ),
                    )
            else:
                pass

            # loop over all subplot levels
            subset_dict = read_system_config.read_yaml_configuration(
                "subplots_levels", "global_variables.yaml"
            )
            for level, columns in subset_dict.items():
                # replace in the columns the NA values with 'onbekend' when the column contains values
                for col in columns:
                    if df_wb_season[col].notnull().any():
                        df_wb_season = df_wb_season.copy()
                        df_wb_season.loc[:, col] = df_wb_season.loc[:, col].fillna(
                            "onbekend"
                        )

                # Check if all level columns have values
                if not all(df_wb_season[col].notnull().all() for col in columns):
                    logger.debug(
                        "Level has one or more empty columns. No output will be created."
                    )
                    continue

                # create a combined column name
                if len(columns) > 1:
                    combined_column_name = "-".join(columns)
                else:
                    combined_column_name = columns[0]

                # create a new combined column
                if len(columns) > 1:
                    df_wb_season = df_wb_season.copy()
                    df_wb_season.loc[:, combined_column_name] = df_wb_season[
                        columns
                    ].apply(lambda row: "-".join(map(str, row)), axis=1)

                # create folder for subplot level
                output_path_wb_level = os.path.join(output_path_wb, level)
                utility.check_and_make_output_subfolder(output_path_wb_level)

                if variable is not None and func is not None:
                    if "scatter" in plottype:
                        # create output for combined level
                        if variable == "Soortenrijkdom_Monster":
                            result = func(df_wb_season, columns, True)
                            if len(result) == 0:
                                continue
                        else:
                            result = func(df_wb_season, columns, level, False)
                            if len(result) == 0:
                                continue
                        result_pivot = tables.create_pivot_table(
                            result, combined_column_name, variable, remove_cols
                        )

                        plotter.PlotCreator(
                            df=result,
                            variable=variable,
                            waterbody=waterbody,
                            output_folder=output_path_wb_level,
                            plot_style="scatter",
                            scale_name=combined_column_name,
                            scale_column=combined_column_name,
                        ).create_scatter_plot()

                        utility.export_df(
                            result_pivot,
                            os.path.join(
                                output_path_wb_level,
                                utility.valid_path(
                                    f"{waterbody} - {variable} - {level} - pivot.xlsx"
                                ),
                            ),
                        )
                        utility.export_df(
                            result,
                            os.path.join(
                                output_path_wb_level,
                                utility.valid_path(
                                    f"{waterbody} - {variable} - {level}.xlsx"
                                ),
                            ),
                        )

                    # Iterate over the items within the level
                    grouped = result.groupby(combined_column_name)
                    for item_name, item_df in grouped:
                        filename = item_name.replace("/", "_")
                        if "scatter" in plottype:
                            plotter.PlotCreator(
                                df=item_df,
                                variable=variable,
                                waterbody=waterbody,
                                output_folder=output_path_wb_level,
                                plot_style="scatter",
                                scale_name=item_name,
                                scale_column=combined_column_name,
                            ).create_scatter_plot()

                    if "bar" in plottype:
                        result_groups = func(df_wb_season, columns, None, True)
                        if len(columns) > 1:
                            result_groups = result_groups.copy()
                            result_groups.loc[:, combined_column_name] = result_groups[
                                columns
                            ].apply(lambda row: "-".join(map(str, row)), axis=1)
                        grouped_groups = result_groups.groupby(combined_column_name)
                        for item_name, item_df in grouped_groups:
                            filename = item_name.replace("/", "_")

                            plotter.PlotCreator(
                                df=item_df,
                                variable=variable,
                                waterbody=waterbody,
                                output_folder=output_path_wb_level,
                                plot_style="bar",
                                scale_name=item_name,
                            ).create_bar_plot()

                            utility.export_df(
                                item_df,
                                os.path.join(
                                    output_path_wb_level,
                                    f"{waterbody} - {variable} - {filename} - groepen.xlsx",
                                ),
                            )
                else:
                    pass


def analysis_main(df: pd.DataFrame) -> bool:
    """Main function for analysis. This function defines what tables and figures are written.

    Args:
        df (pd.DataFrame): dataframe with the data.

    Returns:
        bool: True if analysis is completed.
    """

    ### main tables ###
    tables.export_samples_a_year(df)
    new_disappeared_species.main_new_disappeared_returned_species(df)
    tables.make_species_list(df, year=None)
    msg = "Soortenlijst: gereed"
    logger.info(msg)
    print(msg)

    ### trend analysis ###
    # select only trend data
    df_trend = df[df["Gebruik"] == "trend"].copy()

    # # diversity indexes
    analysis_tree(
        df_trend,
        species_richness.species_richness_over_samples,
        variable="Soortenrijkdom_Monster",
        plottype="scatter",
    )
    analysis_tree(
        df_trend,
        species_richness.species_richness_by_area,
        variable="Soortenrijkdom",
        plottype="scatter",
    )
    analysis_tree(
        df_trend,
        shannon.calculate_shannon_over_samples,
        variable="Shannon_Monster",
        plottype="scatter",
    )
    analysis_tree(
        df_trend,
        shannon.calculate_shannon_by_area,
        variable="Shannon",
        plottype="scatter",
    )
    analysis_tree(
        df_trend,
        margalef.calculate_margalef_over_samples,
        plottype="scatter",
        variable="Margalef_Monster",
    )

    msg = "Diversiteit: gereed"
    print(msg)
    logger.info(msg)

    # densities
    # select the correct support unit
    df_support = df_trend[df_trend["Support_Eenheid"] == "m2"]

    df_density = density.prepare_density(df_support)

    df_density = df_density[df_density["Support_Eenheid"] == "m2"]
    analysis_tree(
        df_density,
        density.aggregate_density,
        plottype="bar/scatter",
        variable="Dichtheid_Aantal",
    )
    analysis_tree(
        df_density,
        density.aggregate_density,
        plottype="bar/scatter",
        variable="Dichtheid_Massa",
    )

    msg = "Dichtheid: gereed"
    print(msg)
    logger.info(msg)

    # # eunis
    # loop over all EUNIS areas
    for eunis_item in df_trend["Ecotoop_EUNIS"].unique():
        df_eunis = df_trend[df_trend["Ecotoop_EUNIS"] == eunis_item]
        if len(df_eunis) > 0:
            # coverage ('bedekking')
            df_eunis_bedek = eunis.calculate_eunis_coverage(df_eunis, "Bedekking")
            eunis.eunis_plot(df_eunis_bedek, "Bedekking")

            # densities per eunis
            df_eunis_density = eunis.calculate_eunis_coverage(
                df_eunis, "Dichtheid_Aantal"
            )
            eunis.eunis_plot(df_eunis_density, "Dichtheid_Aantal")

    return True
