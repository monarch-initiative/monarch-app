from enum import Enum
from typing import List, Optional

from fastapi import Query, Request
from pydantic import BaseModel, Field

from monarch_py.datamodels.category_enums import EntityCategory


class PaginationParams(BaseModel):
    request: Request
    limit: int = Query(default=20, ge=0, le=500)
    offset: int = Query(default=0, ge=0)

    class Config:
        arbitrary_types_allowed = True


class OutputFormat(str, Enum):
    json = "json"
    tsv = "tsv"


class SemsimMetric(str, Enum):
    ANCESTOR_INFORMATION_CONTENT = "ancestor_information_content"
    # COSINE_SIMILARITY = "cosine_similarity"  # Not implemented
    JACCARD_SIMILARITY = "jaccard_similarity"
    PHENODIGM_SCORE = "phenodigm_score"

    def __str__(self):
        return self.value


class SemsimSearchGroup(Enum):
    """Legacy search groups. Superseded by the explicit category/taxon filters below.

    Each group is a CURIE prefix standing in for "entities of some category in some species",
    which works only while the two coincide one-to-one. They do not: mouse models are split
    across the MGI and MMRRC prefixes, so no single group can name them, and MGI alone covers
    mouse genes, genotypes and variants at once. Kept working via `expand_search_group`.
    """

    HGNC = "Human Genes"
    MGI = "Mouse Genes"
    RGD = "Rat Genes"
    ZFIN = "Zebrafish Genes"
    WB = "C. Elegans Genes"
    MONDO = "Human Diseases"


# Explicit (category, taxa, prefixes) each legacy group expands to. This is what preserves the
# old meaning now that the association pool spans every phenotype-bearing entity: before, a
# gene-and-disease-only pool made prefix="MGI" mean "mouse genes" by accident. It no longer does,
# so the category has to be stated.
_SEARCH_GROUP_FILTERS = {
    "HGNC": (["biolink:Gene"], ["NCBITaxon:9606"], ["HGNC"]),
    "MGI": (["biolink:Gene"], ["NCBITaxon:10090"], ["MGI"]),
    "RGD": (["biolink:Gene"], ["NCBITaxon:10116"], ["RGD"]),
    "ZFIN": (["biolink:Gene"], ["NCBITaxon:7955"], ["ZFIN"]),
    "WB": (["biolink:Gene"], ["NCBITaxon:6239"], ["WB"]),
    "MONDO": (["biolink:Disease"], None, ["MONDO"]),
}


def expand_search_group(group):
    """Legacy group -> (categories, taxa, prefixes). Accepts the enum, its name ("MGI") or its
    value ("Mouse Genes"). Returns (None, None, None) for an unknown group so the caller can
    decide whether that is an error."""
    if group is None:
        return None, None, None
    name = group.name if isinstance(group, SemsimSearchGroup) else str(group)
    if name not in _SEARCH_GROUP_FILTERS:
        try:
            name = SemsimSearchGroup(name).name
        except ValueError:
            return None, None, None
    return _SEARCH_GROUP_FILTERS[name]


class SemsimSearchFilter(BaseModel):
    """Explicit replacement for `group`: say what kind of thing, in what species, from where.

    All three fields are optional and AND together, so "every mouse genotype regardless of
    source" is `category=[Genotype], taxon=["NCBITaxon:10090"]` — the query the prefix-based API
    could not express. `taxon` takes an NCBITaxon CURIE or a species label ("Mus musculus").
    """

    category: Optional[List[EntityCategory]] = Field(
        default=None, title="Biolink categories to search within (e.g. biolink:Genotype)"
    )
    taxon: Optional[List[str]] = Field(
        default=None, title="NCBITaxon CURIEs or species labels (e.g. NCBITaxon:10090)"
    )
    prefix: Optional[List[str]] = Field(
        default=None, title="Restrict to these CURIE prefixes (e.g. MMRRC) — a source filter, not a category"
    )

    def as_kwargs(self) -> dict:
        """Engine kwargs for Ducksim.search / full_search / hybrid_search."""
        # `.value`, not `str()`: EntityCategory is a plain Enum, so str() gives
        # "EntityCategory.GENOTYPE" rather than the "biolink:Genotype" CURIE the KG stores. That
        # would match no rows and return an empty result that looks like a real answer.
        return {
            "categories": [c.value for c in self.category] if self.category else None,
            "taxa": self.taxon or None,
            "prefixes": self.prefix or None,
        }


class SemsimDirectionality(str, Enum):
    BIDIRECTIONAL = "bidirectional"
    SUBJECT_TO_OBJECT = "subject_to_object"
    OBJECT_TO_SUBJECT = "object_to_subject"


class SemsimCompareRequest(BaseModel):
    subjects: List[str] = Field(..., title="List of subjects for comparison")
    objects: List[str] = Field(..., title="List of objects for comparison")
    metric: SemsimMetric = Field(SemsimMetric.ANCESTOR_INFORMATION_CONTENT, title="Similarity metric to use")


class SemsimMultiCompareObject(BaseModel):
    id: Optional[str] = Field(None, title="ID of the object set")
    label: str = Field(..., title="Label of the object set")
    phenotypes: List[str] = Field(..., title="List of object for comparison")


class SemsimMultiCompareRequest(BaseModel):
    subjects: List[str] = Field(..., title="List of subjects for comparison")
    object_sets: List[SemsimMultiCompareObject] = Field(..., title="List of object sets for comparison")
    metric: SemsimMetric = Field(SemsimMetric.ANCESTOR_INFORMATION_CONTENT, title="Similarity metric to use")


class SemsimSearchRequest(BaseModel):
    termset: List[str] = Field(..., title="Termset to search")
    group: Optional[SemsimSearchGroup] = Field(
        None, title="DEPRECATED legacy entity group; prefer the explicit `filter`"
    )
    filter: Optional[SemsimSearchFilter] = Field(
        None, title="Explicit category / taxon / prefix filter (supersedes `group`)"
    )
    metric: SemsimMetric = Field(SemsimMetric.ANCESTOR_INFORMATION_CONTENT, title="Similarity metric to use")
    directionality: SemsimDirectionality = Field(
        SemsimDirectionality.BIDIRECTIONAL, title="Directionality of the search"
    )
    limit: Optional[int] = Field(10, title="Limit the number of results", ge=1, le=50)

    def resolved_filter(self) -> dict:
        """Engine kwargs, preferring the explicit filter and falling back to the legacy group.

        `group` stays valid so existing clients keep working, but an explicit `filter` wins when
        both are sent rather than silently intersecting with the group's implied category — two
        filters quietly ANDing is exactly the kind of surprise this API change is meant to end.
        """
        if self.filter is not None:
            return self.filter.as_kwargs()
        categories, taxa, prefixes = expand_search_group(self.group)
        return {"categories": categories, "taxa": taxa, "prefixes": prefixes}


class SemsimProfileSearchRequest(BaseModel):
    """Search driven by an entity's own phenotype profile instead of a hand-typed termset.

    `entity` is any phenotype-annotated node — a phenopacket Case, a MONDO disease, an MGI/MMRRC
    mouse model — and `filter` says what to rank against it, so patient->model, model->patient and
    disease->model are the same request with different filters.
    """

    entity: str = Field(..., title="Entity whose phenotype profile is the query (e.g. a Case id)")
    filter: SemsimSearchFilter = Field(..., title="Explicit category / taxon / prefix filter for the targets")
    metric: SemsimMetric = Field(SemsimMetric.ANCESTOR_INFORMATION_CONTENT, title="Similarity metric to use")
    directionality: SemsimDirectionality = Field(
        SemsimDirectionality.BIDIRECTIONAL, title="Directionality of the search"
    )
    limit: Optional[int] = Field(10, title="Limit the number of results", ge=1, le=50)


class TextAnnotationRequest(BaseModel):
    content: str = Field(..., title="The text content to annotate")
    prefix: Optional[List[str]] = Field(
        default=None,
        title="Restrict grounding results to entities using one of these CURIE prefixes (e.g. MONDO, HP)",
    )
    category: Optional[List[EntityCategory]] = Field(
        default=None,
        title="Restrict grounding results to entities of one of these biolink categories (e.g. biolink:Disease)",
    )


class PathographNode(BaseModel):
    id: str = Field(..., title="Stable merged node id (anchor curie, or <mondo>::<name> when disorder-local)")
    label: str = Field(..., title="Human-readable node label")
    node_type: str = Field(..., title="dismech node type (pathophysiology, phenotype, genetic, …)")
    color: Optional[str] = Field(None, title="dismech node fill color")
    is_orphan: bool = Field(False, title="Whether this node is an unmatched edge target")
    description: Optional[str] = Field(None, title="Node description")
    meta: Optional[dict] = Field(None, title="dismech node metadata (term_id, gene_terms, …)")
    sources: List[str] = Field(..., title="Mondo ids of the disorders contributing this node")


class PathographEdge(BaseModel):
    source: str = Field(..., title="Source node id")
    target: str = Field(..., title="Target node id")
    predicate: Optional[str] = Field(None, title="Causal predicate")
    description: Optional[str] = Field(None, title="Edge description")
    sources: List[str] = Field(..., title="Mondo ids of the disorders contributing this edge")


class PathographSource(BaseModel):
    id: str = Field(..., title="Mondo id of a contributing disorder")
    name: str = Field(..., title="Disorder name")
    url: Optional[str] = Field(None, title="Direct link to this disorder's dismech page")


class Pathograph(BaseModel):
    node_id: str = Field(..., title="The queried node id (disease Mondo or gene HGNC)")
    category: str = Field(..., title="'disease' or 'gene'")
    nodes: List[PathographNode] = Field(default_factory=list)
    edges: List[PathographEdge] = Field(default_factory=list)
    sources: List[PathographSource] = Field(default_factory=list, title="Disorders merged into this pathograph")
