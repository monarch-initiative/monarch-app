from fastapi import APIRouter
from monarch_py.implementations.solr.solr_implentation import SolrImplementation
from monarch_api.model import Node, AssociationCount

router = APIRouter(
    prefix="/api/entity",
    tags=["entity"],
    responses={
        404: {"description": "Not Found"}
    }
)


@router.get("/{id}")
async def _get_entity(
        id,
        get_association_counts: bool = False,
) -> Node:
    solr = SolrImplementation()
    result = solr.get_entity(id, get_association_counts=get_association_counts)

    # todo: is there a nice way to get pydantic to map these? (yes, aliases)
    node = Node(
        id=result["id"],
        label=result["name"],
        category=result["category"][0]
    )

    # todo: move association_counts query to it's own separate request
    for label in result["association_counts"]:
        association_count = AssociationCount(id=label, counts=result["association_counts"][label])
        node.association_counts.append(association_count)

    return node
