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


class SemsimSearchCategory(Enum):
    HGNC = "Human Genes"
    MGI = "Mouse Genes"
    RGD = "Rat Genes"
    ZFIN = "Zebrafish Genes"
    WB = "C. Elegans Genes"
    MONDO = "Human Diseases"


class SemsimCompareRequest(BaseModel):
    subjects: List[str] = Field(..., title="List of subjects for comparison")
    objects: List[str] = Field(..., title="List of objects for comparison")


class SemsimSearchRequest(BaseModel):
    termset: List[str] = Field(..., title="Termset to search")
    category: SemsimSearchCategory = Field(..., title="Category to search for")
    limit: Optional[int] = Field(10, title="Limit the number of results", ge=1, le=50)
