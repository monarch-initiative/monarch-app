import pytest
from monarch_py.implementations.solr.solr_implementation import SolrImplementation
from monarch_py.datamodels.model import InformationResource

pytestmark = pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)


def test_get_infores_catalog():
    """Test that get_infores_catalog returns a list of information resources"""
    si = SolrImplementation()
    catalog = si.get_infores_catalog()

    assert isinstance(catalog, list)
    assert len(catalog) > 0

    # Check that each item is an InformationResource with expected fields
    for infores in catalog:
        assert isinstance(infores, InformationResource)
        assert hasattr(infores, "id")
        assert infores.id.startswith("infores:")
        assert hasattr(infores, "status")
        assert hasattr(infores, "name")


def test_get_infores_by_id():
    """Test that get_infores returns a specific information resource by ID"""
    si = SolrImplementation()

    # First get the catalog to find a valid ID
    catalog = si.get_infores_catalog()
    assert len(catalog) > 0

    test_id = catalog[0].id
    infores = si.get_infores(test_id)

    assert isinstance(infores, InformationResource)
    assert infores.id == test_id
    assert hasattr(infores, "status")
    assert hasattr(infores, "name")


def test_get_infores_nonexistent():
    """Test that get_infores returns None for non-existent ID"""
    si = SolrImplementation()
    infores = si.get_infores("infores:nonexistent-test-id")

    assert infores is None


def test_get_infores_catalog_structure():
    """Test that catalog entries have expected structure"""
    si = SolrImplementation()
    catalog = si.get_infores_catalog()

    assert len(catalog) > 0

    # Test first entry has basic required fields
    first_entry = catalog[0]
    required_fields = ["id", "status", "name"]
    for field in required_fields:
        assert hasattr(first_entry, field)

    # Verify ID format
    assert first_entry.id.startswith("infores:")

    # Verify status is a valid value
    valid_statuses = ["released", "deprecated", "draft"]
    assert first_entry.status in valid_statuses


def test_get_infores_catalog_not_empty():
    """Test that the infores catalog is not empty"""
    si = SolrImplementation()
    catalog = si.get_infores_catalog()

    # Should have at least some standard infores entries
    assert len(catalog) > 10

    # Check for some known infores entries
    infores_ids = [entry.id for entry in catalog]

    # These are common translator infores that should exist
    expected_infores = ["infores:aragorn", "infores:arax"]
    found_infores = [infores_id for infores_id in expected_infores if infores_id in infores_ids]

    # At least one of the expected infores should be present
    assert len(found_infores) > 0
