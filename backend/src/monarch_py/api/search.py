from typing import List, Union

from fastapi import APIRouter, Depends, Query, Response

from monarch_py.api.additional_models import OutputFormat, PaginationParams
from monarch_py.api.config import solr
from monarch_py.datamodels.model import SearchResults, MappingResults
from monarch_py.datamodels.category_enums import EntityCategory, MappingPredicate
from monarch_py.utils.format_utils import to_tsv

router = APIRouter(
    tags=["search"],
    responses={404: {"description": "Not Found"}},
)


@router.get("/search")
async def search(
    q: str = Query(default=None),
    category: Union[List[EntityCategory], None] = Query(default=None),
    in_taxon_label: Union[List[str], None] = Query(default=None),
    pagination: PaginationParams = Depends(),
) -> SearchResults:
    """Search for entities by label, with optional filters

    Args:
        q (str, optional): Query string. Defaults to "*:*".
        category (str, optional): Filter by biolink model category. Defaults to None.
        in_taxon_label (str, optional): Filter by taxon label. Defaults to None.
        offset (int, optional): Offset for pagination. Defaults to 0.
        limit (int, optional): Limit results. Defaults to 20.

    Returns:
        EntityResults
    """
    facet_fields = ["category", "in_taxon_label"]
    if category is None:
        category = []
    response = solr().search(
        q=q or "*:*",
        category=category,
        in_taxon_label=in_taxon_label,
        facet_fields=facet_fields,
        offset=pagination.offset,
        limit=pagination.limit,
        highlighting=True,
    )

    return response


@router.get("/autocomplete")
async def autocomplete(
    q: str = Query(
        default="*:*",
        title="Query string to autocomplete against",
        examples=["fanc", "ehler"],
    )
) -> SearchResults:
    """Autocomplete for entities by label

    Args:
        q (str): Query string to autocomplete against

    Returns:
        SearchResults
    """
    response = solr().autocomplete(q=q)
    return response


@router.get("/mappings", response_model=MappingResults)
async def mappings(
    entity_id: Union[List[str], None] = Query(default=None),
    subject_id: Union[List[str], None] = Query(default=None),
    predicate_id: Union[List[MappingPredicate], None] = Query(default=None),
    object_id: Union[List[str], None] = Query(default=None),
    mapping_justification: Union[List[str], None] = Query(default=None),
    pagination: PaginationParams = Depends(),
    format: OutputFormat = Query(
        default=OutputFormat.json,
        title="Output format for the response",
        examples=["json", "tsv"],
    ),
):
    response = solr().get_mappings(
        entity_id=entity_id,
        subject_id=subject_id,
        predicate_id=predicate_id,
        object_id=object_id,
        mapping_justification=mapping_justification,
        offset=pagination.offset,
        limit=pagination.limit,
    )
    if not response.items:
        return MappingResults(items=[], offset=pagination.offset, limit=pagination.limit, total=0)
    if format == OutputFormat.json:
        return response
    elif format == OutputFormat.tsv:
        tsv = to_tsv(response, print_output=False) or ""
        if tsv:
            return Response(content=tsv, media_type="text/tab-separated-values")
