########################################################################
# This file is used to import pytest fixtures from the tests directory #
########################################################################

from monarch_py.datamodels.model import AssociationResults, HistoPheno, Node, SearchResults


def test_autocomplete(autocomplete):
    autocomplete = SearchResults(**autocomplete)
    assert autocomplete.total != 0


def test_search(search):
    search = SearchResults(**search)
    assert search.total != 0


def test_histopheno(histopheno):
    histopheno = HistoPheno(**histopheno)
    assert histopheno.id == "MONDO:0020121"


def test_node(node):
    node = Node(**node)
    assert node.id == "MONDO:0020121"


def test_node_associations(associations):
    association_results = AssociationResults(**associations)
    assert association_results.total != 0
