import oaklib.datamodels.ontology_metadata as omd
from oaklib import OntologyResource
from oaklib.constants import OAKLIB_MODULE
from oaklib.implementations.sqldb.sql_implementation import SqlImplementation

from fastapi import HTTPException

from monarch_py.api.additional_models import SemsimSearchGroup

IS_A = omd.slots.subClassOf.curie
HP_DB_URL = "https://s3.amazonaws.com/bbop-sqlite/hp.db.gz"


def compare_termsets(
    subjects=[""],
    objects=[""],
    predicates=[IS_A, "BFO:0000050"],
    offset: int = 0,
    limit: int = 20,
):
    hp_db = OAKLIB_MODULE.ensure_gunzip(url=HP_DB_URL, autoclean=False)
    oi = SqlImplementation(OntologyResource(slug=hp_db))
    results = oi.termset_pairwise_similarity(subjects, objects, predicates)
    return results


def parse_similarity_group(value: str):
    if value in SemsimSearchGroup._member_names_:
        value = value
    elif SemsimSearchGroup(value):
        value = SemsimSearchGroup(value).name
    else:
        raise HTTPException(status_code=404, detail="Prefix not found")
    return value
