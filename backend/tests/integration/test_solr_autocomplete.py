import pytest
from monarch_py.implementations.solr.solr_implementation import SolrImplementation

pytestmark = pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)


@pytest.mark.parametrize(
    "q, should_return",
    [
        # This fails because subclasses of Down syndrome come back first,
        # we need an edge ngram version of the keyword tokenized field
        # ("down syn", "Down syndrome"),
        ("marf", "Marfan syndrome"),
        ("BRC", "brc-1"),
        ("brc", "brc-1"),
    ],
)
def test_autocomplete(q, should_return):
    si = SolrImplementation()
    response = si.autocomplete(q)
    assert response
    assert response.total > 0

    names = [x.name for x in response.items]
    names.extend([x.symbol for x in response.items if x.symbol])
    print(names)
    assert should_return in names
