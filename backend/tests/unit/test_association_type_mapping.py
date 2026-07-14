import pytest
from monarch_py.datamodels.model import AssociationTypeMapping
from monarch_py.utils.association_type_utils import (
    AssociationTypeMappings,
    get_solr_criteria_filters,
    get_solr_query_fragment,
    get_sql_query_fragment,
)


@pytest.fixture()
def basic_mapping():
    return AssociationTypeMapping(
        key="biolink:GeneToPhenotypeAssociation",
        subject_label="Genes",
        object_label="Phenotypes",
        category=["biolink:GeneToPhenotypeAssociation"],
    )


@pytest.fixture()
def composite_mapping():
    return AssociationTypeMapping(
        key="clinical_measurement_correlated_phenotypes",
        subject_label="Correlated Phenotypes",
        object_label="Correlated Clinical Measurements",
        category=["biolink:Association"],
        predicate=["biolink:correlated_with"],
        subject_category=["biolink:ClinicalMeasurement"],
        object_category=["biolink:PhenotypicFeature"],
    )


def test_solr_basic_mapping(basic_mapping):
    query_fragment = get_solr_query_fragment(basic_mapping)
    assert query_fragment == 'category:"biolink:GeneToPhenotypeAssociation"'


def test_sql_basic_mapping(basic_mapping):
    query_fragment = get_sql_query_fragment(basic_mapping)
    assert query_fragment == 'category = "biolink:GeneToPhenotypeAssociation"'


def test_solr_composite_mapping(composite_mapping):
    """A section that keys on predicate + subject/object category, not just category."""
    query_fragment = get_solr_query_fragment(composite_mapping)
    assert query_fragment == (
        'category:"biolink:Association" AND predicate:"biolink:correlated_with" '
        'AND subject_category:"biolink:ClinicalMeasurement" '
        'AND object_category:"biolink:PhenotypicFeature"'
    )


def test_solr_legacy_mapping_matches_on_category_only():
    """A legacy section (key defaulted to its category) declares subject/object
    category only as direction metadata; it must NOT constrain the Solr query on
    them, or it would undercount edges whose node categories differ from the
    declared ones (e.g. gene-expression edges to biolink:NamedThing)."""
    mapping = AssociationTypeMapping(
        key="biolink:GeneToExpressionSiteAssociation",
        subject_label="Gene Expression",
        object_label="Gene Expression",
        category=["biolink:GeneToExpressionSiteAssociation"],
        subject_category=["biolink:Gene"],
        object_category=["biolink:AnatomicalEntity"],
    )
    assert get_solr_query_fragment(mapping) == 'category:"biolink:GeneToExpressionSiteAssociation"'
    assert get_solr_criteria_filters(mapping) == []


def test_solr_or_within_criterion():
    """Multiple values in a single criterion are OR'd (and parenthesized)."""
    mapping = AssociationTypeMapping(
        key="drug_indications",
        subject_label="Indications",
        object_label="Treatments",
        category=[
            "biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation",
            "biolink:ChemicalEntityToDiseaseOrPhenotypicFeatureAssociation",
        ],
    )
    query_fragment = get_solr_query_fragment(mapping)
    assert query_fragment == (
        '(category:"biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation" '
        'OR category:"biolink:ChemicalEntityToDiseaseOrPhenotypicFeatureAssociation")'
    )


# =====================================================================
# Tests for AssociationTypeMappings singleton
# =====================================================================


def test_get_mappings_returns_list():
    mappings = AssociationTypeMappings.get_mappings()
    assert isinstance(mappings, list)
    assert len(mappings) > 0


def test_all_mappings_have_category_and_key():
    mappings = AssociationTypeMappings.get_mappings()
    for m in mappings:
        assert m.category is not None
        assert m.key is not None


def test_mapping_key_defaults_to_category():
    """Existing single-category mappings get key == their category."""
    mapping = AssociationTypeMappings.get_mapping("biolink:DiseaseToPhenotypicFeatureAssociation")
    assert mapping is not None
    assert mapping.key == "biolink:DiseaseToPhenotypicFeatureAssociation"


def test_get_mapping_by_category():
    result = AssociationTypeMappings.get_mapping("biolink:DiseaseToPhenotypicFeatureAssociation")
    assert result is not None
    assert "biolink:DiseaseToPhenotypicFeatureAssociation" in result.category


def test_get_mapping_unknown_returns_none():
    result = AssociationTypeMappings.get_mapping("biolink:NonExistent")
    assert result is None


def test_get_mapping_by_key():
    result = AssociationTypeMappings.get_mapping_by_key("biolink:DiseaseToPhenotypicFeatureAssociation")
    assert result is not None
    assert result.key == "biolink:DiseaseToPhenotypicFeatureAssociation"


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
