from oaklib import OntologyResource
from oaklib.implementations.sqldb.sql_implementation import SqlImplementation

HP_DB_PATH = "../../hp.db"

def termlist_similarity(
    offset: int = 0,
    limit: int = 20,
    subjlist=None,
    objlist=None,
    predicate="i,p",
    ):

    oi = SqlImplementation(OntologyResource(slug=f'sqlite:///input/go-nucleus.db'))

    results = 

    return results

