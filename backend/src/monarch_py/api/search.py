from typing import List, Union

from fastapi import APIRouter, Depends, Query, Response

from monarch_py.api.additional_models import (
    ALL_FACET_VALUES,
    ALL_SEARCH_FACET_FIELDS,
    DEFAULT_SEARCH_FACET_FIELDS,
    OutputFormat,
    PaginationParams,
    SearchMatchType,
)
from monarch_py.datamodels.search_scopes import SearchScope
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
    in_taxon: Union[List[str], None] = Query(
        default=None,
        title="Filter by taxon CURIE",
        examples=["NCBITaxon:9606"],
    ),
    in_taxon_label: Union[List[str], None] = Query(default=None),
    namespace: Union[List[str], None] = Query(
        default=None,
        title="Restrict to entities whose CURIE uses one of these namespaces",
        examples=["MONDO", "HP"],
    ),
    exclude_namespace: Union[List[str], None] = Query(
        default=None,
        title="Drop entities whose CURIE uses one of these namespaces",
        examples=["MPATH"],
    ),
    subset: Union[List[str], None] = Query(
        default=None,
        title="Restrict to entities in any of these ontology subsets, trailing `*` allowed",
        examples=["rare", "venom_*"],
    ),
    exclude_subset: Union[List[str], None] = Query(
        default=None,
        title="Drop entities in any of these ontology subsets, trailing `*` allowed",
        examples=["venom_*"],
    ),
    scope: Union[SearchScope, None] = Query(
        default=None,
        title="A named filter bundle, e.g. `human_disease`. Fills in category/namespace/subset/"
        "taxon where you did not pass them yourself; anything you do pass wins. The filters it "
        "resolved to come back on the response as `scope`",
    ),
    facets: Union[bool, None] = Query(
        default=None,
        title="`true` returns counts for every field you can filter on — category, taxon, "
        "namespace and subsets — which is how you discover what values those filters accept "
        "(try `?q=*:*&limit=0&facets=true`). `false` returns none. Omit for the category and "
        "taxon counts the web UI uses. Ignored when `match_type=exact`, where Solr's counts "
        "would describe the candidates rather than the matches that survived",
    ),
    match_type: SearchMatchType = Query(
        default=SearchMatchType.relevance,
        title="`relevance` returns the best available hits; `exact` returns only entities the "
        "query names outright, and nothing at all when there is no such entity",
    ),
    pagination: PaginationParams = Depends(),
) -> SearchResults:
    """Search for entities by label, with optional filters

    Args:
        q (str, optional): Query string. Defaults to "*:*".
        category (str, optional): Filter by biolink model category. Defaults to None.
        in_taxon (str, optional): Filter by taxon CURIE. Defaults to None.
        in_taxon_label (str, optional): Filter by taxon label. Defaults to None.
        namespace (str, optional): Restrict to these CURIE namespaces. Defaults to None.
        exclude_namespace (str, optional): Drop these CURIE namespaces. Defaults to None.
        subset (str, optional): Restrict to entities in these ontology subsets. Defaults to None.
        exclude_subset (str, optional): Drop entities in these ontology subsets. Defaults to None.
        scope (SearchScope, optional): A named filter bundle. Supplies category, namespace, subset,
            exclude_subset and in_taxon where they were not passed explicitly; an explicit value
            wins for that axis. The resolved filters are echoed on the response. Defaults to None.
        facets (bool, optional): `True` facets every filterable field with no cap on values,
            which is how a caller discovers what `namespace` and `subsets` accept. `False`
            disables faceting. Omitted keeps the historical category + in_taxon_label counts.
            Ignored under `match_type=exact`. Defaults to None.
        match_type (SearchMatchType, optional): `relevance` (default) or `exact`. In `exact` mode
            a result is returned only when `q` equals the entity's name or one of its exact
            synonyms as a whole string, case-insensitively; otherwise the result set is empty.
            Items carry `matched_field` and `match_type` so callers can apply their own precision
            policy. Defaults to `relevance`.
        offset (int, optional): Offset for pagination. Defaults to 0.
        limit (int, optional): Limit results. Defaults to 20.

    Returns:
        EntityResults
    """
    if facets is None:
        facet_fields = DEFAULT_SEARCH_FACET_FIELDS
        facet_limit = None
    else:
        facet_fields = ALL_SEARCH_FACET_FIELDS if facets else []
        # Solr caps facet values at 100 by default, which would hand back 100 of the 157
        # subsets and quietly defeat the point of the switch.
        facet_limit = ALL_FACET_VALUES if facets else None
    if category is None:
        category = []
    response = solr().search(
        q=q or "*:*",
        category=category,
        namespace=namespace,
        exclude_namespace=exclude_namespace,
        in_taxon=in_taxon,
        in_taxon_label=in_taxon_label,
        subset=subset,
        exclude_subset=exclude_subset,
        scope=scope,
        facet_fields=facet_fields,
        facet_limit=facet_limit,
        offset=pagination.offset,
        limit=pagination.limit,
        highlighting=True,
        exact=match_type == SearchMatchType.exact,
    )

    return response


@router.get("/autocomplete")
async def autocomplete(
    q: str = Query(
        default="*:*",
        title="Query string to autocomplete against",
        examples=["fanc", "ehler"],
    ),
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
