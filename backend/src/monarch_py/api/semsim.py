from fastapi import APIRouter
from monarch_py.api.config import oak

router = APIRouter(tags=["semsim"], responses={404: {"description": "Not Found"}})


@router.get("/compare/{subjects}/{objects}")
async def _compare(
    subjects: str = "",
    objects: str = "",
):
    """Get pairwise similarity between two sets of terms

    Args:
        subjects (str, optional): List of subjects for comparison. Defaults to "".
        objects (str, optional): List of objects for comparison. Defaults to "".

    Returns:
        TermSetPairwiseSimilarity: Pairwise similarity between subjects and objects
    """
    print(f"subjects: {subjects.split(',')}")
    print(f"objects: {objects.split(',')}")
    print(type(subjects.split(",")), type(objects.split(",")))
    results = oak.compare(
        subjects=subjects.split(","),
        objects=objects.split(","),
    )
    return results
