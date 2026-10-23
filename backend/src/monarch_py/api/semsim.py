from enum import Enum
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Path, Query

from monarch_py.api.additional_models import (
    SemsimCompareRequest,
    SemsimMetric,
    SemsimSearchRequest,
    SemsimSearchGroup,
    SemsimMultiCompareRequest,
    SemsimDirectionality,
    SemsimSearchMode,
    SemsimInformationContent,
    SemsimTieBreak,
    DEFAULT_FREQUENCY,
    DEFAULT_FREQUENCY_TITLE,
    TIE_BREAK_TITLE,
    INFORMATION_CONTENT_TITLE,
    COMPARE_GROUP_TITLE,
)
from monarch_py.api.config import resolve_engine, semsim_service, solr
from monarch_py.api.utils.similarity_utils import parse_similarity_prefix
from monarch_py.datamodels.category_enums import AssociationPredicate, EntityCategory
from monarch_py.datamodels.model import SearchResults, SemsimSearchResult, SemsimSearchSettings
from monarch_py.service.ducksim import AnnotationICUnavailable
from monarch_py.service.semsim_results import annotate_search_results

# Hidden A/B-testing param: ?engine=ducksim|semsimian overrides the default similarity backend.
EngineParam = Query(default=None, include_in_schema=False, title="Similarity backend override")

# Search settings only ducksim implements, with the value that reproduces today's behaviour.
# A request that sets any of them to something else is served by ducksim, whatever the backend.
DUCKSIM_SEARCH_SETTINGS = {
    "search_mode": SemsimSearchMode.HYBRID,
    "information_content": SemsimInformationContent.ONTOLOGY,
    "tie_break": SemsimTieBreak.NONE,
    "default_frequency": DEFAULT_FREQUENCY,
}


def _bad_request_if_unavailable(call):
    """Run a backend call, turning a request the attached KG can't serve into a 400."""
    try:
        return call()
    except AnnotationICUnavailable as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _compare_backend(engine, information_content, group):
    """(service, extra compare kwargs). Ontology IC keeps the configured backend and today's call;
    annotation IC is ducksim-only and needs a group to pick its annotation corpus."""
    if SemsimInformationContent(information_content) == SemsimInformationContent.ONTOLOGY:
        return semsim_service(engine), {}
    if group is None:
        raise HTTPException(
            status_code=400, detail="information_content=annotation needs a group, e.g. group=Human Diseases"
        )
    group_value = group.value if hasattr(group, "value") else group
    return semsim_service("ducksim"), {
        "information_content": SemsimInformationContent.ANNOTATION,
        "group_prefix": parse_similarity_prefix(group_value),
    }


def _run_search(
    *,
    termset: List[str],
    group: str,
    metric: SemsimMetric,
    directionality: SemsimDirectionality,
    limit: int,
    engine: Optional[str],
    **ducksim_settings,
) -> List[SemsimSearchResult]:
    """Run a search on the right backend and attach direction scores and the settings used.

    Ducksim-only settings are passed to the backend only when they differ from their defaults, so
    a request that sets none of them calls either backend exactly as before.
    """
    requested = {name: ducksim_settings.get(name, default) for name, default in DUCKSIM_SEARCH_SETTINGS.items()}
    non_default = {name: value for name, value in requested.items() if value != DUCKSIM_SEARCH_SETTINGS[name]}
    engine_name = "ducksim" if non_default else resolve_engine(engine)
    results = _bad_request_if_unavailable(
        lambda: semsim_service(engine_name).search(
            termset=termset,
            prefix=parse_similarity_prefix(group),
            metric=metric,
            directionality=directionality,
            limit=limit,
            **non_default,
        )
    )
    search_settings = SemsimSearchSettings(
        engine=engine_name,
        metric=str(metric),
        directionality=str(SemsimDirectionality(directionality).value),
        **{name: str(value) if isinstance(value, Enum) else value for name, value in requested.items()},
    )
    return annotate_search_results(results, search_settings)


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
    information_content: SemsimInformationContent = Query(
        SemsimInformationContent.ONTOLOGY, title=INFORMATION_CONTENT_TITLE
    ),
    group: Optional[SemsimSearchGroup] = Query(None, title=COMPARE_GROUP_TITLE),
    engine: Optional[str] = EngineParam,
):
    """Get pairwise similarity between two sets of terms

    <b>Args:</b> <br>
        subjects (str, optional): List of subjects for comparison. Defaults to "". <br>
        objects (str, optional): List of objects for comparison. Defaults to "". <br>
        metric (str, optional): Similarity metric to use. Defaults to "ancestor_information_content". <br>
        information_content (str, optional): "ontology" or "annotation". Defaults to "ontology". <br>
        group (str, optional): The annotation corpus, such as "Human Diseases". Required for annotation IC.

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
    service, extra = _compare_backend(engine, information_content, group)
    return _bad_request_if_unavailable(
        lambda: service.compare(subjects=subjects.split(","), objects=objects.split(","), metric=metric, **extra)
    )


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
    service, extra = _compare_backend(engine, request.information_content, request.group)
    return _bad_request_if_unavailable(
        lambda: service.compare(subjects=request.subjects, objects=request.objects, metric=request.metric, **extra)
    )


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
    service, extra = _compare_backend(engine, request.information_content, request.group)
    extra.pop("information_content", None)  # multi_compare reads it from the request
    return _bad_request_if_unavailable(lambda: service.multi_compare(request, **extra))


@router.get("/search/{termset}/{group}")
def _search(
    termset: str = Path(..., title="Termset to search"),
    group: SemsimSearchGroup = Path(..., title="Group of entities to search within (e.g. Human Genes)"),
    metric: SemsimMetric = Query(SemsimMetric.ANCESTOR_INFORMATION_CONTENT, title="Similarity metric to use"),
    directionality: SemsimDirectionality = Query(
        SemsimDirectionality.BIDIRECTIONAL, title="Directionality of the search"
    ),
    limit: int = Query(default=10, ge=1, le=50),
    search_mode: SemsimSearchMode = Query(
        SemsimSearchMode.HYBRID, title="Score a Jaccard-prefiltered candidate set (hybrid) or every entity (full)"
    ),
    information_content: SemsimInformationContent = Query(
        SemsimInformationContent.ONTOLOGY, title=INFORMATION_CONTENT_TITLE
    ),
    tie_break: SemsimTieBreak = Query(SemsimTieBreak.NONE, title=TIE_BREAK_TITLE),
    default_frequency: float = Query(DEFAULT_FREQUENCY, title=DEFAULT_FREQUENCY_TITLE, ge=0.01, le=1.0),
    engine: Optional[str] = EngineParam,
):
    """Search for terms in a termset

    <b>Args:</b> <br>
        termset (str): Comma separated list of term IDs to find matches for. <br>
        group (str): Group of entities to search within (e.g. Human Genes) <br>
        metric: (str, optional): Similarity metric to use. Defaults to "ancestor_information_content". <br>
        directionality (str, optional): How per-term best matches are averaged. Defaults to "bidirectional". <br>
        limit (int, optional): Limit the number of results. Defaults to 10. <br>
        search_mode (str, optional): "hybrid" or "full". Defaults to "hybrid". "full" is served by the DuckDB backend. <br>
        information_content (str, optional): "ontology" or "annotation". Defaults to "ontology". "annotation" uses the
        searched group's annotations as the corpus and is served by the DuckDB backend. <br>
        tie_break (str, optional): "none" or "frequency". Defaults to "none". "frequency" orders equal scores by
        how frequent the matched phenotypes are in each entity, and is served by the DuckDB backend. <br>
        default_frequency (float, optional): The frequency assumed where an annotation records none. Defaults to 0.5.

    <b>Returns:</b> <br>
        List[SemsimSearchResult]: Ranked entities, each with both direction scores and the settings used
    """
    terms = [term.strip() for term in termset.split(",")]
    return _run_search(
        termset=terms,
        group=group,
        metric=metric,
        directionality=directionality,
        limit=limit,
        engine=engine,
        search_mode=search_mode,
        information_content=information_content,
        tie_break=tie_break,
        default_frequency=default_frequency,
    )


@router.post("/search")
def _post_search(request: SemsimSearchRequest, engine: Optional[str] = EngineParam):
    """
        Search for terms in a termset <br>
        <br>
        Example: <br>
    <pre>
    {
      "termset": ["HP:0002104", "HP:0012378", "HP:0012378", "HP:0012378"],
      "group": "Human Diseases",
      "metric": "ancestor_information_content",
      "limit": 5
    }
    </pre>
    """
    return _run_search(
        termset=request.termset,
        group=request.group.value,
        metric=request.metric,
        directionality=request.directionality,
        limit=request.limit,
        engine=engine,
        search_mode=request.search_mode,
        information_content=request.information_content,
        tie_break=request.tie_break,
        default_frequency=request.default_frequency,
    )
