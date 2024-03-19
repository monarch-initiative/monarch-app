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
        ("BRC", "BRCA1"),
        # This fails now because we prefer case sensitive matches over case insensitive matches
        #("brc", "BRCA1"),
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


@pytest.mark.parametrize(
    "id", [
        "MONDO:0007523",   # Ehlers-Danlos syndrome, hypermobility type
        "MONDO:0019391",   # Fanconi anemia
        "MONDO:0018954",   # Loeys-Dietz syndrome
        "MONDO:0011518",   # Wiedemann-Steiner syndrome
        "HGNC:4851",       # HTT
        "HGNC:3603",       # FBN1
        "HP:0001166",      # Arachnodactyly
        "HP:0001631",      # Atrial septal defect
        "UBERON:0000948",  # heart
        "UBERON:0006585",  # vestibular organ
    ]
)
def test_empty_autocomplete(id):
    si = SolrImplementation()
    response = si.autocomplete("*:*")
    assert response
    assert response.total > 0

    assert id in [x.id for x in response.items]
