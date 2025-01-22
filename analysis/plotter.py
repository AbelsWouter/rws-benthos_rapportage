"""Class for generating bar plots based on the input data and the configuration."""

"""
# File: plotter.py
# Author(s): M. Japink (m.japink@waardenburg.eco) & J. Haringa (j.haringa@waardenburg.eco)
# Creation date: 17-02-2024
# Last modification: 20-02-2024
# Python v3.12.1
"""


import logging
import os
import warnings

import numpy as np
import pandas as pd
from plotnine import aes
from plotnine import element_blank
from plotnine import element_text
from plotnine import geom_col
from plotnine import geom_line
from plotnine import geom_point
from plotnine import ggplot
from plotnine import guide_legend
from plotnine import guides
from plotnine import labs
from plotnine import scale_color_manual
from plotnine import scale_fill_manual
from plotnine import scale_x_discrete
from plotnine import scale_y_continuous
from plotnine import theme
from plotnine import theme_light
from plotnine.exceptions import PlotnineWarning

from preparation import read_system_config
from preparation import utility


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))

logger = logging.getLogger(__name__)
logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)

# Filter out the warning for removed rows containing missing values
warnings.filterwarnings(
    "ignore",
    message="geom_point : Removed.*rows containing missing values",
    category=PlotnineWarning,
)
warnings.filterwarnings(
    "ignore",
    message="position_stack : Removed.*rows containing missing values.",
    category=PlotnineWarning,
)


class PlotCreator:
    """
    Class to handle all related to plotting.
    """

    __slots__ = (
        "df",
        "variable",
        "waterbody",
        "output_folder",
        "plot_style",
        "scale_name",
        "scale_column",
        "output_filename",
        "plot_title",
        "config_titles",
        "config_fill_missing_years",
        "config_colors",
        "y_title",
        "color_dict",
        "df_plot",
        "generate_output",
    )

    def __init__(
        self,
        df: pd.DataFrame,
        variable: str,
        waterbody: str,
        output_folder: str,
        plot_style: str,
        scale_name: str = None,
        scale_column: str = None,
    ):
        """Constructs all the necessary attributes for the PlotCreator object.

        Args:
            df (pd.DataFrame, required): Dataframe containing the data to plot
            variable (str, required): The variable to plot
            waterbody (str, required): The waterbody to plot
            output_folder (str, required): The folder to save the output
            plot_style (str, required): The style of the plot (bar or scatter)
            scale_name (str, optional): The name of the scale, defaults to None
            scale_column (str, optional): The column to use for the scale, defaults to None
        """

        self.df = df.copy()
        self.variable = variable
        self.waterbody = waterbody
        self.output_folder = output_folder
        self.plot_style = plot_style
        self.scale_name = scale_name
        self.scale_column = scale_column

        self.output_filename = None
        self.plot_title = None
        self.config_titles = None
        self.config_fill_missing_years = True
        self.config_colors = None
        self.y_title = None
        self.color_dict = None
        self.df_plot = None
        self.generate_output = True

        # read the configuration
        self.read_config_titles()
        self.read_config_fill_missing_years()
        if self.plot_style == "scatter":
            self.read_config_color_dict()

        self.filter_data()
        self.check_has_data()
        self.check_enough_data()

    def read_config_titles(self):
        """Read the plot configuration from the global_variables.yaml file."""
        self.config_titles = read_system_config.read_yaml_configuration(
            f"plot_config.titles.{self.variable}", "global_variables.yaml"
        )

    def read_config_fill_missing_years(self):
        """Read the plot configuration from the global_variables.yaml file."""
        self.config_fill_missing_years = read_system_config.read_yaml_configuration(
            f"plot_config.settings.fill_missing_years_{self.plot_style}",
            "global_variables.yaml",
        )

    def read_config_color_dict(self):
        """Read the plot configuration from the global_variables.yaml file.
        for the scatter plot"""
        self.config_colors = read_system_config.read_yaml_configuration(
            "colorblind_friendly", "global_variables.yaml"
        )

    def filter_data(self):
        """Filter only values > 0 and drop NaN values from the data to plot.
        Mean per year can never be 0.0, so this is a valid filter for the data."""
        if len(self.df) == 0:
            self.df_plot = self.df
            return
        self.df_plot = self.df.dropna(subset=[self.variable])
        self.df_plot = self.df_plot[self.df_plot[self.variable] != 0.0]

    def check_has_data(self):
        """Check if the data has any data to plot."""
        if len(self.df_plot) == 0:
            logger.info(
                f"{self.plot_style} plot - Voor {self.waterbody}: {self.variable} is geen data beschikbaar."
            )
            self.generate_output = False

    def check_enough_data(self):
        """Check if the data has enough years to plot, 3 or more years."""
        if not self.generate_output:
            return

        if len(self.df_plot["Monsterjaar_cluster"].unique()) < 3:
            logger.info(
                f"{self.plot_style} plot - Voor {utility.coalesce(self.scale_name, self.waterbody)} "
                f": {self.variable} is te weinig data beschikbaar voor een grafiek. "
                "Vanaf drie meetjaren worden de als 'trend' gemarkeerde monsters gevisualiseerd."
            )
            self.generate_output = False

    def check_enough_colors(self):
        """Check if the config has enough colors to plot the data."""
        if len(self.df_plot[self.scale_column].unique()) > len(self.config_colors):
            scale_list = self.df_plot[self.scale_column].unique()
            logger.info(
                f"De data-selectie voor {self.scale_column}: {scale_list} - {self.variable} "
                f"bevat meer items dan de {len(self.config_colors)} geconfigureerde kleuren. "
                "Wellicht is een andere visualisatie beter geschikt. "
            )
            self.generate_output = False

    def set_legend_title(self):
        """Change '_' to '-' in the column name and self.scale_column."""
        self.df.rename(
            columns={self.scale_column: self.scale_column.replace("_", "-")},
            inplace=True,
        )
        self.df_plot.rename(
            columns={self.scale_column: self.scale_column.replace("_", "-")},
            inplace=True,
        )
        self.scale_column = self.scale_column.replace("_", "-")

    def set_plot_title(self):
        """Create the plot title based on the plot configuration and the group name.
        Scatter and bar plots have different plot titles.
        """
        self.plot_title = self.config_titles["plot_title"]
        if self.plot_style == "scatter":
            if self.scale_column != "Waterlichaam":
                self.plot_title += " - " + self.waterbody

        if self.plot_style == "bar":
            self.plot_title += " - " + self.waterbody
            if self.scale_name is not None and self.scale_name != self.waterbody:
                self.plot_title += " " + self.scale_name

        if "Seizoen" in self.df:
            for season in self.df["Seizoen"].unique():
                if season != "geen_seizoenen":
                    self.plot_title += " (" + season + ")"

    def set_y_title(self):
        """Create the y title based on the plot configuration."""
        self.y_title = self.config_titles["y_title"]

    def create_color_dict(self):
        """Create the color dictionary based on the group and group color."""
        self.color_dict = self.df.set_index("Groep")["Groepkleur"].to_dict()

    def set_output_filename(self):
        """Set the output filename based on the input parameters"""
        self.output_filename = self.waterbody + " - " + self.variable
        if self.scale_name is not None and self.scale_name != self.waterbody:
            self.output_filename += " - " + self.scale_name.replace("/", "_")
        if self.plot_style == "bar":
            self.output_filename += " - groepen"
        self.output_filename += ".png"
        self.output_filename = utility.valid_path(self.output_filename)

    def set_output_folder(self):
        """Add output_filename to the output folder."""
        self.set_output_filename()
        self.output_folder = os.path.join(self.output_folder, self.output_filename)

    def fill_missing_years(self):
        """Fill the missing years in the data with Nan."""
        if not self.config_fill_missing_years:
            return

        # Get the unique rows, except for the variable and sample year cluster columns
        groups = self.df_plot.drop(columns=[self.variable, "Monsterjaar_cluster"])
        unique_row = groups.drop_duplicates()

        all_years = []
        self.df_plot["Monsterjaar_cluster"] = self.df_plot[
            "Monsterjaar_cluster"
        ].astype(str)
        for cluster in self.df_plot["Monsterjaar_cluster"].drop_duplicates():
            if "-" in cluster:
                start, end = map(int, cluster.split("-"))
                all_years.extend(range(start, end + 1))
            else:
                all_years.append(int(cluster))

        # create a full year range
        full_range = list(range(min(all_years), max(all_years) + 1))

        # add missing years to the data, setting the variable to 0
        for year in full_range:
            if year not in all_years:
                # add year as value to year_cluster column in unique_row
                new_row = unique_row.copy()
                new_row["Monsterjaar_cluster"] = str(year)
                new_row[self.variable] = np.NaN
                self.df_plot = pd.concat(
                    [self.df_plot, new_row],
                    axis=0,
                )

    def scale_y_axis(self):
        """Scale the y axis based on the max value of the variable."""
        max_value = self.df_plot[self.variable].max()
        if max_value > 9999:
            self.df_plot[self.variable] /= 1000
            if "mg" in self.y_title:
                self.y_title = self.y_title.replace("mg", "g")
            if "n" in self.y_title:
                self.y_title = self.y_title.replace(")", " x 1000)")

    def create_bar_plot(self):
        """Create the bar plot based on the input data and the configuration."""

        if not self.generate_output:
            return

        self.create_color_dict()
        self.set_plot_title()
        self.set_y_title()
        self.set_output_folder()
        self.fill_missing_years()
        self.scale_y_axis()
        self.write_bar_plot()

    def create_scatter_plot(self):
        """Create the scatter plot based on the input data and the configuration."""

        if not self.generate_output:
            return

        # check enough data and return if not enough
        self.check_enough_colors()

        if not self.generate_output:
            return

        self.set_plot_title()
        self.set_y_title()
        self.set_legend_title()
        self.set_output_folder()
        self.fill_missing_years()
        self.scale_y_axis()
        self.write_scatter_plot()

    def write_bar_plot(self):
        """write the bar plot based on the input data and the configuration."""

        plot = (
            ggplot(data=self.df_plot)
            + aes(x="Monsterjaar_cluster", y=self.variable)
            + scale_x_discrete()
            + scale_y_continuous()
            + theme_light()
            + theme(axis_text_x=element_text(angle=45, hjust=1))
            + theme(plot_title=element_text(hjust=0.5))
            + theme(axis_title_x=element_blank())
            + geom_col(aes(fill="Groep", group=1))
            + scale_fill_manual(
                values=self.color_dict, labels={group: group for group in self.df}
            )
            + labs(
                title=self.plot_title,
                y=self.y_title,
                fill="Groep",
            )
        )

        plot = plot + guides(fill=guide_legend(reverse=True))
        plot.save(
            self.output_folder,
            dpi=600,
            verbose=False,
        )

    def write_scatter_plot(self):
        """write the scatter plot based on the input data and the configuration."""

        max_value = self.df_plot[self.variable].max()
        plot = (
            ggplot(data=self.df_plot)
            + aes(x="Monsterjaar_cluster", y=self.variable, fill=self.scale_column)
            + scale_x_discrete()
            + scale_y_continuous(limits=[0, (max_value * 1.01)])
            + theme_light()
            + geom_line(aes(color=self.scale_column, group=self.scale_column))
            + geom_point(aes(color=self.scale_column, shape=self.scale_column))
            + scale_fill_manual(self.config_colors)
            + scale_color_manual(self.config_colors)
            + theme(axis_text_x=element_text(angle=45, hjust=1))
            + theme(axis_title_x=element_blank())
            + theme(plot_title=element_text(hjust=0.5))
            + labs(title=self.plot_title, y=self.y_title, color=self.scale_column)
        )
        plot.save(self.output_folder, dpi=600, verbose=False)
