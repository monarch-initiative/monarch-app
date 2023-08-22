########################################################################
# This file is used to import pytest fixtures from the tests directory #
########################################################################


from monarch_py.datamodels.model import AssociationResults, TermSetPairwiseSimilarity, HistoPheno, Node, SearchResults

# from .fixtures import autocomplete, histopheno, node, node_associations, search


def test_autocomplete(autocomplete):
    autocomplete = SearchResults(**autocomplete)
    assert autocomplete.total != 0


def test_compare(compare):
    tsps = TermSetPairwiseSimilarity(**compare)
    import pprint

    pprint.PrettyPrinter(indent=2).pprint(tsps.dict())
    assert len(tsps.subject_best_matches) != 0


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
