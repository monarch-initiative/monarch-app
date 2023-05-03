from fastapi import APIRouter, HTTPException
from monarch_api.config import settings
from monarch_api.model import Node
from monarch_api.utils.entity_utils import get_associated_entity, get_node_hierarchy
from monarch_py.implementations.solr.solr_implementation import SolrImplementation

router = APIRouter(
    tags=["entity"], 
    responses={404: {"description": "Not Found"}}
)


@router.get("/{id}")
async def _get_entity(
    id,
    get_association_counts: bool = False,
) -> Node:
    """Retrieves the entity with the specified id

    Args:
        id (str): ID for the entity to retrieve
        get_association_counts (bool, optional): Whether to retrieve association counts for the entity. Defaults to False.

    Raises:
        HTTPException: _description_

    Returns:
        Node: _description_
    """
    solr = SolrImplementation(base_url=settings.solr_url)
    response = solr.get_entity(id)

    # return fastapi 404 not found if node is None
    if response is None:
        raise HTTPException(status_code=404, detail="Entity not found")

    # This is an odd consequence of Node inheriting from monarch-py:Entity rather than including it within
    node = Node(**response.__dict__)

    if "biolink:Disease" in node.category:
        mode_of_inheritance_associations = solr.get_associations(
            subject=id, predicate="biolink:has_mode_of_inheritance", offset=0
        )
        if (
            mode_of_inheritance_associations is not None
            and len(mode_of_inheritance_associations.items) == 1
        ):
            node.inheritance = get_associated_entity(
                mode_of_inheritance_associations.items[0], node
            )

    node.node_hierarchy = get_node_hierarchy(node, solr)

    node.association_counts = solr.get_association_counts(id)

    return node
