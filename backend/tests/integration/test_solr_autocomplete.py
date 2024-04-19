import pytest
from monarch_py.implementations.solr.solr_implementation import SolrImplementation

pytestmark = pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)


@pytest.mark.parametrize(
    "q, should_return",
    [
        ("down syn", "Down syndrome"),
        ("marf", "Marfan syndrome"),
        ("BRCA", "BRCA1"),
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
