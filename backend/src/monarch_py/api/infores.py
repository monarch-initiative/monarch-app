from typing import Union, List

from fastapi import APIRouter, HTTPException, Path, Query, Response

from monarch_py.api.config import solr
from monarch_py.api.additional_models import OutputFormat
from monarch_py.datamodels.model import InformationResource

router = APIRouter(tags=["infores"], responses={404: {"description": "Not Found"}})


@router.get("/")
async def _get_infores_catalog(
    format: OutputFormat = Query(
        default=OutputFormat.json,
        title="Output format for the response",
        examples=["json", "tsv"],
    ),
) -> Union[List[InformationResource], str]:
    """Retrieves all information resources from the catalog

    <b>Returns:</b> <br>
        List[InformationResource]: Complete collection of information resources
    """
    response = solr().get_infores_catalog()
    if format == OutputFormat.json:
        return response
    elif format == OutputFormat.tsv:
        if not response:
            return Response(content="", media_type="text/tab-separated-values")
        
        # Create TSV from pydantic models
        headers = list(response[0].model_dump().keys()) if response else []
        tsv_lines = ["\t".join(headers)]
        
        for item in response:
            row = []
            for header in headers:
                value = getattr(item, header, "")
                if isinstance(value, list):
                    value = ";".join(str(v) for v in value) if value else ""
                row.append(str(value) if value is not None else "")
            tsv_lines.append("\t".join(row))
        
        tsv_content = "\n".join(tsv_lines)
        return Response(content=tsv_content, media_type="text/tab-separated-values")


@router.get("/{id}")
async def _get_entity(
    id: str = Path(
        title="ID of the information resource to retrieve",
        examples=["infores:zfin"],
    ),
    format: OutputFormat = Query(
        default=OutputFormat.json,
        title="Output format for the response",
        examples=["json", "tsv"],
    ),
) -> Union[InformationResource, str]:
    """Retrieves the information resource with the specified id

    <b>Args:</b> <br>
        id (str): ID for the entity to retrieve, ex: infores:zfin

    <b>Raises:</b> <br>
        HTTPException: 404 if the entity is not found

    <b>Returns:</b> <br>
        InformationResource: Information resource details for the specified id
    """
    response = solr().get_infores(id)
    if response is None:
        raise HTTPException(status_code=404, detail="Information resource not found")
    if format == OutputFormat.json:
        return response
    elif format == OutputFormat.tsv:
        # Create TSV from pydantic model
        headers = list(response.model_dump().keys())
        tsv_lines = ["\t".join(headers)]
        
        row = []
        for header in headers:
            value = getattr(response, header, "")
            if isinstance(value, list):
                value = ";".join(str(v) for v in value) if value else ""
            row.append(str(value) if value is not None else "")
        tsv_lines.append("\t".join(row))
        
        tsv_content = "\n".join(tsv_lines)
        return Response(content=tsv_content, media_type="text/tab-separated-values")
