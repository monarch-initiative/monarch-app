from fastapi import APIRouter, Depends

from monarch_api.additional_models import PaginationParams

router = APIRouter(
    prefix="/api/association",
    tags=["association"],
    responses={404: {"description": "Not Found"}},
)

d = Depends()


@router.get("/all")
async def _get_all_associations(
    pagination: PaginationParams = d,
    category: str = None,
    predicate: str = None,
    subject: str = None,
    object: str = None,
    entity: str = None,  # return nodes where entity is subject or object
    between: str = None,  # strip by comma and check associations in both directions
):
    pass


@router.get("/to/{subject}")
async def _get_association_to(subject: str, pagination: PaginationParams = d):
    pass


@router.get("/from/{object}")
async def _get_association_from(object: str, pagination: PaginationParams = d):
    pass


@router.get("/between/{subject}/{object}")
async def _get_association_between(
    subject: str, object: str, pagination: PaginationParams = d
):
    pass


async def _get_association_find(subject_category, object_category=None):
    pass
