from fastapi import APIRouter, Path, Request # , Depends, HTTPException, Query
# from monarch_py.api.utils import get_text_annotations
from monarch_py.api.config import oak
from monarch_py.api.additional_models import TextAnnotationRequest

router = APIRouter(tags=["text_annotation"], responses={404: {"description": "Not Found"}})


@router.get("/annotate/{content}")
def _annotate(
        content: str = Path(title="The text content to annotate")
):
    return oak().annotate_text(content)


@router.post("/annotate")
def _post_annotate(request: TextAnnotationRequest):
    return oak().annotate_text(request.content)
