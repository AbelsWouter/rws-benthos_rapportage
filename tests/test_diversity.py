"""Tests the levels of diversity and distribution of taxa."""

import logging
import os
from typing import List

import pandas as pd


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))

logger = logging.getLogger(__name__)

from preparation import diversity


def test_mark_diversity_species_main(
    input_mark_diversity: pd.DataFrame,
    diversity_levels: dict[str, List[str]],
    output_mark_diversity: pd.DataFrame,
) -> None:
    """Tests whether the diversity levels are correctly marked.

    Args:
        input_mark_diversity (pd.DataFrame): Fixture with the input for marking diversity levels.
        diversity_levels (dict[str, List[str]]): Fixture with the levels and corresponding columns.
        output_mark_diversity (pd.DataFrame): Fixture with the expected output of marking diversity.
    """
    result = diversity.mark_diversity_species(input_mark_diversity, diversity_levels)
    pd.testing.assert_frame_equal(result, output_mark_diversity)


def test_mark_diversity_species_uncounted(
    input_mark_diversity_species_uncounted: pd.DataFrame,
    diversity_levels: dict[str, List[str]],
    output_mark_diversity_species_uncounted: pd.DataFrame,
) -> None:
    """Tests whether the diversity levels are correctly marked with uncounted taxa.

    Args:
        input_mark_diversity_species_uncounted (pd.DataFrame): Fixture with the input for marking diversity levels.
        diversity_levels (dict[str, List[str]]): Fixture with the levels and corresponding columns.
        output_mark_diversity_species_uncounted (pd.DataFrame): Fixture with the expected output of marking diversity.
    """
    result = diversity.mark_diversity_species(
        input_mark_diversity_species_uncounted, diversity_levels
    )
    pd.testing.assert_frame_equal(result, output_mark_diversity_species_uncounted)


def test_distribute_taxa_abundances_n(
    input_distribute_abunances: pd.DataFrame,
    diversity_levels: dict[str, List[str]],
    output_distribute_n: pd.DataFrame,
) -> None:
    """Tests whether the number of taxa are correctly distributed.

    Args:
        input_distribute_abunances (pd.DataFrame): Fixture with the input for distributing numbers.
        diversity_levels (dict[str, List[str]]): Fixture with the levels and corresponding columns.
        output_distribute_n (pd.DataFrame): Fixture with the expected output for distributing numbers.
    """
    result = diversity.distribute_taxa_abundances(
        input_distribute_abunances, diversity_levels, "Aantal", "n_Soort"
    )
    pd.testing.assert_frame_equal(result, output_distribute_n)


def test_distribute_taxa_abundances_density(
    input_distribute_abunances: pd.DataFrame,
    diversity_levels: dict[str, List[str]],
    output_distribute_density: pd.DataFrame,
) -> None:
    """Tests whether the density of taxa are correctly distributed.

    Args:
        input_distribute_abunances (pd.DataFrame): Fixture with the input for distributing density.
        diversity_levels (dict[str, List[str]]): Fixture with the levels and corresponding columns.
        output_distribute_n (pd.DataFrame): Fixture with the expected output for distributing density.
    """
    result = diversity.distribute_taxa_abundances(
        input_distribute_abunances, diversity_levels, "Dichtheid_Aantal", "nm2_Soort"
    )
    pd.testing.assert_frame_equal(result, output_distribute_density)


def test_distribute_taxa_abundances_density_uncounted(
    input_distribute_density_species_uncounted: pd.DataFrame,
    diversity_levels: dict[str, List[str]],
    output_distribute_density_species_uncounted: pd.DataFrame,
) -> None:
    """Tests whether the density of taxa are correctly distributed for uncounted taxa.

    Args:
        input_distribute_abunances (pd.DataFrame): Fixture with the input for distributing density.
        diversity_levels (dict[str, List[str]]): Fixture with the levels and corresponding columns.
        output_distribute_n (pd.DataFrame): Fixture with the expected output for distributing density.
    """
    result = diversity.distribute_taxa_abundances(
        input_distribute_density_species_uncounted,
        diversity_levels,
        "Dichtheid_Aantal",
        "nm2_Soort",
    )
    pd.testing.assert_frame_equal(result, output_distribute_density_species_uncounted)
