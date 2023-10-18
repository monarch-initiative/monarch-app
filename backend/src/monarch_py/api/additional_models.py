from typing import List

from fastapi import Query, Request
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    request: Request
    limit: int = Query(default=20, ge=0, le=500)
    offset: int = Query(default=0, ge=0)

    class Config:
        arbitrary_types_allowed = True


class CompareRequest(BaseModel):
    subjects: List[str] = Field(..., title="List of subjects for comparison")
    objects: List[str] = Field(..., title="List of objects for comparison")
