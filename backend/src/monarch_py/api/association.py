from typing import List, Union

from fastapi import APIRouter, Depends, Query, Response

from monarch_py.api.additional_models import OutputFormat, PaginationParams
from monarch_py.api.config import solr
from monarch_py.datamodels.model import AssociationResults, CompactAssociationResults, MultiEntityAssociationResults
from monarch_py.datamodels.category_enums import AssociationCategory, AssociationPredicate, EntityCategory
from monarch_py.utils.format_utils import to_tsv

router = APIRouter(
    tags=["association"],
    responses={404: {"description": "Not Found"}},
)


@router.get("")
@router.get("/all", include_in_schema=False)  # We can remove this once the chatgpt plugin & oak aren't using it
async def _get_associations(
    category: List[AssociationCategory] = Query(default_factory=list),
    subject: Union[List[str], None] = Query(default=None),
    subject_category: List[EntityCategory] = Query(default_factory=list),
    subject_namespace: Union[List[str], None] = Query(default=None),
    subject_taxon: Union[List[str], None] = Query(default=None),
    predicate: List[AssociationPredicate] = Query(default_factory=list),
    object: Union[List[str], None] = Query(default=None),
    object_category: List[EntityCategory] = Query(default_factory=list),
    object_namespace: Union[List[str], None] = Query(default=None),
    object_taxon: Union[List[str], None] = Query(default=None),
    entity: Union[List[str], None] = Query(default=None),
    direct: bool = Query(default=False),
    facet_fields: List[str] = Query(default_factory=list),
    facet_queries: List[str] = Query(default_factory=list),
    filter_queries: List[str] = Query(default_factory=list),
    compact: bool = Query(default=False),
    pagination: PaginationParams = Depends(),
    format: OutputFormat = Query(
        default=OutputFormat.json,
        title="Output format for the response",
        examples=["json", "tsv"],
    ),
) -> Union[AssociationResults, CompactAssociationResults, str]:
    """Retrieves all associations for a given entity, or between two entities."""
    response = solr().get_associations(
        category=category,
        subject=subject,
        predicate=predicate,
        object=object,
        entity=entity,
        subject_category=subject_category,
        subject_namespace=subject_namespace,
        subject_taxon=subject_taxon,
        object_taxon=object_taxon,
        object_category=object_category,
        object_namespace=object_namespace,
        direct=direct,
        compact=compact,
        facet_fields=facet_fields,
        facet_queries=facet_queries,
        filter_queries=filter_queries,
        offset=pagination.offset,
        limit=pagination.limit,
    )
    if format == OutputFormat.json:
        return response
    elif format == OutputFormat.tsv:
        tsv = ""
        for row in to_tsv(response, print_output=False):
            tsv += row
        return Response(content=tsv, media_type="text/tab-separated-values")


@router.get("/multi", include_in_schema=False)
async def _get_multi_entity_associations(
    entity: Union[List[str], None] = Query(default=None),
    counterpart_category: Union[List[str], None] = Query(default=None),
    pagination: PaginationParams = Depends(),
    format: OutputFormat = Query(
        default=OutputFormat.json,
        title="Output format for the response",
        examples=["json", "tsv"],
    ),
) -> List[MultiEntityAssociationResults]:
    """Retrieves all associations between each entity and each counterpart category."""
    response = solr().get_multi_entity_associations(
        entity=entity,
        counterpart_category=counterpart_category,
        offset=pagination.offset,
        limit_per_group=pagination.limit,
    )
    if format == OutputFormat.json:
        return response
    elif format == OutputFormat.tsv:
        tsv = ""
        for row in to_tsv(response, print_output=False):
            tsv += row
        return Response(content=tsv, media_type="text/tab-separated-values")
