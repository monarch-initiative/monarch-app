from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from monarch_py.api.additional_models import PaginationParams
from monarch_py.api.config import solr
from monarch_py.datamodels.model import AssociationTableResults, Node

router = APIRouter(tags=["entity"], responses={404: {"description": "Not Found"}})


@router.get("/{id}")
async def _get_entity(
    id: str = Path(
        title="ID of the entity to retrieve",
        examples=["MONDO:0019391"],
    )
) -> Node:
    """Retrieves the entity with the specified id

    Args:
        id (str): ID for the entity to retrieve, ex: MONDO:0019391

    Raises:
        HTTPException: 404 if the entity is not found

    Returns:
        Node: Entity details for the specified id
    """
    response = solr().get_entity(id, extra=True)
    if response is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    return Node(**response.__dict__)  # This is an odd consequence of how Node extends Entity


@router.get("/{id}/{category}")
def _association_table(
    id: str = Path(
        title="ID of the entity to retrieve association table data for",
        examples=["MONDO:0019391"],
    ),
    category: str = Path(
        title="Type of association to retrieve association table data for",
        examples=["biolink:DiseaseToPhenotypicFeatureAssociation"],
    ),
    query: str = Query(default=None, title="query string to limit results to a subset", examples=["thumb"]),
    sort: List[str] = Query(
        default=None,
        title="Sort results by a list of field + direction statements",
        examples=["subject_label asc", "predicate asc", "object_label asc"],
    ),
    pagination: PaginationParams = Depends(),
) -> AssociationTableResults:
    """
    Retrieves association table data for a given entity and association type

    Args:
        id (str): ID of the entity to retrieve association table data, ex: MONDO:0019391
        category (str): Category of association to retrieve association table data for, ex: biolink:DiseaseToPhenotypicFeatureAssociation
        Path (str, optional): Path string to limit results to a subset. Defaults to None.
        pagination (PaginationParams, optional): Pagination parameters. Defaults to Depends().

    Returns:
        AssociationResults: Association table data for the specified entity and association type
    """
    response = solr().get_association_table(
        entity=id, category=category, q=query, sort=sort, offset=pagination.offset, limit=pagination.limit
    )
    return response
