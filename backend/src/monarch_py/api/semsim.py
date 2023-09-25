from typing import List

from fastapi import APIRouter, Path
from monarch_py.api.config import oak

router = APIRouter(tags=["semsim"], responses={404: {"description": "Not Found"}})


@router.get("/compare/{subjects}/{objects}")
def _compare(
    subjects: str = Path(title="List of subjects for comparison"),
    objects: str = Path(title="List of objects for comparison"),
):
    """Get pairwise similarity between two sets of terms

    Args:
        subjects (str, optional): List of subjects for comparison. Defaults to "".
        objects (str, optional): List of objects for comparison. Defaults to "".

    Returns:
        TermSetPairwiseSimilarity: Pairwise similarity between subjects and objects
    """
    print(
        f"""
    Running semsim compare:
        subjects: {subjects.split(',')}
        objects: {objects.split(',')}
    """
    )
    results = oak().compare(
        subjects=subjects.split(","),
        objects=objects.split(","),
    )
    return results


@router.post("/compare")
def _post_compare(
    subjects: List[str] = None,
    objects: List[str] = None,
):
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
    return oak().compare(subjects, objects)
