from fastapi import APIRouter, HTTPException
from monarch_py.implementations.solr.solr_implementation import SolrImplementation
from monarch_api.model import Node, AssociationCount

router = APIRouter(
    prefix="/api/entity", tags=["entity"], responses={404: {"description": "Not Found"}}
)


@router.get("/{id}")
async def _get_entity(
    id,
    get_association_counts: bool = False,
) -> Node:
    solr = SolrImplementation()
    response = solr.get_entity(id)

    # return fastapi 404 not found if node is None
    if response is None:
        raise HTTPException(status_code=404, detail="Entity not found")

    # This is an odd consequence of Node inheriting from monarch-py:Entity rather than including it within
    node = Node(**response.__dict__)

    if "biolink:Disease" in node.category:
        mode_of_inheritance_associations = solr.get_associations(subject=id, predicate="biolink:has_mode_of_inheritance", offset=0)
        if mode_of_inheritance_associations is not None and len(mode_of_inheritance_associations.associations) == 1:
            node.inheritance = mode_of_inheritance_associations.associations[0]


    # todo: move association_counts query to it's own separate request
    # need a monarch-py facet api
    # for label in result["association_counts"]:
    #     association_count = AssociationCount(
    #         id=label, counts=result["association_counts"][label]
    #     )
    #     node.association_counts.append(association_count)

    return node
