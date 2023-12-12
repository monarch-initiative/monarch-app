from fastapi import APIRouter, HTTPException, Path, Query

from monarch_py.api.additional_models import SemsimCompareRequest, SemsimSearchRequest, SemsimSearchCategory
from monarch_py.api.config import semsimian
from monarch_py.api.utils.similarity_utils import parse_similarity_prefix

router = APIRouter(tags=["semsim"], responses={404: {"description": "Not Found"}})


@router.get("/compare/{subjects}/{objects}")
def _compare(
    subjects: str = Path(..., title="List of subjects for comparison"),
    objects: str = Path(..., title="List of objects for comparison"),
):
    """Get pairwise similarity between two sets of terms

    <b>Args:</b> <br>
        subjects (str, optional): List of subjects for comparison. Defaults to "". <br>
        objects (str, optional): List of objects for comparison. Defaults to "". <br>

    <b>Returns:</b> <br>
        TermSetPairwiseSimilarity: Pairwise similarity between subjects and objects
    """
    print(
        f"""
    Running semsim compare:
        subjects: {subjects.split(',')}
        objects: {objects.split(',')}
    """
    )
    results = semsimian().compare(
        subjects=subjects.split(","),
        objects=objects.split(","),
    )
    return results


@router.post("/compare")
def _post_compare(request: SemsimCompareRequest):
    """
        Pairwise similarity between two sets of terms <br>
        <br>
        Example: <br>
    <pre>
    {
      "subjects": ["MP:0010771","MP:0002169","MP:0005391","MP:0005389","MP:0005367"],
      "objects": ["HP:0004325","HP:0000093","MP:0006144"]
    }
    </pre>
    """
    return semsimian().compare(request.subjects, request.objects)


@router.get("/search/{termset}/{prefix}")
def _search(
    termset: str = Path(..., title="Termset to search"),
    prefix: str = Path(..., title="Prefix to search for"),
    limit: int = Query(default=10, ge=0, le=500),
):
    """Search for terms in a termset

    <b>Args:</b> <br>
        termset (str, optional): Termset to search. Defaults to "". <br>
        prefix (str, optional): Prefix to search for. Defaults to "". <br>
        limit (int, optional): Limit the number of results. Defaults to 10.

    <b>Returns:</b> <br>
        List[str]: List of matching terms
    """

    print(
        f"""
    Running semsim search:
        termset: {termset}
        prefix: {prefix}
    """
    )
    
    results = semsimian().search(termset=termset.split(","), prefix=parse_similarity_prefix(prefix), limit=limit)
    return results


@router.post("/search")
def _post_search(request: SemsimSearchRequest):
    """
        Search for terms in a termset <br>
        <br>
        Example: <br>
    <pre>
    {
      "termset": ["HP:0000001", "HP:0000002"],
      "prefix": "ZFIN",
      "limit": 5
    }
    </pre>
    """
    return semsimian().search(request.termset, parse_similarity_prefix(request.prefix), request.limit)
