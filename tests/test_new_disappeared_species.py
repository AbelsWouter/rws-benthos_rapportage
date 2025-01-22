"""Tests the creation of new, disappeared and returned species."""

import logging
import os

import pandas as pd


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))

logger = logging.getLogger(__name__)

from analysis import new_disappeared_species
from analysis import tables
from tests import test_tables


def test_merge_new_disappeared_returned(
    input_merge_NDR: pd.DataFrame,
    output_merge_sample: pd.DataFrame,
    output_merge_new: pd.DataFrame,
    output_merge_returned: pd.DataFrame,
    output_merge_disappeared: pd.DataFrame,
) -> None:
    """Tests merging the new, disappeared and returned species, and the samples.

    Args:
        input_merge_NDR (pd.DataFrame): input for the new, disappeared, returned.
        output_merge_sample (pd.DataFrame): output of the samples.
        output_merge_new (pd.DataFrame): output of the new species.
        output_merge_returned (pd.DataFrame): output of the returned species.
        output_merge_disappeared (pd.DataFrame): output of the disappeared species.
    """
    (
        result_samples,
        result_new,
        result_returned,
        result_disappeared,
    ) = new_disappeared_species.merge_new_disappeared_returned(
        input_merge_NDR,
        waterbody=["Noordzee-overig"],
        min_year=tables.get_min_year(["Noordzee-overig"]),
        max_year=input_merge_NDR["Monsterjaar"].max(),
    )
    result_samples = result_samples.rename_axis(None, axis=1)
    result_new = result_new.rename_axis(None, axis=1)
    result_returned = result_returned.rename_axis(None, axis=1)
    result_disappeared = result_disappeared.rename_axis(None, axis=1)

    cols = {
        col: int(col) if col.isdigit() else col for col in output_merge_sample.columns
    }
    output_merge_sample = output_merge_sample.rename(columns=cols)
    output_merge_new = output_merge_new.rename(columns=cols)
    output_merge_returned = output_merge_returned.rename(columns=cols)
    output_merge_disappeared = output_merge_disappeared.rename(columns=cols)

    pd.testing.assert_frame_equal(result_samples, output_merge_sample)
    pd.testing.assert_frame_equal(result_new, output_merge_new)
    pd.testing.assert_frame_equal(result_returned, output_merge_returned)
    pd.testing.assert_frame_equal(result_disappeared, output_merge_disappeared)


def test_mark_no_exotic(
    input_no_exotic: pd.DataFrame, output_no_exotic: pd.DataFrame
) -> None:
    """Tests marking exotic species where there are none.

    Args:
        input_no_exotic (pd.DataFrame): input without exotic species.
        output_no_exotic (pd.DataFrame): expected output without marked species.
    """
    result = new_disappeared_species.mark_new_exotic_species(
        input_no_exotic, input_no_exotic["Monsterjaar"].max()
    )
    pd.testing.assert_frame_equal(result, output_no_exotic)


def test_mark_exotic(input_exotic: pd.DataFrame, output_exotic: pd.DataFrame) -> None:
    """Tests marking exotic species with exotics in the input.

    Args:
        input_no_exotic (pd.DataFrame): input with exotic species.
        output_no_exotic (pd.DataFrame): expected output with marked exotic species.
    """
    result = new_disappeared_species.mark_new_exotic_species(
        input_exotic, input_exotic["Monsterjaar"].max()
    )

    pd.testing.assert_frame_equal(
        result.reset_index(drop=True), output_exotic.reset_index(drop=True)
    )


def test_main_NDR(input_main_NDR: pd.DataFrame) -> None:
    """Tests the integration of the new, disappeared, returned (NDR) species.

    Args:
        input_main_NDR (pd.DataFrame): input for the main function.
    """
    new_disappeared_species.main_new_disappeared_returned_species(input_main_NDR)
    test_tables.compare_excel_files(
        "./tests/fixtures/new_disappeared_returned/output_main_NDR.xlsx",
        "./output/Noordzee-overig/Noordzee-overig - Nieuw_terug_verdwenen.xlsx",
    )
