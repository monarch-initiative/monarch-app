import pytest
from unittest.mock import patch, MagicMock

from monarch_py.implementations.solr.solr_implementation import SolrImplementation
from monarch_py.datamodels.model import (
    ExpandedAssociation,
    AssociationResults,
    CrossSpeciesTermClique,
    Entity,
    EntityGridResponse,
    CasePhenotypeMatrixResponse,
)
from monarch_py.datamodels.category_enums import EntityCategory


def test_get_counterpart_entities_limit():
    # Make sure that we don't accidentally end up with the default limit again
    with patch.object(SolrImplementation, "get_associations") as mock_get_associations:
        si = SolrImplementation()
        si.get_counterpart_entities("MONDO:0007947")
        assert mock_get_associations.called
        assert mock_get_associations.call_args_list[0].kwargs["limit"] == 1000


# =====================================================================
# Tests for _get_node_relationships (Mondo disease<->gene related_to)
# =====================================================================


def _mondo_related_to_association(
    subject="MONDO:1010417",
    subject_label="myoclonus, GLRA1-related, cattle",
    original_predicate="RO:0004003",
    object="NCBIGene:281783",
    object_label="GLRA1",
    object_category="biolink:Gene",
    object_taxon="NCBITaxon:9913",
    object_taxon_label="Bos taurus",
    id="uuid-1",
):
    return ExpandedAssociation(
        id=id,
        agent_type="not_provided",
        knowledge_level="knowledge_assertion",
        subject=subject,
        subject_label=subject_label,
        subject_category="biolink:Disease",
        predicate="biolink:related_to",
        original_predicate=original_predicate,
        object=object,
        object_label=object_label,
        object_category=object_category,
        object_taxon=object_taxon,
        object_taxon_label=object_taxon_label,
        primary_knowledge_source="infores:mondo",
    )


def _mondo_disease_gene_association():
    return _mondo_related_to_association()


def test_get_node_relationships_for_disease_resolves_ro_label():
    """A disease node should surface its Mondo related_to gene with the RO label from the KG."""
    disease = Entity(id="MONDO:1010417", name="myoclonus, GLRA1-related, cattle", category="biolink:Disease")
    associations = AssociationResults(items=[_mondo_disease_gene_association()], limit=100, offset=0, total=1)
    ro_term = Entity(id="RO:0004003", name="has material basis in germline mutation in", category="biolink:NamedThing")

    with (
        patch.object(SolrImplementation, "get_associations", return_value=associations) as mock_assoc,
        patch.object(SolrImplementation, "get_entity", return_value=ro_term),
    ):
        relationships = SolrImplementation()._get_node_relationships(disease)

    # Disease is the subject; we query the Mondo related_to edges by subject.
    kwargs = mock_assoc.call_args.kwargs
    assert kwargs["subject"] == ["MONDO:1010417"]
    assert kwargs["object"] is None
    assert kwargs["primary_knowledge_source"] == ["infores:mondo"]

    assert len(relationships) == 1
    rel = relationships[0]
    assert rel.relation == "RO:0004003"
    assert rel.relation_label == "has material basis in germline mutation in"
    assert rel.related_entity.id == "NCBIGene:281783"
    assert rel.related_entity.name == "GLRA1"
    # Non-human species is carried through so the UI can show it
    assert rel.related_entity.in_taxon_label == "Bos taurus"


def test_get_node_relationships_for_gene_queries_by_object():
    """A gene node should surface its Mondo related_to disease (counterpart is the subject)."""
    gene = Entity(id="NCBIGene:281783", name="GLRA1", category="biolink:Gene")
    associations = AssociationResults(items=[_mondo_disease_gene_association()], limit=100, offset=0, total=1)
    ro_term = Entity(id="RO:0004003", name="has material basis in germline mutation in", category="biolink:NamedThing")

    with (
        patch.object(SolrImplementation, "get_associations", return_value=associations) as mock_assoc,
        patch.object(SolrImplementation, "get_entity", return_value=ro_term),
    ):
        relationships = SolrImplementation()._get_node_relationships(gene)

    kwargs = mock_assoc.call_args.kwargs
    assert kwargs["object"] == ["NCBIGene:281783"]
    assert kwargs["subject"] is None
    assert kwargs["subject_category"] == [EntityCategory.DISEASE]

    assert len(relationships) == 1
    assert relationships[0].related_entity.id == "MONDO:1010417"
    assert relationships[0].relation_label == "has material basis in germline mutation in"


def test_get_node_relationships_caches_ro_label_lookup():
    """The RO label should be resolved once per distinct relation CURIE."""
    disease = Entity(id="MONDO:1010417", name="d", category="biolink:Disease")
    a1 = _mondo_disease_gene_association()
    a2 = _mondo_disease_gene_association()
    a2.id = "uuid-2"
    a2.object = "HGNC:4329"
    a2.object_label = "GLRB"
    associations = AssociationResults(items=[a1, a2], limit=100, offset=0, total=2)
    ro_term = Entity(id="RO:0004003", name="has material basis in germline mutation in", category="biolink:NamedThing")

    with (
        patch.object(SolrImplementation, "get_associations", return_value=associations),
        patch.object(SolrImplementation, "get_entity", return_value=ro_term) as mock_get_entity,
    ):
        relationships = SolrImplementation()._get_node_relationships(disease)

    assert len(relationships) == 2
    # Same relation CURIE for both -> only one entity lookup.
    assert mock_get_entity.call_count == 1


def test_get_node_relationships_handles_missing_ro_label():
    """If the RO term can't be resolved, relation_label is None and the relationship still renders."""
    disease = Entity(id="MONDO:1010417", name="d", category="biolink:Disease")
    associations = AssociationResults(items=[_mondo_disease_gene_association()], limit=100, offset=0, total=1)

    with (
        patch.object(SolrImplementation, "get_associations", return_value=associations),
        patch.object(SolrImplementation, "get_entity", return_value=None),
    ):
        relationships = SolrImplementation()._get_node_relationships(disease)

    assert len(relationships) == 1
    assert relationships[0].relation == "RO:0004003"
    assert relationships[0].relation_label is None
    assert relationships[0].related_entity.id == "NCBIGene:281783"


def test_get_node_relationships_filters_to_curated_relations():
    """Mondo related_to relations outside the curated allowlist are dropped from the header."""
    disease = Entity(id="MONDO:0018310", name="Langerhans cell histiocytosis", category="biolink:Disease")
    location = _mondo_related_to_association(  # RO:0004026 disease has location -> cell (curated)
        subject="MONDO:0018310",
        original_predicate="RO:0004026",
        object="CL:0000453",
        object_label="Langerhans cell",
        object_category="biolink:Cell",
        object_taxon=None,
        object_taxon_label=None,
        id="loc",
    )
    characteristic = _mondo_related_to_association(  # RO:0000053 has characteristic -> PATO (excluded)
        subject="MONDO:0018310",
        original_predicate="RO:0000053",
        object="PATO:0000389",
        object_label="acute",
        object_category="biolink:NamedThing",
        object_taxon=None,
        object_taxon_label=None,
        id="char",
    )
    associations = AssociationResults(items=[location, characteristic], limit=500, offset=0, total=2)
    ro_term = Entity(id="RO:0004026", name="disease has location", category="biolink:NamedThing")

    with (
        patch.object(SolrImplementation, "get_associations", return_value=associations),
        patch.object(SolrImplementation, "get_entity", return_value=ro_term),
    ):
        relationships = SolrImplementation()._get_node_relationships(disease)

    assert [r.relation for r in relationships] == ["RO:0004026"]
    assert relationships[0].related_entity.id == "CL:0000453"


def test_get_node_relationships_orders_by_curated_sequence():
    """Relationships are ordered per MONDO_HEADER_RELATIONS regardless of Solr order."""
    disease = Entity(id="MONDO:1010417", name="d", category="biolink:Disease")
    # Provided out of order: infectious agent (last) before germline gene (first).
    agent = _mondo_related_to_association(
        original_predicate="RO:0014001",
        object="NCBITaxon:9606",
        object_label="bug",
        object_category="biolink:OrganismTaxon",
        object_taxon=None,
        object_taxon_label=None,
        id="agent",
    )
    gene = _mondo_related_to_association(original_predicate="RO:0004003", id="gene")
    associations = AssociationResults(items=[agent, gene], limit=500, offset=0, total=2)

    def fake_get_entity(curie, extra):
        return Entity(id=curie, name=f"label::{curie}", category="biolink:NamedThing")

    with (
        patch.object(SolrImplementation, "get_associations", return_value=associations),
        patch.object(SolrImplementation, "get_entity", side_effect=fake_get_entity),
    ):
        relationships = SolrImplementation()._get_node_relationships(disease)

    assert [r.relation for r in relationships] == ["RO:0004003", "RO:0014001"]


def test_get_generic_entity_grid_accepts_multiple_row_categories():
    """get_generic_entity_grid should accept row_assoc_categories as a list."""
    mock_entity = MagicMock()
    mock_entity.category = "biolink:Disease"
    mock_entity.configure_mock(name="Type 2 diabetes mellitus")

    with (
        patch.object(SolrImplementation, "get_entity", return_value=mock_entity),
        patch.object(SolrImplementation, "_get_entity_name", return_value="Type 2 diabetes mellitus"),
        patch.object(SolrImplementation, "_raw_solr_query") as mock_query,
    ):
        mock_query.return_value = {"response": {"docs": []}}

        si = SolrImplementation()

        # This should not raise TypeError - it should accept row_assoc_categories
        result = si.get_generic_entity_grid(
            context_id="MONDO:0005148",
            column_assoc_categories=["biolink:DiseaseToPhenotypicFeatureAssociation"],
            row_assoc_categories=[
                "biolink:DiseaseToPhenotypicFeatureAssociation",
                "biolink:CaseToPhenotypicFeatureAssociation",
            ],
        )

        # Verify the call went through
        assert result is not None


# =====================================================================
# Tests for get_entity descendant stripping
# =====================================================================


def test_get_entity_strips_descendant_lists():
    """get_entity should strip has_descendant/has_descendant_label from the response."""
    solr_doc = {
        "id": "UBERON:0000061",
        "category": "biolink:AnatomicalEntity",
        "name": "anatomical structure",
        "provided_by": "phenio_nodes",
        "has_descendant": [f"UBERON:{i:07d}" for i in range(100)],
        "has_descendant_label": [f"structure {i}" for i in range(100)],
        "has_descendant_count": 100,
    }

    with (
        patch("monarch_py.implementations.solr.solr_implementation.SolrService") as mock_solr_cls,
        patch.object(SolrImplementation, "_get_cross_species_term_clique", return_value=None),
        patch.object(SolrImplementation, "_get_node_hierarchy", return_value=None),
        patch.object(SolrImplementation, "get_association_counts") as mock_counts,
        patch.object(SolrImplementation, "_get_mapped_entities", return_value=[]),
    ):
        mock_solr_cls.return_value.get.return_value = solr_doc
        mock_counts.return_value.items = []

        node = SolrImplementation().get_entity("UBERON:0000061", extra=True)

        assert node.has_descendant is None
        assert node.has_descendant_label is None
        assert node.has_descendant_count == 100


# =====================================================================
# Tests for _get_entity_name
# =====================================================================


def _make_named_entity(name):
    entity = MagicMock()
    entity.configure_mock(name=name)
    return entity


def test_get_entity_name_returns_name():
    with patch.object(SolrImplementation, "get_entity", return_value=_make_named_entity("Huntington disease")):
        assert SolrImplementation()._get_entity_name("MONDO:0007078") == "Huntington disease"


@pytest.mark.parametrize(
    "get_entity_return,expected",
    [
        (None, "MONDO:0007078"),
        (_make_named_entity(None), "MONDO:0007078"),
    ],
    ids=["not-found", "name-is-none"],
)
def test_get_entity_name_fallback(get_entity_return, expected):
    with patch.object(SolrImplementation, "get_entity", return_value=get_entity_return):
        assert SolrImplementation()._get_entity_name("MONDO:0007078") == expected


def test_get_entity_name_on_exception():
    with patch.object(SolrImplementation, "get_entity", side_effect=Exception("Solr down")):
        assert SolrImplementation()._get_entity_name("MONDO:0007078") == "MONDO:0007078"


# =====================================================================
# Tests for get_case_phenotype_matrix
# =====================================================================


def test_case_phenotype_matrix_empty():
    with (
        patch.object(SolrImplementation, "_raw_solr_query") as mock_query,
        patch.object(SolrImplementation, "_get_entity_name", return_value="Test Disease"),
    ):
        mock_query.return_value = {"response": {"docs": []}}
        result = SolrImplementation().get_case_phenotype_matrix("MONDO:0007078")
        assert isinstance(result, CasePhenotypeMatrixResponse)
        assert result.total_cases == 0


def test_case_phenotype_matrix_limit_exceeded():
    with patch.object(SolrImplementation, "_raw_solr_query") as mock_query:
        mock_query.return_value = {
            "response": {"docs": [{"subject": f"CASE:{i}", "object": "MONDO:0007078"} for i in range(11)]}
        }
        with pytest.raises(ValueError, match="exceeds limit"):
            SolrImplementation().get_case_phenotype_matrix("MONDO:0007078", limit=10)


def test_case_phenotype_matrix_complete_flow():
    responses = [
        {
            "response": {
                "docs": [
                    {"subject": "CASE:001", "subject_label": "Case 1", "object": "MONDO:0007078", "object_label": "D"}
                ]
            }
        },
        {
            "response": {
                "docs": [
                    {
                        "subject": "CASE:001",
                        "object": "HP:001",
                        "object_label": "P1",
                        "object_closure": ["HP:001", "UPHENO:0001001"],
                    }
                ]
            },
            "facet_counts": {"facet_queries": {}},
        },
    ]
    call_idx = [0]

    def side_effect(params):
        i = call_idx[0]
        call_idx[0] += 1
        return responses[i]

    with (
        patch.object(SolrImplementation, "_raw_solr_query", side_effect=side_effect),
        patch.object(SolrImplementation, "_get_entity_name", return_value="Test Disease"),
    ):
        result = SolrImplementation().get_case_phenotype_matrix("MONDO:0007078")
        assert result.total_cases == 1
        assert result.disease_id == "MONDO:0007078"


# =====================================================================
# Tests for get_entity_grid
# =====================================================================


def test_entity_grid_empty():
    with (
        patch.object(SolrImplementation, "_raw_solr_query") as mock_query,
        patch.object(SolrImplementation, "_get_entity_name", return_value="Test Entity"),
    ):
        mock_query.return_value = {"response": {"docs": []}}
        result = SolrImplementation().get_entity_grid(context_id="MONDO:0007078", grid_type="case-phenotype")
        assert isinstance(result, EntityGridResponse)
        assert result.total_columns == 0


def test_entity_grid_limit_exceeded():
    with patch.object(SolrImplementation, "_raw_solr_query") as mock_query:
        mock_query.return_value = {
            "response": {"docs": [{"subject": f"CASE:{i}", "object": "MONDO:0007078"} for i in range(11)]}
        }
        with pytest.raises(ValueError, match="exceeds limit"):
            SolrImplementation().get_entity_grid(context_id="MONDO:0007078", grid_type="case-phenotype", limit=10)


def test_entity_grid_unknown_type():
    with pytest.raises(ValueError, match="Unknown grid type"):
        SolrImplementation().get_entity_grid(context_id="MONDO:0007078", grid_type="nonexistent-type")


def test_entity_grid_complete_flow():
    responses = [
        {"response": {"docs": [{"subject": "CASE:001", "subject_label": "Case 1", "object": "MONDO:0007078"}]}},
        {
            "response": {
                "docs": [
                    {
                        "subject": "CASE:001",
                        "object": "HP:001",
                        "object_label": "P1",
                        "object_closure": ["HP:001", "UPHENO:0001001"],
                    }
                ]
            },
            "facet_counts": {"facet_queries": {}},
        },
    ]
    call_idx = [0]

    def side_effect(params):
        i = call_idx[0]
        call_idx[0] += 1
        return responses[i]

    with (
        patch.object(SolrImplementation, "_raw_solr_query", side_effect=side_effect),
        patch.object(SolrImplementation, "_get_entity_name", return_value="Test Entity"),
    ):
        result = SolrImplementation().get_entity_grid(context_id="MONDO:0007078", grid_type="case-phenotype")
        assert result.total_columns == 1
        assert result.context_id == "MONDO:0007078"


# =====================================================================
# Helper for generic entity grid tests
# =====================================================================


def _mock_gene_entity(name="Test Gene"):
    mock = MagicMock()
    mock.category = "biolink:Gene"
    mock.configure_mock(name=name)
    return mock


# =====================================================================
# Tests for get_generic_entity_grid
# =====================================================================


def test_generic_grid_empty():
    with (
        patch.object(SolrImplementation, "get_entity", return_value=_mock_gene_entity()),
        patch.object(SolrImplementation, "_get_entity_name", return_value="Test Gene"),
        patch.object(SolrImplementation, "_raw_solr_query") as mock_query,
    ):
        mock_query.return_value = {"response": {"docs": []}}
        result = SolrImplementation().get_generic_entity_grid(
            context_id="HGNC:4851",
            column_assoc_categories=["biolink:CausalGeneToDiseaseAssociation"],
            row_assoc_categories=["biolink:DiseaseToPhenotypicFeatureAssociation"],
        )
        assert result.total_columns == 0


def test_generic_grid_limit_exceeded():
    with (
        patch.object(SolrImplementation, "get_entity", return_value=_mock_gene_entity()),
        patch.object(SolrImplementation, "_raw_solr_query") as mock_query,
    ):
        mock_query.return_value = {
            "response": {"docs": [{"object": f"MONDO:{i:07d}", "subject": "HGNC:4851"} for i in range(11)]}
        }
        with pytest.raises(ValueError, match="exceeds limit"):
            SolrImplementation().get_generic_entity_grid(
                context_id="HGNC:4851",
                column_assoc_categories=["biolink:CausalGeneToDiseaseAssociation"],
                row_assoc_categories=["biolink:DiseaseToPhenotypicFeatureAssociation"],
                limit=10,
            )


def test_generic_grid_context_not_found():
    with patch.object(SolrImplementation, "get_entity", return_value=None):
        with pytest.raises(ValueError, match="not found"):
            SolrImplementation().get_generic_entity_grid(
                context_id="HGNC:NONEXISTENT",
                column_assoc_categories=["biolink:CausalGeneToDiseaseAssociation"],
                row_assoc_categories=["biolink:DiseaseToPhenotypicFeatureAssociation"],
            )


def test_generic_grid_field_mapping():
    with (
        patch.object(SolrImplementation, "get_entity", return_value=_mock_gene_entity()),
        patch.object(SolrImplementation, "_get_entity_name", return_value="Test Gene"),
        patch.object(SolrImplementation, "_raw_solr_query") as mock_query,
    ):
        mock_query.return_value = {"response": {"docs": []}}
        result = SolrImplementation().get_generic_entity_grid(
            context_id="HGNC:4851",
            column_assoc_categories=["biolink:CausalGeneToDiseaseAssociation"],
            row_assoc_categories=["biolink:DiseaseToPhenotypicFeatureAssociation"],
        )
        assert result is not None


def test_generic_grid_column_sorting():
    col_result = {
        "response": {
            "docs": [
                {
                    "object": "MONDO:001",
                    "object_label": "D1",
                    "subject": "HGNC:4851",
                    "subject_label": "HTT",
                    "category": "biolink:CorrelatedGeneToDiseaseAssociation",
                },
                {
                    "object": "MONDO:002",
                    "object_label": "D2",
                    "subject": "HGNC:4851",
                    "subject_label": "HTT",
                    "category": "biolink:CausalGeneToDiseaseAssociation",
                },
            ]
        }
    }
    row_result = {"response": {"docs": []}, "facet_counts": {"facet_queries": {}}}
    call_idx = [0]

    def side_effect(params):
        i = call_idx[0]
        call_idx[0] += 1
        return col_result if i == 0 else row_result

    with (
        patch.object(SolrImplementation, "get_entity", return_value=_mock_gene_entity("HTT")),
        patch.object(SolrImplementation, "_get_entity_name", return_value="HTT"),
        patch.object(SolrImplementation, "_raw_solr_query", side_effect=side_effect),
    ):
        result = SolrImplementation().get_generic_entity_grid(
            context_id="HGNC:4851",
            column_assoc_categories=[
                "biolink:CausalGeneToDiseaseAssociation",
                "biolink:CorrelatedGeneToDiseaseAssociation",
            ],
            row_assoc_categories=["biolink:DiseaseToPhenotypicFeatureAssociation"],
            group_columns_by_category=True,
        )
        assert result.columns[0].source_association_category == "biolink:CausalGeneToDiseaseAssociation"
        assert result.columns[1].source_association_category == "biolink:CorrelatedGeneToDiseaseAssociation"


@pytest.mark.parametrize("row_grouping", ["histopheno", "none"])
def test_generic_grid_row_grouping(row_grouping):
    with (
        patch.object(SolrImplementation, "get_entity", return_value=_mock_gene_entity()),
        patch.object(SolrImplementation, "_get_entity_name", return_value="Test Gene"),
        patch.object(SolrImplementation, "_raw_solr_query") as mock_query,
    ):
        mock_query.return_value = {"response": {"docs": []}}
        result = SolrImplementation().get_generic_entity_grid(
            context_id="HGNC:4851",
            column_assoc_categories=["biolink:CausalGeneToDiseaseAssociation"],
            row_assoc_categories=["biolink:DiseaseToPhenotypicFeatureAssociation"],
            row_grouping=row_grouping,
        )
        assert result is not None


def test_generic_grid_entity_list_category():
    mock_entity = _mock_gene_entity()
    mock_entity.category = ["biolink:Gene", "biolink:NamedThing"]

    with (
        patch.object(SolrImplementation, "get_entity", return_value=mock_entity),
        patch.object(SolrImplementation, "_get_entity_name", return_value="Test Gene"),
        patch.object(SolrImplementation, "_raw_solr_query") as mock_query,
    ):
        mock_query.return_value = {"response": {"docs": []}}
        result = SolrImplementation().get_generic_entity_grid(
            context_id="HGNC:4851",
            column_assoc_categories=["biolink:CausalGeneToDiseaseAssociation"],
            row_assoc_categories=["biolink:DiseaseToPhenotypicFeatureAssociation"],
        )
        assert result is not None


# =====================================================================
# Tests for _get_cross_species_term_clique
# =====================================================================


def _make_entity(id, category=None, name=None):
    return Entity(id=id, category=category, name=name)


def _make_association(subject, predicate, obj, **kwargs):
    # API responses (and AssociationResults.items) carry ExpandedAssociation now
    # (Association = imported Solr-truth shape; ExpandedAssociation = + app-computed
    # link decorations). The test builds responses, so build the API class.
    return ExpandedAssociation(
        id=f"{subject}-{predicate}-{obj}",
        subject=subject,
        predicate=predicate,
        object=obj,
        knowledge_level="not_provided",
        agent_type="not_provided",
        **kwargs,
    )


def _make_assoc_results(items):
    return AssociationResults(items=items, limit=500, offset=0, total=len(items))


def test_cross_species_clique_non_phenotypic_returns_none():
    """Entities with prefixes not in CROSS_SPECIES or SPECIES_SPECIFIC lists should return None."""
    entity = _make_entity("HGNC:4851", category="biolink:Gene")
    si = SolrImplementation()
    result = si._get_cross_species_term_clique(entity)
    assert result is None


def test_cross_species_clique_species_neutral_returns_none():
    """Species-neutral ontologies like CL and GO should not get a clique."""
    si = SolrImplementation()
    for id, category in [("CL:0000540", "biolink:Cell"), ("GO:0110165", "biolink:CellularComponent")]:
        entity = _make_entity(id, category=category)
        result = si._get_cross_species_term_clique(entity)
        assert result is None, f"{id} should not get a cross-species clique"


def test_cross_species_clique_filters_species_neutral_children():
    """CL and GO children of a UBERON root should be excluded from the clique."""
    root = _make_entity("UBERON:0000061", category="biolink:AnatomicalEntity", name="anatomical structure")
    zfa_child = _make_entity("ZFA:0000037", name="anatomical structure")
    cl_child = _make_entity("CL:0000000", name="cell")

    vertical_assocs = [
        _make_association("ZFA:0000037", "biolink:subclass_of", "UBERON:0000061"),
    ]

    with (
        patch.object(
            SolrImplementation,
            "get_counterpart_entities",
            return_value=[zfa_child, cl_child],
        ),
        patch.object(
            SolrImplementation,
            "get_associations",
            side_effect=[_make_assoc_results(vertical_assocs)],
        ),
    ):
        si = SolrImplementation()
        result = si._get_cross_species_term_clique(root)

        assert result is not None
        child_ids = [c.id for c in result.clique_entities]
        assert "ZFA:0000037" in child_ids
        assert "CL:0000000" not in child_ids


def test_cross_species_clique_root_term():
    """When given a UPHENO root term, should find species-specific children."""
    root = _make_entity("UPHENO:0001471", category="biolink:PhenotypicFeature", name="increased size of the heart")
    hp_child = _make_entity("HP:0001640", name="Cardiomegaly")
    mp_child = _make_entity("MP:0000274", name="enlarged heart")

    vertical_assocs = [
        _make_association("HP:0001640", "biolink:subclass_of", "UPHENO:0001471"),
        _make_association("MP:0000274", "biolink:subclass_of", "UPHENO:0001471"),
    ]

    with (
        patch.object(
            SolrImplementation,
            "get_counterpart_entities",
            return_value=[hp_child, mp_child],
        ),
        patch.object(
            SolrImplementation,
            "get_associations",
            side_effect=[
                _make_assoc_results(vertical_assocs),  # vertical
                _make_assoc_results([]),  # sideways
            ],
        ),
    ):
        si = SolrImplementation()
        result = si._get_cross_species_term_clique(root)

        assert result is not None
        assert isinstance(result, CrossSpeciesTermClique)
        assert result.root_term.id == "UPHENO:0001471"
        assert len(result.clique_entities) == 2
        assert len(result.clique_associations) == 2


def test_cross_species_clique_child_term():
    """When given a species-specific term (HP), should find parent and siblings."""
    entity = _make_entity("HP:0001640", category="biolink:PhenotypicFeature", name="Cardiomegaly")
    root = _make_entity("UPHENO:0001471", name="increased size of the heart")
    mp_child = _make_entity("MP:0000274", name="enlarged heart")
    hp_child = _make_entity("HP:0001640", name="Cardiomegaly")

    vertical_assocs = [
        _make_association("HP:0001640", "biolink:subclass_of", "UPHENO:0001471"),
        _make_association("MP:0000274", "biolink:subclass_of", "UPHENO:0001471"),
    ]
    sideways_assocs = [
        _make_association("HP:0001640", "biolink:same_as", "MP:0000274"),
    ]

    call_count = [0]

    def mock_counterpart(this_entity, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            return [root]  # _find_cross_species_parent
        else:
            return [hp_child, mp_child]  # _get_species_specific_children

    with (
        patch.object(SolrImplementation, "get_counterpart_entities", side_effect=mock_counterpart),
        patch.object(
            SolrImplementation,
            "get_associations",
            side_effect=[
                _make_assoc_results(vertical_assocs),
                _make_assoc_results(sideways_assocs),
            ],
        ),
    ):
        si = SolrImplementation()
        result = si._get_cross_species_term_clique(entity)

        assert result is not None
        assert result.root_term.id == "UPHENO:0001471"
        assert len(result.clique_entities) == 2
        # 2 vertical + 1 sideways
        assert len(result.clique_associations) == 3


def test_cross_species_clique_no_parent_returns_none():
    """Species-specific term with no UPHENO/UBERON parent should return None."""
    entity = _make_entity("HP:9999999", category="biolink:PhenotypicFeature")

    with patch.object(SolrImplementation, "get_counterpart_entities", return_value=[]):
        si = SolrImplementation()
        result = si._get_cross_species_term_clique(entity)
        assert result is None


def test_cross_species_clique_no_children_returns_none():
    """Root term with no species-specific children should return None."""
    root = _make_entity("UPHENO:0001471", category="biolink:PhenotypicFeature")

    with patch.object(SolrImplementation, "get_counterpart_entities", return_value=[]):
        si = SolrImplementation()
        result = si._get_cross_species_term_clique(root)
        assert result is None


def test_cross_species_clique_filters_non_clique_sideways():
    """Sideways associations where the object is not in the clique should be filtered out."""
    root = _make_entity("UPHENO:0001471", category="biolink:PhenotypicFeature")
    hp_child = _make_entity("HP:0001640", name="Cardiomegaly")
    mp_child = _make_entity("MP:0000274", name="enlarged heart")

    vertical_assocs = [
        _make_association("HP:0001640", "biolink:subclass_of", "UPHENO:0001471"),
        _make_association("MP:0000274", "biolink:subclass_of", "UPHENO:0001471"),
    ]
    # This association has an object NOT in the clique - should be filtered
    sideways_all = [
        _make_association("HP:0001640", "biolink:same_as", "MP:0000274"),  # in clique
        _make_association("HP:0001640", "biolink:same_as", "ZP:9999999"),  # NOT in clique
    ]

    with (
        patch.object(SolrImplementation, "get_counterpart_entities", return_value=[hp_child, mp_child]),
        patch.object(
            SolrImplementation,
            "get_associations",
            side_effect=[
                _make_assoc_results(vertical_assocs),
                _make_assoc_results(sideways_all),
            ],
        ),
    ):
        si = SolrImplementation()
        result = si._get_cross_species_term_clique(root)

        assert result is not None
        sideways = [a for a in result.clique_associations if a.predicate != "biolink:subclass_of"]
        assert len(sideways) == 1
        assert sideways[0].object == "MP:0000274"


def test_deduplicate_sideways():
    """Bidirectional sideways edges should be deduplicated to one direction."""
    assocs = [
        _make_association("HP:0001640", "biolink:same_as", "MP:0000274"),
        _make_association("MP:0000274", "biolink:same_as", "HP:0001640"),
        _make_association("HP:0001640", "biolink:homologous_to", "MP:0000274"),
        _make_association("MP:0000274", "biolink:homologous_to", "HP:0001640"),
    ]
    result = SolrImplementation._deduplicate_sideways(assocs)
    assert len(result) == 2
    predicates = {a.predicate for a in result}
    assert predicates == {"biolink:same_as", "biolink:homologous_to"}


def test_cross_species_clique_singleton_no_sideways():
    """A clique with only one child should not query for sideways associations."""
    root = _make_entity("UPHENO:0001471", category="biolink:PhenotypicFeature")
    hp_child = _make_entity("HP:0001640", name="Cardiomegaly")

    vertical_assocs = [
        _make_association("HP:0001640", "biolink:subclass_of", "UPHENO:0001471"),
    ]

    with (
        patch.object(SolrImplementation, "get_counterpart_entities", return_value=[hp_child]),
        patch.object(
            SolrImplementation,
            "get_associations",
            side_effect=[_make_assoc_results(vertical_assocs)],
        ) as mock_assocs,
    ):
        si = SolrImplementation()
        result = si._get_cross_species_term_clique(root)

        assert result is not None
        assert len(result.clique_entities) == 1
        # Only vertical query, no sideways query
        assert mock_assocs.call_count == 1
