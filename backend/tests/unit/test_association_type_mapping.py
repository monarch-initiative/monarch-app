import pytest
from monarch_py.datamodels.model import AssociationTypeMapping
from monarch_py.utils.association_type_utils import (
    AssociationTypeMappings,
    get_association_type_mapping_by_query_string,
    get_solr_query_fragment,
    get_sql_query_fragment,
    parse_query_string_for_category,
)


@pytest.fixture()
def basic_mapping():
    return AssociationTypeMapping(
        subject_label="Genes",
        object_label="Phenotypes",
        category="biolink:GeneToPhenotypeAssociation",
    )


def test_solr_basic_mapping(basic_mapping):
    query_fragment = get_solr_query_fragment(basic_mapping)
    assert query_fragment == 'category:"biolink:GeneToPhenotypeAssociation"'


def test_sql_basic_mapping(basic_mapping):
    query_fragment = get_sql_query_fragment(basic_mapping)
    assert query_fragment == 'category = "biolink:GeneToPhenotypeAssociation"'


def test_parse_association_type_query_string_single_category():
    query_string = 'category:"biolink:GeneToPhenotypeAssociation"'
    category = parse_query_string_for_category(query_string)
    assert category == "biolink:GeneToPhenotypeAssociation"


def test_parse_association_type_query_string_multiple_categories():
    query_string = 'category:"biolink:GeneToDiseaseAssociation" AND (predicate:"biolink:gene_associated_with_condition" OR predicate:"biolink:contributes_to")'
    category = parse_query_string_for_category(query_string)
    assert category == "biolink:GeneToDiseaseAssociation"


# =====================================================================
# Tests for AssociationTypeMappings singleton
# =====================================================================


# =====================================================================
# Tests for AssociationTypeMappings singleton
# =====================================================================


def test_get_mappings_returns_list():
    mappings = AssociationTypeMappings.get_mappings()
    assert isinstance(mappings, list)
    assert len(mappings) > 0


def test_all_mappings_have_category():
    mappings = AssociationTypeMappings.get_mappings()
    for m in mappings:
        assert m.category is not None


def test_get_mapping_by_category():
    result = AssociationTypeMappings.get_mapping("biolink:DiseaseToPhenotypicFeatureAssociation")
    assert result is not None
    assert result.category == "biolink:DiseaseToPhenotypicFeatureAssociation"


def test_get_mapping_unknown_returns_none():
    result = AssociationTypeMappings.get_mapping("biolink:NonExistent")
    assert result is None


def test_get_traversable_associations_for_gene():
    results = AssociationTypeMappings.get_traversable_associations("biolink:Gene")
    assert len(results) > 0
    categories = [r["category"] for r in results]
    assert "biolink:GeneToPhenotypicFeatureAssociation" in categories


def test_get_traversable_associations_for_disease():
    results = AssociationTypeMappings.get_traversable_associations("biolink:Disease")
    assert len(results) > 0
    categories = [r["category"] for r in results]
    assert "biolink:DiseaseToPhenotypicFeatureAssociation" in categories


def test_get_traversable_associations_returns_direction():
    results = AssociationTypeMappings.get_traversable_associations("biolink:Gene")
    for r in results:
        assert "context_field" in r
        assert r["context_field"] in ("subject", "object")
        assert "target_category" in r
        assert "label" in r


def test_get_traversable_associations_empty_for_unknown():
    results = AssociationTypeMappings.get_traversable_associations("biolink:Unknown")
    assert results == []


# =====================================================================
# Tests for get_association_type_mapping_by_query_string
# =====================================================================


def test_mapping_by_query_string_valid():
    result = get_association_type_mapping_by_query_string('category:"biolink:DiseaseToPhenotypicFeatureAssociation"')
    assert result.category == "biolink:DiseaseToPhenotypicFeatureAssociation"


def test_mapping_by_query_string_no_match():
    with pytest.raises(ValueError, match="No matching"):
        get_association_type_mapping_by_query_string('category:"biolink:NonExistentAssociation"')


def test_mapping_by_query_string_no_category():
    with pytest.raises(ValueError, match="No categories"):
        get_association_type_mapping_by_query_string("predicate:something")
