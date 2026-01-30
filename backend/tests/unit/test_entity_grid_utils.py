"""Unit tests for entity grid utilities."""
import pytest
from monarch_py.utils.entity_grid_utils import _build_columns, sort_columns_by_category
from monarch_py.datamodels.grid_configs import get_grid_config, GridTypeConfig
from monarch_py.datamodels.model import GridColumnEntity
from monarch_py.datamodels.category_enums import AssociationCategory, EntityCategory


class TestBuildColumns:
    """Test _build_columns function."""

    @pytest.fixture
    def sample_column_docs(self):
        """Sample Solr docs for column building."""
        return [
            {
                "subject": "CASE:001",
                "subject_label": "Case 1",
                "object": "MONDO:0007078",
                "object_label": "Achondroplasia",
                "category": "biolink:CaseToDiseaseAssociation",
                "predicate": "biolink:has_phenotype",
                "publications": ["PMID:12345"],
                "primary_knowledge_source": "infores:hpo",
            },
            {
                "subject": "CASE:002",
                "subject_label": "Case 2",
                "object": "MONDO:0007078",
                "object_label": "Achondroplasia",
                "category": "biolink:CaseToDiseaseAssociation",
                "predicate": "biolink:has_phenotype",
                "publications": ["PMID:67890", "PMID:11111"],
                "primary_knowledge_source": "infores:hpo",
            },
        ]

    def test_columns_include_source_association_data(self, sample_column_docs):
        """Built columns should include source association fields."""
        config = get_grid_config("case-phenotype")
        columns = _build_columns(
            column_docs=sample_column_docs,
            context_id="MONDO:0007078",
            config=config,
        )

        assert len(columns) == 2

        col1 = columns[0]
        assert col1.source_association_category == "biolink:CaseToDiseaseAssociation"
        assert col1.source_association_predicate == "biolink:has_phenotype"
        assert col1.source_association_publications == ["PMID:12345"]
        assert col1.source_association_primary_knowledge_source == "infores:hpo"

    def test_columns_handle_missing_association_fields(self):
        """Columns should handle missing association fields gracefully."""
        config = get_grid_config("case-phenotype")
        docs = [
            {
                "subject": "CASE:001",
                "object": "MONDO:0007078",
                # No association fields
            }
        ]

        columns = _build_columns(docs, "MONDO:0007078", config)

        assert len(columns) == 1
        assert columns[0].source_association_category is None
        assert columns[0].source_association_predicate is None


class TestSortColumnsByCategory:
    """Test column sorting by association category."""

    def test_sort_columns_by_category(self):
        """Columns should be sortable by association category."""
        columns = [
            GridColumnEntity(
                id="MONDO:001",
                category="biolink:Disease",
                is_direct=True,
                source_association_category="biolink:CorrelatedGeneToDiseaseAssociation",
            ),
            GridColumnEntity(
                id="MONDO:002",
                category="biolink:Disease",
                is_direct=True,
                source_association_category="biolink:CausalGeneToDiseaseAssociation",
            ),
            GridColumnEntity(
                id="MONDO:003",
                category="biolink:Disease",
                is_direct=True,
                source_association_category="biolink:CorrelatedGeneToDiseaseAssociation",
            ),
        ]

        category_order = [
            "biolink:CausalGeneToDiseaseAssociation",
            "biolink:CorrelatedGeneToDiseaseAssociation",
        ]

        sorted_cols = sort_columns_by_category(columns, category_order)

        # Causal should come first
        assert sorted_cols[0].id == "MONDO:002"
        # Then correlated
        assert sorted_cols[1].source_association_category == "biolink:CorrelatedGeneToDiseaseAssociation"
        assert sorted_cols[2].source_association_category == "biolink:CorrelatedGeneToDiseaseAssociation"

    def test_sort_preserves_order_within_category(self):
        """Sort should preserve original order within same category."""
        columns = [
            GridColumnEntity(
                id="A",
                category="biolink:Disease",
                is_direct=True,
                source_association_category="biolink:Causal",
            ),
            GridColumnEntity(
                id="B",
                category="biolink:Disease",
                is_direct=True,
                source_association_category="biolink:Causal",
            ),
            GridColumnEntity(
                id="C",
                category="biolink:Disease",
                is_direct=True,
                source_association_category="biolink:Causal",
            ),
        ]

        sorted_cols = sort_columns_by_category(columns, ["biolink:Causal"])

        assert [c.id for c in sorted_cols] == ["A", "B", "C"]

    def test_sort_empty_list(self):
        """Should handle empty list."""
        assert sort_columns_by_category([], ["biolink:Causal"]) == []

    def test_sort_empty_category_order(self):
        """Should return original order when no category order specified."""
        columns = [
            GridColumnEntity(id="A", category="biolink:Disease", is_direct=True),
            GridColumnEntity(id="B", category="biolink:Disease", is_direct=True),
        ]

        sorted_cols = sort_columns_by_category(columns, [])
        assert [c.id for c in sorted_cols] == ["A", "B"]
