from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from monarch_py.api.additional_models import PaginationParams
from monarch_py.api.config import oak
from monarch_py.datamodels.model import AssociationTableResults, Node
from monarch_py.api.utils import get_text_annotations

router = APIRouter(tags=["text_annotation"], responses={404: {"description": "Not Found"}})


@router.get("/annotate")
def _annotate(
        content: str = Query(title="The text content to annotate")
):
    response = get_text_annotations.annotate_text(content)
    return response
