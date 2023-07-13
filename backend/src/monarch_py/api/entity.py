from fastapi import APIRouter, Depends, HTTPException, Query
from monarch_py.api.additional_models import PaginationParams
from monarch_py.api.config import settings
from monarch_py.datamodels.model import AssociationTableResults, Node
from monarch_py.implementations.solr.solr_implementation import SolrImplementation

router = APIRouter(tags=["entity"], responses={404: {"description": "Not Found"}})


@router.get("/{id}")
async def _get_entity(
    id: str = Query(
        ...,
        description="ID for the entity to retrieve, ex: MONDO:0019391",
        example="MONDO:0019391",
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
    solr = SolrImplementation(base_url=settings.solr_url)
    response = solr.get_entity(id, extra=True)

    # return fastapi 404 not found if node is None
    if response is None:
        raise HTTPException(status_code=404, detail="Entity not found")

    # This is an odd consequence of Node inheriting from monarch-py:Entity rather than including it within
    return Node(**response.__dict__)


@router.get("/{id}/{category}")
def _association_table(
    id: str = Query(
        ...,
        example="MONDO:0019391",
        title="ID of the entity to retrieve association table data for",
    ),
    category: str = Query(
        ...,
        example="biolink:DiseaseToPhenotypicFeatureAssociation",
        title="Type of association to retrieve association table data for",
    ),
    query: str = Query(None, example="thumb", title="Query string to limit results to a subset"),
    pagination: PaginationParams = Depends(),
) -> AssociationTableResults:
    """
    Retrieves association table data for a given entity and association type

    Args:
        id (str): ID of the entity to retrieve association table data, ex: MONDO:0019391
        category (str): Category of association to retrieve association table data for, ex: biolink:DiseaseToPhenotypicFeatureAssociation
        query (str, optional): Query string to limit results to a subset. Defaults to None.
    Returns:
        AssociationResults: Association table data for the specified entity and association type
    """
    solr = SolrImplementation(base_url=settings.solr_url)
    response = solr.get_association_table(
        entity=id, category=category, q=query, offset=pagination.offset, limit=pagination.limit
    )

    return response
