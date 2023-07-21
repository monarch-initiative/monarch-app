from fastapi import APIRouter, Depends

from oaklib.cli import _shorthand_to_pred_curie

from monarch_py.api.additional_models import PaginationParams
from monarch_py.api.utils.get_similarity import compare_termsets

router = APIRouter(
    tags=["semsim"], 
    responses={404: {"description": "Not Found"}}
)


@router.get("/compare/{subjects}/{objects}")
async def _compare(
    subjects: str = "",
    objects: str = "",
    predicates: str = "",
    pagination: PaginationParams = Depends(),
):
    """Get pairwise similarity between two sets of terms

    Args:
        subjects (str, optional): List of subjects for comparison. Defaults to "".
        objects (str, optional): List of objects for comparison. Defaults to "".
        predicates (str, optional): List of predicates for comparison. Defaults to "".
        pagination (PaginationParams, optional): Pagination parameters. Defaults to Depends().

    Returns:
        TermSetPairwiseSimilarity: Pairwise similarity between subjects and objects
    """

    for sublist in [subjects, objects, predicates]:
        sublist = sublist.split(",")
    predicates = [_shorthand_to_pred_curie(p) for p in predicates]

    results = compare_termsets(
        subjects=subjects,
        objects=objects,
        predicates=predicates,
        offset=pagination.offset,
        limit=pagination.limit,
    )
    return results
