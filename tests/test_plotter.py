"""Tests creating the plots based on the Benthos data."""
import logging
from pathlib import Path

import pandas as pd

from analysis import plotter


logger = logging.getLogger(__name__)


def test_barplot_creator_ok(
    input_barplot_dichtheid_aantal: pd.DataFrame,
    output_barplot_fill_missing_years: pd.DataFrame,
    tmp_path: Path,
) -> None:
    """Test the BarPlotCreator class."""
    # Specify the output path within the temporary directory
    output_folder = tmp_path / "output"
    output_folder.mkdir()
    generated_figure_path = output_folder / "Zandmaas - Dichtheid_Aantal - groepen.png"
    variable = "Dichtheid_Aantal"

    bar_plot_creator = plotter.PlotCreator(
        df=input_barplot_dichtheid_aantal,
        variable=variable,
        waterbody="Zandmaas",
        output_folder=output_folder,
        plot_style="bar",
    )
    bar_plot_creator.filter_data()

    bar_plot_creator.set_y_title()
    assert bar_plot_creator.y_title == "Gemiddelde dichtheid (n/m²)"

    bar_plot_creator.set_plot_title()
    assert (
        bar_plot_creator.plot_title == "Gemiddelde dichtheid aantal - Zandmaas (najaar)"
    )

    bar_plot_creator.fill_missing_years()

    pd.testing.assert_frame_equal(
        bar_plot_creator.df_plot.reset_index(drop=True),
        output_barplot_fill_missing_years.reset_index(drop=True),
    )

    bar_plot_creator.create_color_dict()
    assert bar_plot_creator.color_dict == {
        "Bivalvia-overig": "#708090",
        "Crustacea-Amphipoda": "#A52A2A",
        "Crustacea-Corophiidae": "#E6E6FA",
        "Crustacea-Isopoda": "#808000",
        "Diptera-Chironomidae": "#228B22",
        "Dreissenidae": "#4B0082",
        "Gastropoda": "#CC79A7",
        "Oligochaeta": "#F0E442",
        "Overig": "#0072B2",
    }

    bar_plot_creator.create_bar_plot()
    assert generated_figure_path.exists()


def test_barplot_creator_no_data(tmp_path: Path) -> None:
    """Test the BarPlotCreator class when there is no data."""

    # Specify the output path within the temporary directory

    df_input = pd.DataFrame(
        columns=[
            "Waterlichaam",
            "Groep",
            "Groepkleur",
            "Monsterjaar_cluster",
            "Dichtheid_Aantal",
        ]
    )
    output_folder = tmp_path / "output"
    output_folder.mkdir()
    generated_figure_path = output_folder / "Zandmaas - Dichtheid_Aantal - groepen.png"
    variable = "Dichtheid_Aantal"

    bar_plot_creator = plotter.PlotCreator(
        df=df_input,
        variable=variable,
        waterbody="Zandmaas",
        output_folder=output_folder,
        plot_style="bar",
    )
    bar_plot_creator.filter_data()
    bar_plot_creator.check_has_data()
    assert bar_plot_creator.generate_output is False

    bar_plot_creator.create_bar_plot()
    assert not generated_figure_path.exists()


def test_barplot_creator_not_enough_data(
    input_barplot_dichtheid_aantal: pd.DataFrame, tmp_path: Path
) -> None:
    """Test the BarPlotCreator class."""

    # filter only 3 rows from the input dataframe
    df_input = input_barplot_dichtheid_aantal.head(2)
    output_folder = tmp_path / "output"
    output_folder.mkdir()
    generated_figure_path = output_folder / "Zandmaas - Dichtheid_Aantal - groepen.png"
    variable = "Dichtheid_Aantal"

    bar_plot_creator = plotter.PlotCreator(
        df=df_input,
        variable=variable,
        waterbody="Zandmaas",
        output_folder=output_folder,
        plot_style="bar",
    )

    bar_plot_creator.filter_data()
    bar_plot_creator.check_enough_data()
    assert bar_plot_creator.generate_output is False

    bar_plot_creator.create_bar_plot()
    assert not generated_figure_path.exists()


def test_bar_plot_creator_no_fill(
    input_barplot_dichtheid_aantal: pd.DataFrame,
    output_barplot_no_fill_missing_years: pd.DataFrame,
    tmp_path: Path,
) -> None:
    """Tests if the bar plot creator respects the setting for not filling missing years."""

    # Specify the output path within the temporary directory
    output_folder = tmp_path / "output"
    output_folder.mkdir()
    generated_figure_path = output_folder / "Zandmaas - Dichtheid_Aantal - groepen.png"

    variable = "Dichtheid_Aantal"

    bar_plot_creator = plotter.PlotCreator(
        df=input_barplot_dichtheid_aantal,
        variable=variable,
        waterbody="Zandmaas",
        output_folder=output_folder,
        plot_style="bar",
    )
    bar_plot_creator.filter_data()
    bar_plot_creator.config_fill_missing_years = False
    bar_plot_creator.fill_missing_years()

    pd.testing.assert_frame_equal(
        bar_plot_creator.df_plot.reset_index(drop=True),
        output_barplot_no_fill_missing_years.reset_index(drop=True),
    )

    bar_plot_creator.create_bar_plot()
    assert generated_figure_path.exists()


def test_scatter_plot_titles(
    input_scatterplot_dichtheid_aantal: pd.DataFrame, tmp_path: Path
) -> None:
    """Test if the scatter plot creator sets the titles correctly."""
    output_folder = tmp_path / "output"
    output_folder.mkdir()

    variable = "Dichtheid_Aantal"

    scatter_plot_creator = plotter.PlotCreator(
        df=input_scatterplot_dichtheid_aantal,
        variable=variable,
        waterbody="Zandmaas",
        output_folder=output_folder,
        plot_style="scatter",
        scale_column="Gebied",
    )

    scatter_plot_creator.set_y_title()
    assert scatter_plot_creator.y_title == "Gemiddelde dichtheid (n/m²)"

    scatter_plot_creator.set_output_filename()
    assert scatter_plot_creator.output_filename == "Zandmaas - Dichtheid_Aantal.png"

    scatter_plot_creator.set_output_folder()
    assert "Zandmaas - Dichtheid_Aantal.png" in scatter_plot_creator.output_folder

    scatter_plot_creator.set_plot_title()
    assert (
        scatter_plot_creator.plot_title
        == "Gemiddelde dichtheid aantal - Zandmaas (najaar) (voorjaar)"
    )


def test_scatter_plot_number_of_colors() -> None:
    """Test if the scatter plot creator checks if there are enough colors."""
    scatter_plot_creator = plotter.PlotCreator(
        df=pd.DataFrame(
            {
                "Waterlichaam": 10 * ["test"],
                "Gebied": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
                "Monsterjaar_cluster": 10 * [2032],
                "Dichtheid_Aantal": 10 * [4],
            }
        ),
        variable="Dichtheid_Aantal",
        waterbody="Zandmaas",
        output_folder="iets",
        plot_style="scatter",
        scale_column="Gebied",
    )

    scatter_plot_creator.check_enough_colors()
    assert scatter_plot_creator.generate_output is False


def test_scatter_plot_write(
    input_scatterplot_dichtheid_aantal: pd.DataFrame, tmp_path: Path
) -> None:
    """Test if a plot is written to the output folder."""
    output_folder = tmp_path / "output"
    output_folder.mkdir()
    generated_figure_path = output_folder / "Zandmaas - Dichtheid_Aantal.png"

    variable = "Dichtheid_Aantal"

    scatter_plot_creator = plotter.PlotCreator(
        df=input_scatterplot_dichtheid_aantal,
        variable=variable,
        waterbody="Zandmaas",
        output_folder=output_folder,
        plot_style="scatter",
        scale_column="Gebied",
    )

    scatter_plot_creator.create_scatter_plot()
    assert generated_figure_path.exists()
