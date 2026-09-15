from typing import Optional

from fastapi import APIRouter, HTTPException, Path, Query

from monarch_py.api.additional_models import (
    SemsimCompareRequest,
    SemsimMetric,
    SemsimSearchRequest,
    SemsimProfileSearchRequest,
    SemsimSearchGroup,
    SemsimMultiCompareRequest,
    SemsimDirectionality,
    expand_search_group,
)
from monarch_py.api.config import semsim_service, solr
from monarch_py.api.utils.similarity_utils import parse_similarity_prefix
from monarch_py.datamodels.category_enums import AssociationPredicate, EntityCategory
from monarch_py.datamodels.model import SearchResults

# Hidden A/B-testing param: ?engine=ducksim|semsimian overrides the default similarity backend.
EngineParam = Query(default=None, include_in_schema=False, title="Similarity backend override")

router = APIRouter(tags=["semsim"], responses={404: {"description": "Not Found"}})


@router.get("/autocomplete")
def autocomplete(
    q: str = Query(
        default="*:*",
        title="Query string to autocomplete against",
        examples=["fanc", "ehler"],
    ),
) -> SearchResults:
    """
    Autocomplete for semantic similarity lookups, prioritizes entities which have direct phenotype associations.
    Note: This API endpoint is experimental and may evolve or disappear over time.

    Args:
        q (str): Query string to autocomplete against

    Returns:
        SearchResults
    """
    response = solr().autocomplete(
        q=q,
        category=[EntityCategory.DISEASE, EntityCategory.GENE, EntityCategory.PHENOTYPIC_FEATURE],
        prioritized_predicates=[AssociationPredicate.HAS_PHENOTYPE],
    )
    return response


@router.get("/compare/{subjects}/{objects}")
def _compare(
    subjects: str = Path(..., title="List of subjects for comparison"),
    objects: str = Path(..., title="List of objects for comparison"),
    metric: SemsimMetric = Query(SemsimMetric.ANCESTOR_INFORMATION_CONTENT, title="Similarity metric to use"),
    engine: Optional[str] = EngineParam,
):
    """Get pairwise similarity between two sets of terms

    <b>Args:</b> <br>
        subjects (str, optional): List of subjects for comparison. Defaults to "". <br>
        objects (str, optional): List of objects for comparison. Defaults to "". <br>
        metric (str, optional): Similarity metric to use. Defaults to "ancestor_information_content".

    <b>Returns:</b> <br>
        TermSetPairwiseSimilarity: Pairwise similarity between subjects and objects
    """
    print(
        f"""
    Running semsim compare:
        subjects: {subjects.split(",")}
        objects: {objects.split(",")}
        metric: {metric}
    """
    )
    results = semsim_service(engine).compare(
        subjects=subjects.split(","),
        objects=objects.split(","),
        metric=metric,
    )
    return results


@router.post("/compare")
def _post_compare(request: SemsimCompareRequest, engine: Optional[str] = EngineParam):
    """
        Pairwise similarity between two sets of terms <br>
        <br>
        Example: <br>
    <pre>
    {
        "subjects": ["MP:0010771", "MP:0002169"],
        "objects": ["HP:0004325"]
        "metric": "ancestor_information_content"
    }
    </pre>
    """
    return semsim_service(engine).compare(subjects=request.subjects, objects=request.objects, metric=request.metric)


# add a multicompare post endpoint
@router.post("/multicompare")
def _post_multicompare(request: SemsimMultiCompareRequest, engine: Optional[str] = EngineParam):
    """
        Pairwise similarity between two sets of terms <br>
        <br>
        Example: <br>
    <pre>
    {
        "metric": "ancestor_information_content",
        "subjects": ["HP:0002616","HP:0001763","HP:0004944","HP:0010749","HP:0001533","HP:0002020","HP:0012450"],
        "object_sets": [
            {
            "id": "MGI:2441732",
            "label": "Adgrg7",
            "phenotypes": ["MP:0011965","MP:0002834","MP:0003731","MP:0011962","MP:0011960","MP:0008489","MP:0003291","MP:0001262"]
            },
            {
            "id": "MGI:87909",
            "label": "Acta2",
            "phenotypes": ["MP:0002834","MP:0003070","MP:0004022","MP:0004021","MP:0003026","MP:0006264","MP:0000230","MP:0000233","MP:0000272","MP:0009862"]
            }
        ]
    }
    </pre>
    """
    return semsim_service(engine).multi_compare(request)


@router.get("/search/{termset}/{group}")
def _search(
    termset: str = Path(..., title="Termset to search"),
    group: SemsimSearchGroup = Path(..., title="Group of entities to search within (e.g. Human Genes)"),
    metric: SemsimMetric = Query(SemsimMetric.ANCESTOR_INFORMATION_CONTENT, title="Similarity metric to use"),
    directionality: SemsimDirectionality = Query(
        SemsimDirectionality.BIDIRECTIONAL, title="Directionality of the search"
    ),
    limit: int = Query(default=10, ge=1, le=50),
    engine: Optional[str] = EngineParam,
):
    """Search for terms in a termset, within one of the legacy entity groups.

    Superseded by `POST /search`, which takes explicit category/taxon filters and can express
    targets no group can name — notably "all mouse models", which spans the MGI and MMRRC
    prefixes. This route expands the group to those same explicit filters.

    <b>Args:</b> <br>
        termset (str): Comma separated list of term IDs to find matches for. <br>
        group (str): Group of entities to search within (e.g. Human Genes) <br>
        metric: (str, optional): Similarity metric to use. Defaults to "ancestor_information_content". <br>
        limit (int, optional): Limit the number of results. Defaults to 10.

    <b>Returns:</b> <br>
        List[str]: List of matching terms
    """
    terms = [term.strip() for term in termset.split(",")]
    categories, taxa, prefixes = expand_search_group(group)
    results = semsim_service(engine).search(
        termset=terms,
        prefix=parse_similarity_prefix(group),
        metric=metric,
        directionality=directionality,
        limit=limit,
        categories=categories,
        taxa=taxa,
        prefixes=prefixes,
    )
    return results


@router.get("/filters")
def _filters(engine: Optional[str] = EngineParam):
    """The (category, taxon) combinations available to search, with entity counts.

    Explicit filters are only usable if callers can find out what to pass, so this enumerates the
    valid values from the KG itself rather than from a hand-maintained enum that drifts.
    """
    service = semsim_service(engine)
    if not hasattr(service, "engine"):
        return {"detail": "filter discovery requires the ducksim backend"}
    return [
        {"category": cat, "taxon": tax, "taxon_label": lab, "count": n}
        for cat, tax, lab, n in service.engine.categories()
    ]


@router.post("/search")
def _post_search(request: SemsimSearchRequest, engine: Optional[str] = EngineParam):
    """
        Search for entities whose phenotype profile matches a termset. <br>
        <br>
        Every mouse model, across MGI *and* MMRRC — not expressible with the legacy `group`: <br>
    <pre>
    {
      "termset": ["HP:0002104", "HP:0012378"],
      "filter": {"category": ["biolink:Genotype"], "taxon": ["NCBITaxon:10090"]},
      "metric": "phenodigm_score",
      "limit": 5
    }
    </pre>
        Only orderable MMRRC strains: <br>
    <pre>
    {"termset": ["HP:0002104"], "filter": {"category": ["biolink:Genotype"], "prefix": ["MMRRC"]}}
    </pre>
        Legacy form, still supported: <br>
    <pre>
    {"termset": ["HP:0002104"], "group": "Human Diseases", "limit": 5}
    </pre>
        Call <code>GET /semsim/filters</code> for the category/taxon values this KG supports.
    """
    if request.filter is None and request.group is None:
        raise HTTPException(status_code=422, detail="provide either `filter` (preferred) or `group`")
    return semsim_service(engine).search(
        termset=request.termset,
        metric=request.metric,
        directionality=request.directionality,
        limit=request.limit,
        **request.resolved_filter(),
    )


@router.post("/search-by-profile")
def _post_search_by_profile(request: SemsimProfileSearchRequest, engine: Optional[str] = EngineParam):
    """
        Search using an entity's OWN phenotype profile as the query. <br>
        <br>
        Mouse models for a patient (phenopacket Case -> mouse genotypes): <br>
    <pre>
    {
      "entity": "phenopacket.store:PMID_38991538_Individual_1",
      "filter": {"category": ["biolink:Genotype"], "taxon": ["NCBITaxon:10090"]},
      "metric": "phenodigm_score"
    }
    </pre>
        Patients matching a mouse model (mouse genotype -> Cases): <br>
    <pre>
    {"entity": "MMRRC:000415-UCD", "filter": {"category": ["biolink:Case"]}}
    </pre>
        The likely diagnosis for a patient (Case -> diseases): <br>
    <pre>
    {"entity": "phenopacket.store:PMID_38991538_Individual_1", "filter": {"category": ["biolink:Disease"]}}
    </pre>
        Needs the ducksim backend (the entity's profile is read from the KG).
    """
    service = semsim_service(engine)
    if not hasattr(service, "search_by_profile"):
        raise HTTPException(
            status_code=501, detail="search-by-profile requires the ducksim backend (?engine=ducksim)"
        )
    profile, results = service.search_by_profile(
        entity_id=request.entity,
        metric=request.metric,
        directionality=request.directionality,
        limit=request.limit,
        **request.filter.as_kwargs(),
    )
    if not profile:
        raise HTTPException(status_code=404, detail=f"no phenotype profile found for entity {request.entity!r}")
    return {"entity": request.entity, "query_profile": profile, "results": results}
