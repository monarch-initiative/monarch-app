from oaklib import OntologyResource
from oaklib.implementations.sqldb.sql_implementation import SqlImplementation
HP_DB_URL = "phenio.db"

resource = OntologyResource(slug=HP_DB_URL)
oi = SqlImplementation(resource)


def test_oak():
    print(oi.label("HP:0000498"))

    sim = oi.termset_pairwise_similarity(["HP:0001036"],
                                         ["HP:0002583"])
    assert sim.subject_best_matches["HP:0001036"]
