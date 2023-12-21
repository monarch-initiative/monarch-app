from fastapi import APIRouter, Path  # , Depends, HTTPException, Query

from monarch_py.api.additional_models import TextAnnotationRequest
from monarch_py.api.config import oak, spacyner

router = APIRouter(tags=["text_annotation"], responses={404: {"description": "Not Found"}})


#@router.get("/annotate/{content}", include_in_schema=False)
@router.get("/annotate/{content}")
def _annotate(content: str = Path(title="The text content to annotate")):
    print(f"\n\nRunning oak annotate (GET):\n{content}\n")
    return spacyner().annotate_text(content)


#@router.post("/annotate", include_in_schema=False)
@router.post("/annotate")
def _post_annotate(request: TextAnnotationRequest):
    print(f"\n\nRunning oak annotate (POST):\n{request.content}\n")
    # print(request.content.split("\n"))
    return spacyner().annotate_text(request.content)
