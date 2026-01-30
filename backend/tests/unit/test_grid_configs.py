"""Unit tests for grid configuration."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from monarch_py.datamodels.grid_configs import GridTypeConfig, get_grid_config
from monarch_py.datamodels.category_enums import AssociationCategory, EntityCategory
from monarch_py.api.main import app


class TestGridTypeConfigMultiCategory:
    """Test GridTypeConfig with multiple association categories."""

    def test_single_category_still_works(self):
        """Single category config should still work (backwards compatible)."""
        config = get_grid_config("case-phenotype")
        assert config.column_assoc_category == AssociationCategory.CASE_TO_DISEASE_ASSOCIATION

    def test_column_assoc_categories_returns_list(self):
        """Config should provide column_assoc_categories as a list."""
        config = get_grid_config("case-phenotype")
        categories = config.get_column_assoc_categories()
        assert isinstance(categories, list)
        assert AssociationCategory.CASE_TO_DISEASE_ASSOCIATION in categories

    def test_multi_category_config(self):
        """Config with multiple categories should return all."""
        # Create a config with multiple categories
        config = GridTypeConfig(
            name="Multi-Category Test",
            context_category=EntityCategory.GENE,
            column_assoc_categories=[
                AssociationCategory.CAUSAL_GENE_TO_DISEASE_ASSOCIATION,
                AssociationCategory.CORRELATED_GENE_TO_DISEASE_ASSOCIATION,
            ],
            row_assoc_category=AssociationCategory.DISEASE_TO_PHENOTYPIC_FEATURE_ASSOCIATION,
            row_entity_category=EntityCategory.PHENOTYPIC_FEATURE,
            column_entity_category=EntityCategory.DISEASE,
        )

        categories = config.get_column_assoc_categories()
        assert len(categories) == 2
        assert AssociationCategory.CAUSAL_GENE_TO_DISEASE_ASSOCIATION in categories
        assert AssociationCategory.CORRELATED_GENE_TO_DISEASE_ASSOCIATION in categories


class TestGetGridConfig:
    """Test get_grid_config function."""

    def test_get_case_phenotype_config(self):
        """Should return case-phenotype config."""
        config = get_grid_config("case-phenotype")
        assert config.name == "Case-Phenotype"
        assert config.context_category == EntityCategory.DISEASE

    def test_get_disease_phenotype_config(self):
        """Should return disease-phenotype config."""
        config = get_grid_config("disease-phenotype")
        assert config.name == "Disease-Phenotype"
        assert config.context_category == EntityCategory.GENE

    def test_get_unknown_config_raises(self):
        """Should raise ValueError for unknown grid type."""
        with pytest.raises(ValueError, match="Unknown grid type"):
            get_grid_config("unknown-type")


class TestGenericEntityGridAPIMultiRowCategory:
    """Test /entity-grid endpoint accepts multiple row_association_category params."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_api_accepts_multiple_row_association_category(self, client):
        """API should accept multiple row_association_category query parameters."""
        from monarch_py.implementations.solr.solr_implementation import SolrImplementation
        from monarch_py.datamodels.model import EntityGridResponse

        # Mock the solr implementation to avoid actual Solr calls
        mock_response = EntityGridResponse(
            context_id="MONDO:0005148",
            context_name="Test Disease",
            context_category="biolink:Disease",
            total_columns=0,
            total_rows=0,
            columns=[],
            rows=[],
            bins=[],
            cells={},
        )

        with patch.object(SolrImplementation, "get_generic_entity_grid") as mock_get_grid:
            mock_get_grid.return_value = mock_response

            # Call API with multiple row_association_category params
            response = client.get(
                "/v3/api/entity-grid/MONDO:0005148",
                params={
                    "column_association_category": "biolink:CaseToDiseaseAssociation",
                    "row_association_category": [
                        "biolink:DiseaseToPhenotypicFeatureAssociation",
                        "biolink:CaseToPhenotypicFeatureAssociation",
                    ],
                },
            )

            # Should not return 422 validation error
            assert response.status_code == 200, f"Response: {response.json()}"

            # Verify the mock was called with row_assoc_categories as list
            mock_get_grid.assert_called_once()
            call_kwargs = mock_get_grid.call_args.kwargs
            assert "row_assoc_categories" in call_kwargs
            assert isinstance(call_kwargs["row_assoc_categories"], list)
            assert len(call_kwargs["row_assoc_categories"]) == 2

    def test_api_accepts_single_row_association_category(self, client):
        """API should still work with single row_association_category parameter."""
        from monarch_py.implementations.solr.solr_implementation import SolrImplementation
        from monarch_py.datamodels.model import EntityGridResponse

        mock_response = EntityGridResponse(
            context_id="MONDO:0005148",
            context_name="Test Disease",
            context_category="biolink:Disease",
            total_columns=0,
            total_rows=0,
            columns=[],
            rows=[],
            bins=[],
            cells={},
        )

        with patch.object(SolrImplementation, "get_generic_entity_grid") as mock_get_grid:
            mock_get_grid.return_value = mock_response

            # Call API with single row_association_category param
            response = client.get(
                "/v3/api/entity-grid/MONDO:0005148",
                params={
                    "column_association_category": "biolink:CaseToDiseaseAssociation",
                    "row_association_category": "biolink:DiseaseToPhenotypicFeatureAssociation",
                },
            )

            # Should work
            assert response.status_code == 200, f"Response: {response.json()}"

            # FastAPI should auto-wrap single value in list
            call_kwargs = mock_get_grid.call_args.kwargs
            assert "row_assoc_categories" in call_kwargs
            assert isinstance(call_kwargs["row_assoc_categories"], list)
            assert len(call_kwargs["row_assoc_categories"]) == 1
