from fastapi import APIRouter, HTTPException

from monarch_py.api.config import solr
from monarch_py.datamodels.model import HistoPheno

router = APIRouter(
    tags=["histopheno"],
    responses={404: {"description": "Not Found"}},
)


@router.get("/{id}")
async def _get_histopheno(id) -> HistoPheno:
    """Retrieves the entity with the specified id"""
    response = solr().get_histopheno(id)
    if response is None:
        raise HTTPException(status_code=404, detail="Entity not found")

    return response
