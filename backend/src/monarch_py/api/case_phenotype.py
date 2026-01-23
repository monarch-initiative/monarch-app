"""API endpoint for case-phenotype matrix."""
import re
from fastapi import APIRouter, HTTPException, Query, Path

from monarch_py.api.config import solr
from monarch_py.datamodels.model import CasePhenotypeMatrixResponse

router = APIRouter(
    tags=["case-phenotype"],
    responses={
        400: {"description": "Case count exceeds limit, or ID is not a disease"},
        404: {"description": "Disease not found"},
        422: {"description": "Invalid disease ID format"},
    },
)

DISEASE_ID_PATTERN = re.compile(r"^MONDO:\d{7}$")


def validate_disease_id(disease_id: str) -> str:
    """Validate and normalize disease ID.

    Args:
        disease_id: The disease ID to validate

    Returns:
        Normalized disease ID

    Raises:
        HTTPException: If ID is invalid
    """
    if not disease_id:
        raise HTTPException(
            status_code=422,
            detail="Disease ID is required",
        )

    normalized = disease_id.strip().upper()
    if "_" in normalized and ":" not in normalized:
        normalized = normalized.replace("_", ":", 1)

    if not DISEASE_ID_PATTERN.match(normalized):
        raise HTTPException(
            status_code=422,
            detail=f"Invalid disease ID format: '{disease_id}'. Expected format: MONDO:0000000",
        )

    return normalized


def _is_disease_entity(entity) -> bool:
    """Check if entity is a disease.

    Args:
        entity: Entity object to check

    Returns:
        True if entity is a disease
    """
    category = getattr(entity, "category", None)
    if category is None:
        return False

    # Category can be a string or list
    categories = [category] if isinstance(category, str) else category

    disease_categories = {"biolink:Disease", "biolink:DiseaseOrPhenotypicFeature"}
    return bool(set(categories) & disease_categories)


@router.get(
    "/{disease_id}",
    response_model=CasePhenotypeMatrixResponse,
    summary="Get case-phenotype matrix for a disease",
    description="""
    Returns a matrix of cases (patients) and their phenotypes for a given disease.

    The matrix includes:
    - **cases**: List of patient cases with the disease
    - **phenotypes**: List of phenotypes observed across all cases
    - **bins**: Body system categories (HistoPheno) with phenotype counts
    - **cells**: Map of case:phenotype pairs to observation details

    Use `direct=true` (default) to get only cases with exactly this disease.
    Use `direct=false` to include cases with descendant diseases (subtypes).
    """,
)
async def get_case_phenotype_matrix(
    disease_id: str = Path(
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
        description="Maximum number of cases",
    ),
) -> CasePhenotypeMatrixResponse:
    """Get case-phenotype matrix for a disease.

    Args:
        disease_id: MONDO disease ID
        direct: If True, only include cases with exactly this disease
        limit: Maximum number of cases allowed

    Returns:
        CasePhenotypeMatrixResponse with complete matrix data

    Raises:
        HTTPException: On validation errors or if limit exceeded
    """
    normalized_id = validate_disease_id(disease_id)

    solr_impl = solr()

    # Check if entity exists and is a disease
    try:
        entity = solr_impl.get_entity(normalized_id, extra=False)
        if entity is None:
            raise HTTPException(
                status_code=404,
                detail=f"Disease {normalized_id} not found",
            )

        if not _is_disease_entity(entity):
            raise HTTPException(
                status_code=400,
                detail=f"{normalized_id} is not a disease ID. Use a MONDO ID.",
            )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=404,
            detail=f"Disease {normalized_id} not found",
        )

    # Get the matrix
    try:
        return solr_impl.get_case_phenotype_matrix(
            disease_id=normalized_id,
            direct_only=direct,
            limit=limit,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
