from fastapi import APIRouter
from monarch_py.implementations.solr.solr_implentation import SolrImplementation

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
):
    solr = SolrImplementation()
    results = solr.get_entity(id, get_association_counts=get_association_counts)
    return results
