import pytest
from oaklib import OntologyResource
from oaklib.implementations.sqldb.sql_implementation import SqlImplementation
from pprint import pprint
resource = OntologyResource(slug=f"sqlite:///phenio.db")
oi = SqlImplementation(resource)


def test_oak():
    print(oi.label("HP:0000498"))
    sim = oi.termset_pairwise_similarity(["HP:0001036",
                                          "HP:0001978",
                                          "HP:0001903",
                                          "HP:0000498",
                                          "HP:0001974",
                                          "HP:0008551",
                                          "HP:0008707",
                                          "HP:0002249",
                                          "HP:0003251"],
                                         ["HP:0002583",
                                          "HP:0002583",
                                          "HP:0002240",
                                          "HP:0011877",
                                          "HP:0002840",
                                          "HP:0001508",
                                          "HP:0001640"])
    assert sim.subject_best_matches["HP:0001036"]
