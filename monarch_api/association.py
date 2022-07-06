from fastapi import APIRouter
import pysolr

router = APIRouter()


@router.get("/test")
async def test():
    results = {"data": "EXAMPLE ASSOCIATION"}# solr.search
    return results