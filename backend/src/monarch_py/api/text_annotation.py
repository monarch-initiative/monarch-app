from fastapi import APIRouter, Query, Response
from typing import List, Optional, Union

from monarch_py.api.additional_models import TextAnnotationRequest
from monarch_py.api.config import solr, spacyner
from monarch_py.datamodels.category_enums import EntityCategory
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


def _ground_entity(
    text: str,
    prefix: Optional[List[str]] = None,
    category: Optional[List[str]] = None,
) -> List[Entity]:
    """Shared grounding logic for the GET and POST endpoints."""
    if not text.strip():
        return []
    return solr().ground_entity(text, prefix=prefix, category=category)


@router.get("/ground")
def _ground(
    text: str = Query(default="", title="The text to ground to an entity"),
    prefix: Union[List[str], None] = Query(
        default=None,
        title="Restrict results to entities using one of these CURIE prefixes (e.g. MONDO, HP)",
    ),
    category: Union[List[EntityCategory], None] = Query(
        default=None,
        title="Restrict results to entities of one of these biolink categories (e.g. biolink:Disease)",
    ),
) -> List[Entity]:
    return _ground_entity(
        text,
        prefix=prefix,
        category=[c.value for c in category] if category else None,
    )


@router.post("/ground")
def _post_ground(request: TextAnnotationRequest) -> List[Entity]:
    return _ground_entity(request.content, prefix=request.prefix, category=request.category)
