import pytest
from monarch_py.datamodels.model import AssociationTypeMapping, MatchCriteriaEnum
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
        # LOINC edges all share biolink:Association, so this section cannot be identified
        # by category and has to opt in to matching on every declared criterion.
        match_criteria=MatchCriteriaEnum.full,
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


# =====================================================================
# match_criteria is explicit, not inferred
# =====================================================================


def test_match_criteria_defaults_to_category_for_every_shipped_mapping():
    """Category-only matching is what every legacy section relies on, so it has to be what
    you get by omitting the field. A section that wants more says so."""
    for mapping in AssociationTypeMappings.get_mappings():
        if mapping.match_criteria == MatchCriteriaEnum.full:
            continue
        assert mapping.match_criteria == MatchCriteriaEnum.category, mapping.key


def test_adding_a_key_does_not_change_what_a_section_matches():
    """The regression this field exists to prevent. `key` is set for URL and UI reasons;
    it used to double as the opt-in to full-criteria matching, so giving a legacy section a
    key silently started constraining its query on subject/object_category — the change
    that cost GeneToExpressionSite -83% of its edges."""
    fields = dict(
        subject_label="Gene Expression",
        object_label="Gene Expression",
        category=["biolink:GeneToExpressionSiteAssociation"],
        subject_category=["biolink:Gene"],
        object_category=["biolink:AnatomicalEntity"],
    )
    keyed_by_category = AssociationTypeMapping(key="biolink:GeneToExpressionSiteAssociation", **fields)
    keyed_for_the_url = AssociationTypeMapping(key="gene_expression", **fields)
    assert get_solr_query_fragment(keyed_by_category) == get_solr_query_fragment(keyed_for_the_url)
    assert get_solr_criteria_filters(keyed_for_the_url) == []


def test_full_criteria_must_be_asked_for():
    """A composite section that forgets the opt-in matches on category alone — which for
    the LOINC sections means every biolink:Association edge. Better that it be visibly
    wrong in the yaml than silently switched on by an unrelated field."""
    forgot_to_opt_in = AssociationTypeMapping(
        key="clinical_measurement_correlated_phenotypes",
        subject_label="Correlated Phenotypes",
        object_label="Correlated Clinical Measurements",
        category=["biolink:Association"],
        predicate=["biolink:correlated_with"],
        subject_category=["biolink:ClinicalMeasurement"],
    )
    assert get_solr_query_fragment(forgot_to_opt_in) == 'category:"biolink:Association"'


def test_duplicate_section_keys_are_rejected_at_load():
    """Two sections sharing a key silently merge their counts, and one wins the table
    lookup. Easy to introduce now that `key` defaults to the first of several categories."""
    import pytest as _pytest

    from monarch_py.utils import association_type_utils

    # The class is a singleton, so reload the already-constructed instance rather than
    # building a second one.
    if AssociationTypeMappings._AssociationTypeMappings__instance is None:
        AssociationTypeMappings()
    instance = AssociationTypeMappings._AssociationTypeMappings__instance
    duplicated = [
        {"subject_label": "A", "object_label": "A", "category": ["biolink:X"]},
        {"subject_label": "B", "object_label": "B", "category": ["biolink:X", "biolink:Y"]},
    ]
    original = association_type_utils.yaml.load
    association_type_utils.yaml.load = lambda *args, **kwargs: duplicated
    try:
        with _pytest.raises(ValueError, match="Duplicate association-type section keys"):
            instance.load_mappings()
    finally:
        association_type_utils.yaml.load = original
        instance.load_mappings()
    assert len(instance.mappings) > 1  # the real yaml is restored
