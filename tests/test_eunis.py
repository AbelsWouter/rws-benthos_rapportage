"""Tests the calculation and plots of the EUNIS."""

import logging
import os
from pathlib import Path

import pandas as pd


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))

logger = logging.getLogger(__name__)

from analysis import eunis


def test_calculate_eunis(input_eunis: pd.DataFrame, output_eunis: pd.DataFrame) -> None:
    """Tests calculating the EUNIS.

    Args:
        input_eunis (pd.DataFrame): input benthos data with EUNIS column filled.
        output_eunis (pd.DataFrame): output benthos data.
    """
    result = eunis.calculate_eunis_coverage(input_eunis, "Bedekking")
    pd.testing.assert_frame_equal(result, output_eunis)


def test_plot_eunis(output_eunis: pd.DataFrame, tmp_path: Path) -> None:
    """Tests creating the plot of the EUNIS.

    Args:
        output_eunis (pd.DataFrame): the input for the barplot.
        tmp_path (Path): the temporary path.
    """
    output_folder = tmp_path / "output"
    output_folder.mkdir()
    generated_figure_path = output_folder / "Eunis a - Bedekking - groepen.png"
    eunis.eunis_plot(output_eunis, variable="Bedekking", output_path=output_folder)

    assert generated_figure_path.exists()


def test_plot_eunis_density(input_eunis: pd.DataFrame, tmp_path: Path) -> None:
    """Tests creating the plot of the EUNIS densities.

    Args:
        output_eunis (pd.DataFrame): the input for the barplot.
        tmp_path (Path): the temporary path.
    """
    output_folder = tmp_path / "output"
    output_folder.mkdir()
    generated_figure_path = output_folder / "Eunis a - Dichtheid_Aantal - groepen.png"

    output_eunis = eunis.calculate_eunis_coverage(input_eunis, "Dichtheid_Aantal")
    eunis.eunis_plot(
        output_eunis, variable="Dichtheid_Aantal", output_path=output_folder
    )

    assert generated_figure_path.exists()
