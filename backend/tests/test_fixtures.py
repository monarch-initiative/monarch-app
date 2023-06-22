########################################################################
# This file is used to import pytest fixtures from the tests directory #
########################################################################

import pytest

from monarch_api.model import AssociationResults, Node, HistoPheno, SearchResults

from .fixtures import autocomplete, histopheno, node, node_associations, search


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

def test_node_associations(node_associations):
    node_associations = AssociationResults(**node_associations)
    assert node_associations.total != 0