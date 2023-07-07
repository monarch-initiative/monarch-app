from fastapi import APIRouter, Depends
from monarch_py.api.additional_models import PaginationParams
from monarch_py.api.utils.get_similarity import *
from oaklib.cli import _shorthand_to_pred_curie

router = APIRouter(prefix="/api/semsim", tags=["semsim"], responses={404: {"description": "Not Found"}})


@router.get("/semsim/{subjlist}/{objlist}")
async def _get_termlist_similarity(
    pagination: PaginationParams = Depends(),
    subjlist: str = "",
    objlist: str = "",
    predicates: str = "",
):
    """_summary_

    Args:
        pagination (PaginationParams, optional): _description_. Defaults to Depends().
        subjlist (str, optional): _description_. Defaults to "".
        objlist (str, optional): _description_. Defaults to "".
        predicates (str, optional): _description_. Defaults to "".

    Returns:
        _type_: _description_
    """

    # Process string values to lists
    for list_type in [subjlist, objlist, predicates]:
        if "," in list_type:
            list_type = list_type.split(",")
    predicates = [_shorthand_to_pred_curie(p) for p in predicates]

    results = termlist_similarity(
        subjlist=subjlist,
        objlist=objlist,
        predicates=predicates,
        offset=pagination.offset,
        limit=pagination.limit,
    )
    return results
