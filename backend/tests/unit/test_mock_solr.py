
def test_entity(mock_solr, node):
    si = mock_solr
    assert si.get_entity("MONDO:0020121").name == "muscular dystrophy"


def test_associations(mock_solr, associations):
    si = mock_solr
    assert si.get_associations("MONDO:0020121").total != 0


def test_autocomplete(mock_solr, autocomplete):
    si = mock_solr
    assert si.autocomplete("fanc").total != 0


def test_search(mock_solr, search):
    si = mock_solr
    assert si.search("fanc").total != 0


def test_histopheno(mock_solr, histopheno):
    si = mock_solr
    assert si.get_histopheno("MONDO:0020121").total != 0