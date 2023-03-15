from fastapi import APIRouter, Depends
from monarch_py.implementations.solr.solr_implementation import SolrImplementation

from monarch_api.model import HistoPheno 

router = APIRouter(
    prefix="/api/histpheno", # ?????
    # tags=["??????"],
    responses={404: {"description": "Not Found"}},
)
