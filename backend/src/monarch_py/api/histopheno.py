from fastapi import APIRouter, HTTPException
from monarch_py.api.config import settings
from monarch_py.datamodels.model import HistoPheno
from monarch_py.implementations.solr.solr_implementation import SolrImplementation

router = APIRouter(
    # tags=["histopheno"],
    responses={404: {"description": "Not Found"}},
)


@router.get("/{id}")
async def _get_histopheno(id) -> HistoPheno:
    """Retrieves the entity with the specified id"""

    solr = SolrImplementation(base_url=settings.solr_url)
    response = solr.get_histopheno(id)

    # return fastapi 404 not found if node is None
    if response is None:
        raise HTTPException(status_code=404, detail="Entity not found")

    return response
