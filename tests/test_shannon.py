"""Tests for calculating the Shannon index."""

import logging
import os

import pandas as pd


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))

from analysis import shannon


logger = logging.getLogger(__name__)


def test_calculate_shannon_by_area(
    input_shannon: pd.DataFrame, output_shannon_area: pd.DataFrame
) -> None:
    """Tests calculating the shannon by aggregating over the area.

    Args:
        input_shannon (pd.DataFrame): the input of the shannon calculations.
        output_shannon_area (pd.DataFrame): the output with the shannon indices.
    """
    shannon_aggregate_area = shannon.calculate_shannon_by_area(
        input_shannon, ["Gebied"], "Gebied", by_sample=False
    )

    pd.testing.assert_frame_equal(
        shannon_aggregate_area.reset_index(drop=True),
        output_shannon_area.reset_index(drop=True),
    )


def test_calculate_shannon_over_samples(
    input_shannon: pd.DataFrame, output_shannon_sample: pd.DataFrame
) -> None:
    """Tests calculating the shannon by aggregating over samples and then by area.

    Args:
        input_shannon (pd.DataFrame): the input of the shannon calculations.
        output_shannon_sample (pd.DataFrame): the output with the shannon indices.
    """
    shannon_aggregate_samples = shannon.calculate_shannon_over_samples(
        input_shannon, ["Waterlichaam"], None, by_sample=True
    )
    pd.testing.assert_frame_equal(
        shannon_aggregate_samples.reset_index(drop=True),
        output_shannon_sample.reset_index(drop=True),
    )
