"""Tests for the taxa mapping."""

import os

import pandas as pd
import pytest


if __name__ == "__main__":
    dirname = os.path.dirname
    os.chdir(path=os.path.join(dirname(dirname(__file__))))

from preparation import taxa_mapping


def test_create_taxonomy(valid_twn: pd.DataFrame, twn_taxonomy: pd.DataFrame) -> None:
    """Tests the creation of the taxonomy by adding the taxonomic order.

    Args:
        valid_twn (pd.DataFrame): Fixture that filters valid twn ('Statuscode' 10 or 80).
        twn_taxonomy (pd.DataFrame): Fixture that loads the 'twn_taxonomy.csv' file.
    """
    result = taxa_mapping.create_taxonomy(valid_twn)
    pd.testing.assert_frame_equal(result, twn_taxonomy)


def test_create_taxonomy_exit_rank() -> None:
    """Tests the creation of taxonomy with wrong data."""
    data = [
        [
            "Abietinaria",
            "MACEV",
            "BRHYP",
            "ExtraRank",
            "Sertulariidae",
            10,
            "Abietinaria",
        ]
    ]
    twn_error = pd.DataFrame(
        data,
        columns=[
            "Name",
            "Taxontype",
            "Taxongroup_code",
            "Taxonrank",
            "Parentname",
            "Statuscode",
            "Synonymname",
        ],
    )

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        taxa_mapping.create_taxonomy(twn_error)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code is None


def test_recode_subspecies_valid(
    valid_twn: pd.DataFrame,
    twn_taxonomy: pd.DataFrame,
    twn_recoded_subspecies: pd.DataFrame,
) -> None:
    """Tests recodes the twn taxa below the species level to species level.

    Args:
        valid_twn (pd.DataFrame): Fixture that filters valid twn ('Statuscode' 10 or 80).
        twn_taxonomy (pd.DataFrame): Fixture that loads the 'twn_taxonomy.csv' file.
        twn_recoded_subspecies (pd.DataFrame):  Fixture that loads the 'twn_recoded_subspecies.csv' file.
    """
    result = taxa_mapping.recode_subspecies(valid_twn, twn_taxonomy)
    pd.testing.assert_frame_equal(result, twn_recoded_subspecies)


def test_recode_subspecies_exit_cardinality(
    valid_twn: pd.DataFrame, twn_taxonomy: pd.DataFrame
) -> None:
    """Tests the recoding of taxa below the species level to species level for the error.

    Args:
        valid_twn (pd.DataFrame): Fixture that filters valid twn ('Statuscode' 10 or 80).
        twn_taxonomy (pd.DataFrame): Fixture that loads the 'twn_taxonomy.csv' file.
    """
    # Insert Dict to the dataframe using DataFrame.append()
    new_row = {
        "Name": "Ablabesmyia monilis",
        "Parentname": "Ablabesmyia",
        "Taxonrank": "Species",
        "Order": 1,
    }
    twn_taxonomy = pd.concat([twn_taxonomy, pd.DataFrame([new_row])], ignore_index=True)

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        taxa_mapping.recode_subspecies(valid_twn, twn_taxonomy)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code is None


def test_glue_hierarchie_valid(
    twn_recoded_subspecies: pd.DataFrame,
    twn_taxonomy: pd.DataFrame,
    output_glue_hierarchie: pd.DataFrame,
) -> None:
    """Tests adding and checking the hierarhical order.

    Args:
        twn_recoded_subspecies (pd.DataFrame): Fixture that loads the 'twn_recoded_subspecies.csv' file.
        twn_taxonomy (pd.DataFrame): Fixture that loads the 'twn_taxonomy.csv' file.
        output_glue_hierarchie (pd.DataFrame): Fixture that loads the 'output_glue_hierarchie.csv' file.
    """
    result = taxa_mapping.glue_hierarchie(twn_recoded_subspecies, twn_taxonomy)
    assert isinstance(result, pd.DataFrame)
    assert result.columns.tolist() == [
        "Twn_name",
        "Name",
        "Hierarchie",
        "Taxonrank",
        "Order",
    ]
    pd.testing.assert_frame_equal(result, output_glue_hierarchie)


def test_glue_hierarchie_exit_subspecies(
    twn_recoded_subspecies: pd.DataFrame, twn_taxonomy: pd.DataFrame
) -> None:
    """Tests adding and checking the hierarhical order by resulting in an error for subspecies.

    Args:
        twn_recoded_subspecies (pd.DataFrame): Fixture that loads the 'twn_recoded_subspecies.csv' file.
        twn_taxonomy (pd.DataFrame): Fixture that loads the 'twn_taxonomy.csv' file.
        output_glue_hierarchie (pd.DataFrame): Fixture that loads the 'output_glue_hierarchie.csv' file.
    """
    twn_taxonomy.loc[twn_taxonomy["Name"] == "Ablabesmyia monilis", "Order"] = -1

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        taxa_mapping.glue_hierarchie(twn_recoded_subspecies, twn_taxonomy)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code is None


def test_glue_hierarchie_exit_taxonrank(
    twn_recoded_subspecies: pd.DataFrame, twn_taxonomy: pd.DataFrame
) -> None:
    """Tests adding and checking the hierarhical order by resulting in an error for taxonrank.

    Args:
        twn_recoded_subspecies (pd.DataFrame): Fixture that loads the 'twn_recoded_subspecies.csv' file.
        twn_taxonomy (pd.DataFrame): Fixture that loads the 'twn_taxonomy.csv' file.
        output_glue_hierarchie (pd.DataFrame): Fixture that loads the 'output_glue_hierarchie.csv' file.
    """
    twn_taxonomy.loc[twn_taxonomy["Name"] == "Ablabesmyia monilis", "Taxonrank"] = pd.NA

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        taxa_mapping.glue_hierarchie(twn_recoded_subspecies, twn_taxonomy)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code is None


def test_glue_hierarchie_exit_hierarchie(
    twn_recoded_subspecies: pd.DataFrame, twn_taxonomy: pd.DataFrame
) -> None:
    """Tests adding and checking the hierarhical order by resulting in an error for hierarhie.

    Args:
        twn_recoded_subspecies (pd.DataFrame): Fixture that loads the 'twn_recoded_subspecies.csv' file.
        twn_taxonomy (pd.DataFrame): Fixture that loads the 'twn_taxonomy.csv' file.
        output_glue_hierarchie (pd.DataFrame): Fixture that loads the 'output_glue_hierarchie.csv' file.
    """
    twn_taxonomy.loc[
        twn_taxonomy["Name"] == "Ablabesmyia monilis", "Parentname"
    ] = "Ablabes"

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        taxa_mapping.glue_hierarchie(twn_recoded_subspecies, twn_taxonomy)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code is None


def test_split_taxa_speciescombi(
    input_split_combined_taxa: pd.DataFrame, output_split_speciescombi: pd.DataFrame
) -> None:
    """Tests splitting the combined twn species taxa and concatenates their full names to a new "combi" column.

    Args:
        input_split_combined_taxa (pd.DataFrame): Fixture that loads the 'input_split_combined_taxa.csv' file.
        output_split_speciescombi (pd.DataFrame): Fixture that loads the 'output_split_speciescombi.csv' file.
    """

    result = taxa_mapping.split_combined_taxa(input_split_combined_taxa, "SpeciesCombi")

    # nan values are not equal, so replace them with NA
    output_split_speciescombi.fillna("NA", inplace=True)
    result.fillna("NA", inplace=True)
    pd.testing.assert_frame_equal(result, output_split_speciescombi)


def test_split_taxa_genuscombi(
    input_split_combined_taxa: pd.DataFrame, output_split_genuscombi: pd.DataFrame
) -> None:
    """Tests splitting the combined twn genus taxa and concatenates their full names to a new "combi" column.

    Args:
        input_split_combined_taxa (pd.DataFrame): Fixture that loads the 'input_split_combined_taxa.csv' file.
        output_split_speciescombi (pd.DataFrame): Fixture that loads the 'output_split_speciescombi.csv' file.
    """
    result = taxa_mapping.split_combined_taxa(input_split_combined_taxa, "GenusCombi")

    # nan values are not equal, so replace them with NA
    output_split_genuscombi.fillna("NA", inplace=True)
    result.fillna("NA", inplace=True)
    pd.testing.assert_frame_equal(result, output_split_genuscombi)


def test_integration_taxa_mapping(
    twn_corrected: pd.DataFrame, output_integration_taxa_mapping: pd.DataFrame
) -> None:
    """Tests the integration of the taxa mapping functions.

    Args:
        twn_corrected (pd.DataFrame): Fixture that loads the corrected TWN data ('twn_corrected.csv').
        output_integration_taxa_mapping (pd.DataFrame): Fixture that loads the 'output_integration_taxa_mapping.csv'.
    """
    result = taxa_mapping.main_taxa_mapping(twn_corrected)
    pd.testing.assert_frame_equal(result, output_integration_taxa_mapping)
