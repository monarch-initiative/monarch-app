"""API endpoints for entity grids.

Provides generic entity x entity grid endpoints that support:
- Disease -> Case × Phenotype (case-phenotype-grid)
- Gene -> Disease × Phenotype (disease-phenotype-grid)
- Gene -> Ortholog × Phenotype (ortholog-phenotype-grid)
- Generic grids with configurable association categories
"""
from enum import Enum
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Path

from monarch_py.api.config import solr
from monarch_py.datamodels.model import EntityGridResponse
from monarch_py.datamodels.category_enums import AssociationCategory, EntityCategory


# Define row grouping options
class RowGrouping(str, Enum):
    """Row grouping options."""
    HISTOPHENO = "histopheno"
    NONE = "none"

router = APIRouter(
    tags=["entity-grid"],
    responses={
        400: {"description": "Column count exceeds limit, or ID category mismatch"},
        404: {"description": "Entity not found"},
        422: {"description": "Invalid entity ID format"},
    },
)


def _validate_entity_category(entity_id: str, expected_category: EntityCategory) -> None:
    """Validate that an entity exists and has the expected category.

    Args:
        entity_id: The entity ID to validate
        expected_category: The expected biolink category

    Raises:
        HTTPException: If entity not found or wrong category
    """
    solr_impl = solr()
    try:
        entity = solr_impl.get_entity(entity_id, extra=False)
        if entity is None:
            raise HTTPException(
                status_code=404,
                detail=f"Entity {entity_id} not found",
            )

        # Check category
        category = getattr(entity, "category", None)
        if category is None:
            raise HTTPException(
                status_code=400,
                detail=f"Entity {entity_id} has no category",
            )

        # Category can be a string or list
        categories = [category] if isinstance(category, str) else category
        if expected_category.value not in categories:
            raise HTTPException(
                status_code=400,
                detail=f"{entity_id} is not a {expected_category.name.lower().replace('_', ' ')}. "
                f"Expected category: {expected_category.value}",
            )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=404,
            detail=f"Entity {entity_id} not found",
        )


def _get_grid(
    context_id: str,
    grid_type: str,
    direct: bool,
    limit: int,
) -> EntityGridResponse:
    """Get entity grid using the generic implementation.

    Args:
        context_id: The context entity ID
        grid_type: The grid type identifier
        direct: If True, only direct associations
        limit: Maximum column entities

    Returns:
        EntityGridResponse

    Raises:
        HTTPException: On errors
    """
    solr_impl = solr()
    try:
        return solr_impl.get_entity_grid(
            context_id=context_id,
            grid_type=grid_type,
            direct_only=direct,
            limit=limit,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{context_id}/case-phenotype-grid",
    response_model=EntityGridResponse,
    summary="Get case-phenotype grid for a disease",
    description="""
    Returns a grid of cases (patients) and their phenotypes for a given disease.

    The grid includes:
    - **columns**: List of case entities with the disease
    - **rows**: List of phenotypes observed across all cases
    - **bins**: Body system categories (HistoPheno) with phenotype counts
    - **cells**: Map of case:phenotype pairs to observation details

    Use `direct=true` (default) to get only cases with exactly this disease.
    Use `direct=false` to include cases with descendant diseases (subtypes).
    """,
)
async def get_case_phenotype_grid(
    context_id: str = Path(
        ...,
        description="MONDO disease ID",
        examples=["MONDO:0007078"],
    ),
    direct: bool = Query(
        True,
        description="Only include cases with exactly this disease",
    ),
    limit: int = Query(
        1000,
        ge=1,
        le=1000,
        description="Maximum number of cases (columns)",
    ),
) -> EntityGridResponse:
    """Get case-phenotype grid for a disease.

    The context_id must be a disease ID (e.g., MONDO:0007078).
    """
    _validate_entity_category(context_id, EntityCategory.DISEASE)
    return _get_grid(context_id, "case-phenotype", direct, limit)


@router.get(
    "/{context_id}/disease-phenotype-grid",
    response_model=EntityGridResponse,
    summary="Get disease-phenotype grid for a gene",
    description="""
    Returns a grid of diseases and their phenotypes for a given gene.

    The grid shows diseases causally associated with the gene and the
    phenotypes associated with each disease.

    - **columns**: List of disease entities associated with the gene
    - **rows**: List of phenotypes observed across all diseases
    - **bins**: Body system categories (HistoPheno) with phenotype counts
    - **cells**: Map of disease:phenotype pairs to observation details
    """,
)
async def get_disease_phenotype_grid(
    context_id: str = Path(
        ...,
        description="Gene ID (e.g., HGNC ID)",
        examples=["HGNC:4851"],
    ),
    direct: bool = Query(
        True,
        description="Only include directly associated diseases",
    ),
    limit: int = Query(
        500,
        ge=1,
        le=500,
        description="Maximum number of diseases (columns)",
    ),
) -> EntityGridResponse:
    """Get disease-phenotype grid for a gene.

    The context_id must be a gene ID (e.g., HGNC:4851).
    """
    _validate_entity_category(context_id, EntityCategory.GENE)
    return _get_grid(context_id, "disease-phenotype", direct, limit)


@router.get(
    "/{context_id}/ortholog-phenotype-grid",
    response_model=EntityGridResponse,
    summary="Get ortholog-phenotype grid for a gene",
    description="""
    Returns a grid of orthologs and their phenotypes for a given gene.

    The grid shows orthologous genes and the phenotypes associated with
    each ortholog (typically from model organisms).

    - **columns**: List of orthologous genes
    - **rows**: List of phenotypes observed across all orthologs
    - **bins**: Body system categories (HistoPheno) with phenotype counts
    - **cells**: Map of ortholog:phenotype pairs to observation details
    """,
)
async def get_ortholog_phenotype_grid(
    context_id: str = Path(
        ...,
        description="Gene ID (e.g., HGNC ID)",
        examples=["HGNC:4851"],
    ),
    direct: bool = Query(
        True,
        description="Only include direct orthologs",
    ),
    limit: int = Query(
        500,
        ge=1,
        le=500,
        description="Maximum number of orthologs (columns)",
    ),
) -> EntityGridResponse:
    """Get ortholog-phenotype grid for a gene.

    The context_id must be a gene ID (e.g., HGNC:4851).
    """
    _validate_entity_category(context_id, EntityCategory.GENE)
    return _get_grid(context_id, "ortholog-phenotype", direct, limit)


# =============================================================================
# Generic Entity Grid Endpoint
# =============================================================================


@router.get(
    "-grid/{context_id}",
    response_model=EntityGridResponse,
    summary="Get generic entity grid with configurable associations",
    description="""
    Returns a generic entity × entity grid with configurable association categories.

    This endpoint allows you to specify:
    - **column_association_category**: One or more association categories for the
      context → column hop (e.g., causal gene-disease, correlated gene-disease)
    - **row_association_category**: The association category for the column → row hop
    - **row_grouping**: How to group rows (histopheno for body systems, or none)
    - **group_columns_by_category**: Whether to sort columns by their source association

    Example: To get a grid of diseases (causal + correlated) and their phenotypes for a gene:
    ```
    GET /entity-grid/HGNC:4851?column_association_category=biolink:CausalGeneToDiseaseAssociation
        &column_association_category=biolink:CorrelatedGeneToDiseaseAssociation
        &row_association_category=biolink:DiseaseToPhenotypicFeatureAssociation
        &group_columns_by_category=true
    ```

    The response includes source_association_category on each column entity,
    allowing the frontend to display different column groups.
    """,
)
async def get_generic_entity_grid(
    context_id: str = Path(
        ...,
        description="Context entity ID (gene, disease, etc.)",
        examples=["HGNC:4851", "MONDO:0007078"],
    ),
    column_association_category: List[AssociationCategory] = Query(
        ...,
        description="Association category/categories for context → column",
        examples=["biolink:CausalGeneToDiseaseAssociation"],
    ),
    row_association_category: List[AssociationCategory] = Query(
        ...,
        description="Association category/categories for column → row",
        examples=["biolink:DiseaseToPhenotypicFeatureAssociation"],
    ),
    row_grouping: RowGrouping = Query(
        RowGrouping.HISTOPHENO,
        description="How to group rows",
    ),
    group_columns_by_category: bool = Query(
        False,
        description="Sort columns by association category",
    ),
    direct: bool = Query(
        True,
        description="Only include direct associations (not via closure)",
    ),
    limit: int = Query(
        500,
        ge=1,
        le=1000,
        description="Maximum number of column entities",
    ),
) -> EntityGridResponse:
    """Get a generic entity grid with configurable association categories.

    This endpoint dynamically constructs a grid based on the specified
    association categories, allowing flexible exploration of relationships.
    """
    solr_impl = solr()

    # Convert enum values to strings
    column_categories = [cat.value for cat in column_association_category]
    row_categories = [cat.value for cat in row_association_category]

    try:
        return solr_impl.get_generic_entity_grid(
            context_id=context_id,
            column_assoc_categories=column_categories,
            row_assoc_categories=row_categories,
            row_grouping=row_grouping.value,
            group_columns_by_category=group_columns_by_category,
            direct_only=direct,
            limit=limit,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
