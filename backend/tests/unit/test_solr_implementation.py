import pytest
from unittest.mock import patch, MagicMock

from monarch_py.implementations.solr.solr_implementation import SolrImplementation
from monarch_py.datamodels.model import EntityGridResponse, CasePhenotypeMatrixResponse


def test_get_counterpart_entities_limit():
    # Make sure that we don't accidentally end up with the default limit again
    with patch.object(SolrImplementation, "get_associations") as mock_get_associations:
        si = SolrImplementation()
        si.get_counterpart_entities("MONDO:0007947")
        assert mock_get_associations.called
        assert mock_get_associations.call_args_list[0].kwargs["limit"] == 1000


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
# Tests for _get_entity_name and _get_disease_name
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


def test_get_disease_name_returns_name():
    with patch.object(SolrImplementation, "get_entity", return_value=_make_named_entity("Achondroplasia")):
        assert SolrImplementation()._get_disease_name("MONDO:0007078") == "Achondroplasia"


def test_get_disease_name_on_exception():
    with patch.object(SolrImplementation, "get_entity", side_effect=Exception("err")):
        assert SolrImplementation()._get_disease_name("MONDO:0007078") == "MONDO:0007078"


# =====================================================================
# Tests for get_case_phenotype_matrix
# =====================================================================


def test_case_phenotype_matrix_empty():
    with (
        patch.object(SolrImplementation, "_raw_solr_query") as mock_query,
        patch.object(SolrImplementation, "_get_disease_name", return_value="Test Disease"),
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
        patch.object(SolrImplementation, "_get_disease_name", return_value="Test Disease"),
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
