from typing import Union

from fastapi import APIRouter, HTTPException, Path, Query, Response

from monarch_py.api.config import solr
from monarch_py.api.additional_models import OutputFormat
from monarch_py.datamodels.model import HistoPheno
from monarch_py.utils.format_utils import to_tsv

router = APIRouter(
    tags=["histopheno"],
    responses={404: {"description": "Not Found"}},
)


@router.get("/{id}")
async def _get_histopheno(
    id: str = Path(
        title="ID of the entity to get histopheno data for",
        examples=["MONDO:0019391"],
    ),
    format: OutputFormat = Query(
        default=OutputFormat.json,
        title="Output format for the response",
        examples=["json", "tsv"],
    ),
) -> Union[HistoPheno, str]:
    """Retrieves the entity with the specified id"""
    response = solr().get_histopheno(id)
    if response is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    if format == OutputFormat.json:
        return response
    elif format == OutputFormat.tsv:
        tsv = ""
        for row in to_tsv(response, print_output=False):
            tsv += row
        return Response(content=tsv, media_type="text/tab-separated-values")
