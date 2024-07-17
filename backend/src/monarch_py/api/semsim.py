from fastapi import APIRouter, Path, Query

from monarch_py.api.additional_models import (
    SemsimCompareRequest,
    SemsimMetric,
    SemsimSearchRequest,
    SemsimSearchGroup,
    SemsimMultiCompareRequest,
    SemsimDirectionality,
)
from monarch_py.api.config import semsimian, solr
from monarch_py.api.utils.similarity_utils import parse_similarity_prefix
from monarch_py.datamodels.category_enums import AssociationPredicate, EntityCategory
from monarch_py.datamodels.model import SearchResults

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
        subjects: {subjects.split(',')}
        objects: {objects.split(',')}
        metric: {metric}
    """
    )
    results = semsimian().compare(
        subjects=subjects.split(","),
        objects=objects.split(","),
        metric=metric,
    )
    return results


@router.post("/compare")
def _post_compare(request: SemsimCompareRequest):
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
    return semsimian().compare(subjects=request.subjects, objects=request.objects, metric=request.metric)


# add a multicompare post endpoint
@router.post("/multicompare")
def _post_multicompare(request: SemsimMultiCompareRequest):
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
    return semsimian().multi_compare(request)


@router.get("/search/{termset}/{group}")
def _search(
    termset: str = Path(..., title="Termset to search"),
    group: SemsimSearchGroup = Path(..., title="Group of entities to search within (e.g. Human Genes)"),
    metric: SemsimMetric = Query(SemsimMetric.ANCESTOR_INFORMATION_CONTENT, title="Similarity metric to use"),
    directionality: SemsimDirectionality = Query(
        SemsimDirectionality.BIDIRECTIONAL, title="Directionality of the search"
    ),
    limit: int = Query(default=10, ge=1, le=50),
):
    """Search for terms in a termset

    <b>Args:</b> <br>
        termset (str): Comma separated list of term IDs to find matches for. <br>
        group (str): Group of entities to search within (e.g. Human Genes) <br>
        metric: (str, optional): Similarity metric to use. Defaults to "ancestor_information_content". <br>
        limit (int, optional): Limit the number of results. Defaults to 10.

    <b>Returns:</b> <br>
        List[str]: List of matching terms
    """
    terms = [term.strip() for term in termset.split(",")]
    results = semsimian().search(
        termset=terms, prefix=parse_similarity_prefix(group), metric=metric, directionality=directionality, limit=limit
    )
    return results


@router.post("/search")
def _post_search(request: SemsimSearchRequest):
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
    return semsimian().search(
        termset=request.termset,
        prefix=parse_similarity_prefix(request.group.value),
        metric=request.metric,
        limit=request.limit,
    )
