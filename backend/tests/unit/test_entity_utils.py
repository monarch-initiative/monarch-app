import pytest
from unittest.mock import patch

from monarch_py.utils.entity_utils import expansion_patch, get_uri, get_expanded_curie
from monarch_py.datamodels.model import ExpandedCurie


class TestExpansionPatch:
    """Tests for the expansion_patch function."""

    def test_mgi_url_fix(self):
        """Test that MGI URLs with slashes are converted to use colons."""
        url = "https://identifiers.org/MGI/97486"
        result = expansion_patch(url)
        assert result == "https://identifiers.org/MGI:97486"

    def test_mgi_url_already_correct(self):
        """Test that correctly formatted MGI URLs are not modified."""
        url = "https://identifiers.org/MGI:97486"
        result = expansion_patch(url)
        assert result == "https://identifiers.org/MGI:97486"

    def test_phenopacket_url_expansion(self):
        """Test that phenopacket.store URLs are expanded correctly."""
        url = "https://github.com/monarch-initiative/phenopacket-store/blob/main/notebooks/BRCA1.Smith_2020_30696174-III-2"
        result = expansion_patch(url)
        expected = "https://github.com/monarch-initiative/phenopacket-store/blob/main/notebooks/BRCA1/phenopackets/Smith_2020_30696174-III-2.json"
        assert result == expected

    def test_phenopacket_url_with_pedigree_notation(self):
        """Test that pedigree notation dots in filenames are converted to underscores."""
        url = "https://github.com/monarch-initiative/phenopacket-store/blob/main/notebooks/BRCA1.Smith_2020.IV.12"
        result = expansion_patch(url)
        expected = "https://github.com/monarch-initiative/phenopacket-store/blob/main/notebooks/BRCA1/phenopackets/Smith_2020_IV_12.json"
        assert result == expected

    def test_non_matching_url_unchanged(self):
        """Test that URLs not matching any pattern are returned unchanged."""
        url = "https://example.com/some/path"
        result = expansion_patch(url)
        assert result == url


class TestGetUri:
    """Tests for the get_uri function."""

    def test_known_prefix_returns_uri(self):
        """Test that a known prefix returns an expanded URI."""
        result = get_uri("MONDO:0005737")
        assert result is not None
        assert "MONDO" in result

    def test_unknown_prefix_returns_none(self):
        """Test that an unknown prefix returns None."""
        result = get_uri("UNKNOWN_PREFIX:12345")
        assert result is None

    def test_applies_expansion_patch(self):
        """Test that get_uri applies the expansion_patch to the result."""
        result = get_uri("MGI:97486")
        assert result is not None
        # The expansion_patch should fix the MGI URL format
        assert "MGI:97486" in result or "MGI/97486" not in result


class TestGetExpandedCurie:
    """Tests for the get_expanded_curie function."""

    def test_returns_expanded_curie_object(self):
        """Test that get_expanded_curie returns an ExpandedCurie object."""
        result = get_expanded_curie("MONDO:0005737")
        assert isinstance(result, ExpandedCurie)
        assert result.id == "MONDO:0005737"
        assert result.url is not None

    def test_unknown_prefix_returns_none_url(self):
        """Test that an unknown prefix returns ExpandedCurie with None url."""
        result = get_expanded_curie("UNKNOWN_PREFIX:12345")
        assert isinstance(result, ExpandedCurie)
        assert result.id == "UNKNOWN_PREFIX:12345"
        assert result.url is None

    def test_uses_get_uri_for_expansion(self):
        """Test that get_expanded_curie uses get_uri (and thus applies patches)."""
        with patch("monarch_py.utils.entity_utils.get_uri") as mock_get_uri:
            mock_get_uri.return_value = "https://example.com/patched"
            result = get_expanded_curie("TEST:123")
            mock_get_uri.assert_called_once_with("TEST:123")
            assert result.url == "https://example.com/patched"
