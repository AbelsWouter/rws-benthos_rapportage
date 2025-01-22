"""Tests the utility (overall-usefull) functions."""

import os

import numpy as np
import pandas as pd
import pytest


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))

from preparation import utility


def test_coalesce() -> None:
    """Tests returning the first non-None value or None if all values are None."""
    assert utility.coalesce(1, "twee") == 1
    assert utility.coalesce(None, "twee") == "twee"
    assert pd.isna(utility.coalesce(pd.NA, None))
    assert utility.coalesce(None, pd.NA) is np.nan
    assert utility.coalesce(None, np.nan) is np.nan


def test_replace_values() -> None:
    """Tests replacing a value in a pandas DataFrame."""
    df = pd.DataFrame({"Name": ["A", "B", "C", "D"], "Age": [1, 1, 1, 1]})
    replace_dict = {"A": 2}
    find_field = "Name"
    replace_field = "Age"

    expected = pd.DataFrame({"Name": ["A", "B", "C", "D"], "Age": [2, 1, 1, 1]})
    pd.testing.assert_frame_equal(
        utility.replace_values(df, replace_dict, find_field, replace_field), expected
    )


def test_add_prefix_suffix() -> None:
    """Tests adding a prefix and suffix symbol."""
    result = utility.add_prefix_suffix("string")
    assert result == "-string-"
    result = utility.add_prefix_suffix("string|another string|and another")
    assert result == "-string-|-another string-|-and another-"
    result = utility.add_prefix_suffix(1)
    assert result == "-1-"


def test_stop_script() -> None:
    """Tests stopping the script."""
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        utility.stop_script()
        assert pytest_wrapped_e.type == SystemExit


def test_valid_path() -> None:
    """Tests removing characters for making valid paths."""
    assert utility.valid_path("test") == "test"
    assert utility.valid_path(">8m") == "gd8m"
    assert utility.valid_path("< 2m") == "kd 2m"

    assert utility.valid_path("test.csv") == "test.csv"
    assert utility.valid_path("test.csv.csv") == "test csv.csv"
    assert utility.valid_path("test.csv.csv.csv") == "test csv csv.csv"

    assert utility.valid_path("test/test") == "test/test"
    assert utility.valid_path("test/test.csv") == "test/test.csv"

    assert utility.valid_path(".\\test/test") == ".\\test/test"

    assert utility.valid_path("test/test.csv.csv") == "test/test csv.csv"

    assert utility.valid_path("test?test.") == "test test"
    assert utility.valid_path("test?test.csv") == "test test.csv"
