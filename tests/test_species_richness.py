"""Tests calculating the species richness."""

import pandas as pd

from analysis import species_richness


def test_species_richness_sample_area(
    input_species_richness: pd.DataFrame, output_species_rich_sample: pd.DataFrame
) -> None:
    """Tests the species richness over samples and area.

    Args:
        input_analysis_main (pd.DataFrame): Fixture with the benthos input data.
        output_species_rich_sample (pd.DataFrame): Fixture with the expected output.
    """
    result = species_richness.species_richness_over_samples(
        input_species_richness, ["Waterlichaam"], "Waterlichaam"
    )

    pd.testing.assert_frame_equal(result, output_species_rich_sample)


def test_species_richness_area(
    input_species_richness: pd.DataFrame, output_species_rich_area: pd.DataFrame
) -> None:
    """Tests the species richness over area.

    Args:
        input_analysis_main (pd.DataFrame): Fixture with the benthos input data.
        output_species_rich_sample (pd.DataFrame): Fixture with the expected output.
    """
    result = species_richness.species_richness_by_area(
        input_species_richness, ["Waterlichaam"], "Waterlichaam"
    )

    pd.testing.assert_frame_equal(result, output_species_rich_area)
