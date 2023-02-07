from fastapi import APIRouter, Depends
from monarch_py.implementations.solr.solr_implementation import SolrImplementation

from monarch_api.additional_models import PaginationParams
from monarch_api.model import AssociationResults

router = APIRouter(
    prefix="/api/association",
    tags=["association"],
    responses={404: {"description": "Not Found"}},
)


@router.get("/all")
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
    si = SolrImplementation()
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


@router.get("/to/{subject}")
async def _get_association_to(
    subject: str, pagination: PaginationParams = Depends()
) -> AssociationResults:
    """Retrieves all associations to an entity as the subject

    Args:
        subject (str): _description_
        pagination (PaginationParams, optional): _description_. Defaults to Depends().

    Returns:
        AssociationResults: _description_
    """
    si = SolrImplementation()
    response = si.get_associations(
        subject=subject, offset=pagination.offset, limit=pagination.limit
    )

    return response


@router.get("/from/{object}")
async def _get_association_from(object: str, pagination: PaginationParams = Depends()):
    """Retrieves all associations from an entity as the object

    Args:
        object (str): _description_
        pagination (PaginationParams, optional): _description_. Defaults to Depends().

    Returns:
        _type_: _description_
    """
    si = SolrImplementation()
    response = si.get_associations(
        object=object, offset=pagination.offset, limit=pagination.limit
    )

    return response


@router.get("/between/{subject}/{object}")
async def _get_association_between(
    subject: str, object: str, pagination: PaginationParams = Depends()
) -> AssociationResults:
    """Retrieves all associations from an object to a subject

    Args:
        subject (str): _description_
        object (str): _description_
        pagination (PaginationParams, optional): _description_. Defaults to Depends().

    Returns:
        AssociationResults: _description_
    """
    si = SolrImplementation()
    response = si.get_associations(
        subject=subject, object=object, offset=pagination.offset, limit=pagination.limit
    )

    return response
