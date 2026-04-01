"""Tests for case-phenotype matrix data models."""

import pytest
from monarch_py.datamodels.model import (
    CasePhenotypeMatrixResponse,
    CaseEntity,
    CasePhenotype,
    HistoPhenoBin,
    CasePhenotypeCellData,
)


class TestCaseEntity:
    """Test CaseEntity model."""

    def test_create_direct_case(self):
        """A direct case should have is_direct=True and no source_disease."""
        case = CaseEntity(
            id="MONARCH:case123",
            label="Patient 1",
            is_direct=True,
        )
        assert case.id == "MONARCH:case123"
        assert case.is_direct is True
        assert case.source_disease_id is None

    def test_create_indirect_case(self):
        """An indirect case should have is_direct=False and source disease info."""
        case = CaseEntity(
            id="MONARCH:case456",
            label="Patient 2",
            is_direct=False,
            source_disease_id="MONDO:0007079",
            source_disease_label="Specific Disease Subtype",
        )
        assert case.is_direct is False
        assert case.source_disease_id == "MONDO:0007079"


class TestCasePhenotype:
    """Test CasePhenotype model."""

    def test_phenotype_with_bin(self):
        """Phenotype should have bin assignment."""
        phenotype = CasePhenotype(
            id="HP:0001250",
            label="Seizure",
            bin_id="UPHENO:0004523",  # nervous system
        )
        assert phenotype.bin_id == "UPHENO:0004523"


class TestHistoPhenoBin:
    """Test HistoPhenoBin model."""

    def test_bin_with_count(self):
        """Bin should track phenotype count."""
        bin = HistoPhenoBin(
            id="UPHENO:0002964",
            label="skeletal system",
            phenotype_count=42,
        )
        assert bin.phenotype_count == 42


class TestCasePhenotypeCellData:
    """Test CasePhenotypeCellData model."""

    @pytest.mark.parametrize(
        "cell_kwargs,expected_attr,expected_value",
        [
            ({"present": True}, "present", True),
            ({"present": True}, "negated", None),
            ({"present": True, "negated": True}, "negated", True),
            ({"present": True, "negated": False}, "negated", False),
            ({"present": True, "onset_qualifier": "P2Y"}, "onset_qualifier", "P2Y"),
            ({"present": True, "onset_qualifier": "P6M"}, "onset_qualifier", "P6M"),
            ({"present": True, "onset_qualifier_label": "2 years"}, "onset_qualifier_label", "2 years"),
        ],
    )
    def test_cell_attributes(self, cell_kwargs, expected_attr, expected_value):
        """Cell should store various attributes correctly."""
        cell = CasePhenotypeCellData(**cell_kwargs)
        assert getattr(cell, expected_attr) == expected_value

    @pytest.mark.parametrize(
        "publications,expected_count",
        [
            (["PMID:12345"], 1),
            (["PMID:12345", "PMID:67890"], 2),
            ([], 0),
            (None, None),
        ],
    )
    def test_cell_publications(self, publications, expected_count):
        """Cell should handle publication lists."""
        cell = CasePhenotypeCellData(present=True, publications=publications)
        if expected_count is None:
            assert cell.publications is None
        else:
            assert len(cell.publications) == expected_count


class TestCasePhenotypeMatrixResponse:
    """Test complete matrix response model."""

    def test_empty_matrix(self):
        """Matrix with no cases or phenotypes."""
        matrix = CasePhenotypeMatrixResponse(
            disease_id="MONDO:0007078",
            disease_name="Test Disease",
            total_cases=0,
            total_phenotypes=0,
            cases=[],
            phenotypes=[],
            bins=[],
            cells={},
        )
        assert matrix.total_cases == 0
        assert len(matrix.cases) == 0

    def test_matrix_with_data(self):
        """Matrix with cases, phenotypes, and cells."""
        case = CaseEntity(id="MONARCH:case1", label="P1", is_direct=True)
        phenotype = CasePhenotype(id="HP:0001250", label="Seizure", bin_id="UPHENO:0004523")
        bin = HistoPhenoBin(id="UPHENO:0004523", label="nervous system", phenotype_count=1)
        cell_key = "MONARCH:case1:HP:0001250"
        cell = CasePhenotypeCellData(present=True)

        matrix = CasePhenotypeMatrixResponse(
            disease_id="MONDO:0007078",
            disease_name="Achondroplasia",
            total_cases=1,
            total_phenotypes=1,
            cases=[case],
            phenotypes=[phenotype],
            bins=[bin],
            cells={cell_key: cell},
        )
        assert matrix.total_cases == 1
        assert cell_key in matrix.cells
