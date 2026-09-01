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
    HGNC = "Human Genes"
    MGI = "Mouse Genes"
    RGD = "Rat Genes"
    ZFIN = "Zebrafish Genes"
    WB = "C. Elegans Genes"
    MONDO = "Human Diseases"


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
    group: SemsimSearchGroup = Field(..., title="Group of entities to search within (e.g. Human Genes)")
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
