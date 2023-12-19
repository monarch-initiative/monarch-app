from typing import List, Optional, Union

from fastapi import APIRouter, Depends, Query
from monarch_py.api.additional_models import PaginationParams
from monarch_py.api.config import solr
from monarch_py.datamodels.model import AssociationResults, MultiEntityAssociationResults
from monarch_py.datamodels.category_enums import AssociationCategory, AssociationPredicate

router = APIRouter(
    tags=["association"],
    responses={404: {"description": "Not Found"}},
)


@router.get("")
@router.get("/all", include_in_schema=False)  # We can remove this once the chatgpt plugin & oak aren't using it
async def _get_associations(
    category: Union[List[AssociationCategory], None] = Query(default=None),
    subject: Union[List[str], None] = Query(default=None),
    predicate: Union[List[AssociationPredicate], None] = Query(default=None),
    object: Union[List[str], None] = Query(default=None),
    entity: Union[List[str], None] = Query(default=None),
    direct: Union[bool, None] = Query(default=None),
    pagination: PaginationParams = Depends(),
) -> AssociationResults:
    """Retrieves all associations for a given entity, or between two entities."""
    if category:
        category = [c.value if isinstance(c, AssociationCategory) else c for c in category]
    if predicate:
        predicate = [p.value if isinstance(p, AssociationPredicate) else p for p in predicate]
    response = solr().get_associations(
        category=category,
        predicate=predicate,
        subject=subject,
        object=object,
        entity=entity,
        direct=direct,
        offset=pagination.offset,
        limit=pagination.limit,
    )
    return response


@router.get("/multi")
async def _get_multi_entity_associations(
    entity: Union[List[str], None] = Query(default=None),
    counterpart_category: Union[List[str], None] = Query(default=None),
    pagination: PaginationParams = Depends(),
) -> List[MultiEntityAssociationResults]:
    """Retrieves all associations between each entity and each counterpart category."""
    response = solr().get_multi_entity_associations(
        entity=entity,
        counterpart_category=counterpart_category,
        offset=pagination.offset,
        limit_per_group=pagination.limit,
    )
    return response
