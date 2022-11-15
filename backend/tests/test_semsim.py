import pytest
from oaklib import OntologyResource
from oaklib.implementations.sqldb.sql_implementation import SqlImplementation
from pprint import pprint
resource = OntologyResource(slug=f"sqlite:///phenio.db")
oi = SqlImplementation(resource)


def test_oak():
    print(oi.label("HP:0000498"))
    sim = oi.termset_pairwise_similarity(["HP:0001036"], ["HP:0002583"])
    pprint(sim)
