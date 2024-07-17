from enum import Enum
from typing import List, Optional

from fastapi import Query, Request
from pydantic import BaseModel, Field


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
    directionality: SemsimDirectionality = (
        Query(SemsimDirectionality.BIDIRECTIONAL, title="Directionality of the search"),
    )
    limit: Optional[int] = Field(10, title="Limit the number of results", ge=1, le=50)


class TextAnnotationRequest(BaseModel):
    content: str = Field(..., title="The text content to annotate")
