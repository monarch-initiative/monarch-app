from fastapi import Query, Request
from pydantic import BaseModel


# todo: convert this to linkml and add it to the schema
class PaginationParams(BaseModel):
    request: Request
    limit: int = Query(default=20, ge=0)
    offset: int = Query(default=1, ge=1)

    class Config:
        arbitrary_types_allowed = True

