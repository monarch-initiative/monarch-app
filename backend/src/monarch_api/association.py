from fastapi import APIRouter, Depends
from monarch_api.additional_models import PaginationParams
from monarch_api.config import settings
from monarch_api.model import AssociationResults
from monarch_py.implementations.solr.solr_implementation import SolrImplementation

router = APIRouter(
    tags=["associations"],
    responses={404: {"description": "Not Found"}},
)


@router.get("/")
@router.get("/all", include_in_schema=False) # Hang on to singular association/all endpoint for now, but hide it
async def _get_all_associations(
    pagination: PaginationParams = Depends(),
    category: str = None,
    predicate: str = None,
    subject: str = None,
    object: str = None,
    entity: str = None,  # return nodes where entity is subject or object
    between: str = None,  # strip by comma and check associations in both directions
) -> AssociationResults:
    """Retrieves all associations for a given entity, or between two entities

    Args:
        pagination (PaginationParams, optional): _description_. Defaults to Depends().
        category (str, optional): _description_. Defaults to None.
        predicate (str, optional): _description_. Defaults to None.
        subject (str, optional): _description_. Defaults to None.
        object (str, optional): _description_. Defaults to None.
        entity (str, optional): _description_. Defaults to None.

    Returns:
        AssociationResults: _description_
    """
    si = SolrImplementation(base_url=settings.solr_url)
    response = si.get_associations(
        category=category,
        predicate=predicate,
        subject=subject,
        object=object,
        entity=entity,
        between=between,
        offset=pagination.offset,
        limit=pagination.limit,
    )

    return response

