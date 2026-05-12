from fastapi import APIRouter, Query, Response
from typing import List

from monarch_py.api.additional_models import TextAnnotationRequest
from monarch_py.api.config import solr, spacyner
from monarch_py.datamodels.model import Entity, TextAnnotationResult

router = APIRouter(tags=["text_annotation"], responses={404: {"description": "Not Found"}})


@router.get("/annotate")
def _annotate(text: str = Query(default="", title="The text content to annotate")) -> str:
    return Response(content=spacyner().annotate_text(text), media_type="text/html")


@router.post("/annotate")
def _post_annotate(request: TextAnnotationRequest) -> str:
    return _annotate(request.content)


@router.get("/annotate/entities")
def _entities(text: str = Query(default="", title="")) -> List[TextAnnotationResult]:
    return spacyner().get_annotated_entities(text)


@router.post("/annotate/entities")
def _post_entities(request: TextAnnotationRequest) -> List[TextAnnotationResult]:
    return _entities(request.content)


@router.get("/ground")
def _ground(text: str = Query(default="", title="The text to ground to an entity")) -> List[Entity]:
    return solr().ground_entity(text)


@router.post("/ground")
def _post_ground(request: TextAnnotationRequest) -> List[Entity]:
    return _ground(request.content)
