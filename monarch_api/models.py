from fastapi import Query, Request
from pydantic import BaseModel


class PaginationParams(BaseModel):
    request: Request
    limit: int = 20
    offset: int = Query(default=1, ge=1)

    class Config:
        arbitrary_types_allowed = True

