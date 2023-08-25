import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from monarch_py.api.additional_models import PaginationParams
from monarch_py.api.config import solr
from monarch_py.datamodels.model import AssociationTableResults, Node, TermSetPairwiseSimilarity


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
    response = solr().get_entity(id, extra=True)
    if response is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    return Node(**response.__dict__)  # This is an odd consequence of how Node extends Entity


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
    sort: List[str] = Query(
        None,
        example=["subject_label asc", "predicate asc", "object_label asc"],
        title="Sort results by a list of field + direction statements",
    ),
    pagination: PaginationParams = Depends(),
) -> AssociationTableResults:
    """
    Retrieves association table data for a given entity and association type

    Args:
        id (str): ID of the entity to retrieve association table data, ex: MONDO:0019391
        category (str): Category of association to retrieve association table data for, ex: biolink:DiseaseToPhenotypicFeatureAssociation
        query (str, optional): Query string to limit results to a subset. Defaults to None.
        pagination (PaginationParams, optional): Pagination parameters. Defaults to Depends().

    Returns:
        AssociationResults: Association table data for the specified entity and association type
    """
    response = solr().get_association_table(
        entity=id, category=category, q=query, sort=sort, offset=pagination.offset, limit=pagination.limit
    )
    return response

@router.get("/{subject}/compare/{object}")
def _entity_compare(
        subject: str = Query(
        ...,
        description="ID for the entity to retrieve, ex: MONDO:0019391",
        example="MONDO:0019391",
    ),
    object: str = Query(
        ...,
        description="ID for the entity to compare against, ex: MONDO:0007915",
        example="MONDO:0007915",
    ),
) -> TermSetPairwiseSimilarity:
    """Retrieves the entity with the specified id

    Args:
        subject (str): ID for the entity to retrieve, ex: MONDO:0019391
        object (str): ID for the entity to compare against, ex: MONDO:0007915

    Raises:
        HTTPException: 404 if the entities are not found or if no phenotypes are found

    Returns:
        TermPairwiseSimilarity: Pairwise similarity between the phenotypes of subject and subject entities
    """
    categories = ["biolink:DiseaseToPhenotypicFeatureAssociation", "biolink:GeneToPhenotypicFeatureAssociation"]
    subject = solr().get_entity(id=object, extra=False)
    if subject is None:
        raise HTTPException(status_code=404, detail=f"{subject} not found")
    subject_associations = solr().get_associations(subject=subject, category=categories, limit=10000).items
    if subject_associations is None:
        raise HTTPException(status_code=404, detail=f"No phenotypes found for ${subject}")
    subject_phenotypes = [association.object for association in subject_associations]

    object = solr().get_entity(id=object, extra=False)
    if object is None:
        raise HTTPException(status_code=404, detail=f"{object} not found")
    object_associations = solr().get_associations(subject=object, category=categories, limit=10000).items
    if object_associations is None:
        raise HTTPException(status_code=404, detail=f"No phenotypes found for ${object}")
    object_phenotypes = [association.object for association in object_associations]

    logging.debug(f"Comparing {subject} ({len(subject_phenotypes)} phenotypes) to {object} ({len(object_phenotypes)} phenotypes)")

    return oak().compare(subjects=subject_phenotypes, objects=object_phenotypes)

