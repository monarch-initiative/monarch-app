import oaklib.datamodels.ontology_metadata as omd
from oaklib import OntologyResource
from oaklib.implementations.sqldb.sql_implementation import SqlImplementation

# TODO: download this and check to see if it exists
HP_DB_PATH = "hp.db"

IS_A = omd.slots.subClassOf.curie

def termlist_similarity(
    offset: int = 0,
    limit: int = 20,
    subjlist=[""],
    objlist=[""],
    predicates=[IS_A, "BFO:0000050"],
    ):

    oi = SqlImplementation(OntologyResource(slug=HP_DB_PATH))

    results = oi.termset_pairwise_similarity(subjlist,objlist,predicates)

    return results

