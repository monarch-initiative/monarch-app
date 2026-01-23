"""Tests for HistoPheno bin label mapping."""
import pytest
from monarch_py.datamodels.solr import (
    HistoPhenoKeys,
    HISTOPHENO_BIN_LABELS,
    get_bin_label,
    get_all_bin_ids,
)


class TestHistoPhenoBinLabels:
    """Test that all HistoPhenoKeys have human-readable labels."""

    def test_all_keys_have_labels(self):
        """Every HistoPhenoKeys enum should have a corresponding label."""
        for key in HistoPhenoKeys:
            assert key.value in HISTOPHENO_BIN_LABELS, f"Missing label for {key}"

    def test_labels_are_nonempty_strings(self):
        """Labels should be meaningful strings."""
        for key_value, label in HISTOPHENO_BIN_LABELS.items():
            assert isinstance(label, str)
            assert len(label) > 0, f"Empty label for {key_value}"

    def test_label_count_matches_enum_count(self):
        """Number of labels should match number of enum values."""
        assert len(HISTOPHENO_BIN_LABELS) == len(HistoPhenoKeys)

    @pytest.mark.parametrize(
        "bin_id,expected_label",
        [
            ("UPHENO:0002964", "skeletal system"),
            ("UPHENO:0004523", "nervous system"),
            ("HP:0001939", "metabolism/homeostasis"),
            ("UPHENO:0080362", "cardiovascular system"),
            ("UPHENO:0004536", "respiratory system"),
            ("UPHENO:0002833", "digestive system"),
            ("UPHENO:0002635", "integument"),
            ("UPHENO:0003020", "eye"),
            ("HP:0000598", "ear"),
            ("UPHENO:0003116", "endocrine system"),
            ("UPHENO:0002642", "genitourinary system"),
            ("UPHENO:0002816", "musculature"),
            ("UPHENO:0002764", "head/neck"),
            ("UPHENO:0002948", "immune system"),
            ("UPHENO:0004459", "blood/blood-forming tissues"),
            ("HP:0002664", "neoplasm"),
            ("UPHENO:0075949", "prenatal/birth"),
            ("UPHENO:0049874", "growth"),
            ("UPHENO:0003013", "breast"),
            ("UPHENO:0002712", "connective tissue"),
        ],
    )
    def test_known_labels(self, bin_id, expected_label):
        """Verify expected labels for HistoPheno bins."""
        assert HISTOPHENO_BIN_LABELS[bin_id] == expected_label


class TestGetBinLabel:
    """Test the get_bin_label helper function."""

    def test_get_valid_bin_label(self):
        """get_bin_label returns correct label for valid bin ID."""
        assert get_bin_label("UPHENO:0002964") == "skeletal system"

    def test_get_bin_label_raises_for_invalid_id(self):
        """get_bin_label raises KeyError for unknown bin ID."""
        with pytest.raises(KeyError):
            get_bin_label("INVALID:0000000")


class TestGetAllBinIds:
    """Test the get_all_bin_ids helper function."""

    def test_returns_all_bin_ids(self):
        """get_all_bin_ids returns all bin IDs."""
        bin_ids = get_all_bin_ids()
        assert len(bin_ids) == len(HistoPhenoKeys)

    def test_returns_list(self):
        """get_all_bin_ids returns a list."""
        bin_ids = get_all_bin_ids()
        assert isinstance(bin_ids, list)

    def test_all_ids_are_strings(self):
        """All returned IDs should be strings."""
        bin_ids = get_all_bin_ids()
        for bin_id in bin_ids:
            assert isinstance(bin_id, str)

    def test_all_ids_are_valid_enum_values(self):
        """All returned IDs should be valid HistoPhenoKeys values."""
        bin_ids = get_all_bin_ids()
        enum_values = {key.value for key in HistoPhenoKeys}
        for bin_id in bin_ids:
            assert bin_id in enum_values, f"{bin_id} not in HistoPhenoKeys"
