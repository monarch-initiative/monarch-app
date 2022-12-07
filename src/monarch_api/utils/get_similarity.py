import oaklib.datamodels.ontology_metadata as omd
from oaklib import OntologyResource
from oaklib.constants import OAKLIB_MODULE
from oaklib.implementations.sqldb.sql_implementation import SqlImplementation

HP_DB_URL = "https://s3.amazonaws.com/bbop-sqlite/hp.db.gz"

IS_A = omd.slots.subClassOf.curie


def termlist_similarity(
    offset: int = 0,
    limit: int = 20,
    subjlist=[""],
    objlist=[""],
    predicates=[IS_A, "BFO:0000050"],
):

    hp_db = OAKLIB_MODULE.ensure_gunzip(url=HP_DB_URL, autoclean=False)

    oi = SqlImplementation(OntologyResource(slug=hp_db))

    results = oi.termset_pairwise_similarity(subjlist, objlist, predicates)

    return results
