"""Tests for calculating the Margalefs indices."""

import os

import pandas as pd


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))

from analysis import margalef


def test_margalef(input_margalef: pd.DataFrame) -> None:
    """Tests calculating the margalef index based on specified input.

    Args:
        input_margalef(pd.DataFrame)
    """
    # https://www2.unbc.ca/sites/default/files/sections/che-elkin/biol410lecture20communitystructure.pdf
    # S(pecies) = 6 and N(individuals) = 50
    # Margalef index = 1.28

    margalef_df = margalef.calculate_margalef_over_samples(
        input_margalef, ["Waterlichaam"], False
    )

    assert margalef_df["Margalef_Monster"][0] == 1.28
    assert margalef_df["Margalef_Monster"][1] == 1.67
