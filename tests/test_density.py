"""Tests calculating the density of taxa."""

import logging
import os

import pandas as pd
import pytest
from pytest_lazyfixture import lazy_fixture


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))

logger = logging.getLogger(__name__)

from analysis import density


def test_prepare_density(
    input_prepare_density: pd.DataFrame, output_prepare_density: pd.DataFrame
) -> None:
    """Tests preparing density calculations by adding groups and filling with 0.

    Args:
        input_prepare_density (pd.DataFrame): Fixture with the input for preparing the calculations.
        output_prepare_density (pd.DataFrame): Fixture with the expected output for preparing.
    """
    result = density.prepare_density(input_prepare_density)
    pd.testing.assert_frame_equal(
        result.reset_index(drop=True), output_prepare_density.reset_index(drop=True)
    )


@pytest.mark.parametrize(
    ("group, with_groups, expected"),
    [
        (
            ["Waterlichaam"],
            False,
            lazy_fixture("output_aggregate_density_waterbody_no_group"),
        ),
        (
            ["Waterlichaam"],
            True,
            lazy_fixture("output_aggregate_density_waterbody_group"),
        ),
        (["Gebied"], False, lazy_fixture("output_aggregate_density_area_no_group")),
        (["Gebied"], True, lazy_fixture("output_aggregate_density_area_group")),
        (
            ["Strata", "Gebied"],
            False,
            lazy_fixture("output_aggregate_density_stratum_area_no_group"),
        ),
        (
            ["Strata", "Gebied"],
            True,
            lazy_fixture("output_aggregate_density_stratum_area_group"),
        ),
    ],
)
def test_aggregate_density(
    input_aggregate_density: pd.DataFrame,
    group: list,
    with_groups: bool,
    expected: pd.DataFrame,
) -> None:
    """Aggregates the densities to the requested level.

    Args:
        input_aggregate_density (pd.DataFrame): Fixture with the input benthos data.
        group (list): Lazy fixture with the columns to aggregate on.
        with_groups (bool): Lazy fixture with True if groups should be included, if not False.
        expected (pd.DataFrame): Lazy fixture with the expected outcome.
    """
    result = density.aggregate_density(
        input_aggregate_density, group, None, with_groups
    )
    pd.testing.assert_frame_equal(result, expected)
