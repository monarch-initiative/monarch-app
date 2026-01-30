"""Unit tests for grid data models."""
import pytest
from monarch_py.datamodels.model import GridColumnEntity


class TestGridColumnEntity:
    """Test GridColumnEntity model with source association fields."""

    def test_source_association_fields_optional(self):
        """Source association fields should be optional."""
        entity = GridColumnEntity(
            id="MONDO:0007078",
            category="biolink:Disease",
            is_direct=True,
        )
        assert entity.id == "MONDO:0007078"
        assert entity.source_association_category is None
        assert entity.source_association_predicate is None
        assert entity.source_association_publications is None
        assert entity.source_association_evidence_count is None

    def test_source_association_fields_populated(self):
        """Source association fields can be populated."""
        entity = GridColumnEntity(
            id="MONDO:0007078",
            label="Achondroplasia",
            category="biolink:Disease",
            is_direct=True,
            source_association_category="biolink:CausalGeneToDiseaseAssociation",
            source_association_predicate="biolink:causes",
            source_association_publications=["PMID:12345", "PMID:67890"],
            source_association_evidence_count=5,
            source_association_primary_knowledge_source="infores:orphanet",
        )
        assert entity.source_association_category == "biolink:CausalGeneToDiseaseAssociation"
        assert entity.source_association_predicate == "biolink:causes"
        assert entity.source_association_publications == ["PMID:12345", "PMID:67890"]
        assert entity.source_association_evidence_count == 5
        assert entity.source_association_primary_knowledge_source == "infores:orphanet"

    def test_json_serialization_includes_source_association(self):
        """Model should serialize source association fields to JSON."""
        entity = GridColumnEntity(
            id="MONDO:0007078",
            category="biolink:Disease",
            is_direct=True,
            source_association_category="biolink:CausalGeneToDiseaseAssociation",
        )
        data = entity.model_dump()
        assert "source_association_category" in data
        assert data["source_association_category"] == "biolink:CausalGeneToDiseaseAssociation"
