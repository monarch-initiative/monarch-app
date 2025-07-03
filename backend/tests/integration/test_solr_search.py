import pytest

from monarch_py.datamodels.category_enums import AssociationCategory, EntityCategory
from monarch_py.datamodels.model import AssociationDirectionEnum
from monarch_py.implementations.solr.solr_implementation import SolrImplementation

pytestmark = pytest.mark.skipif(
    condition=not SolrImplementation().solr_is_available(),
    reason="Solr is not available",
)


@pytest.mark.parametrize(
    "query",
    [
        "fgf8a",
        "MONDO:0015938",
        "Alzheimer disease 16",
        "breast cancer",
        # Failing because we don't have synonyms coming in from Phenio (!)
        #        "AD16",
        "symphalangism, C. S. Lewis type",
        "OMIM:301045",  # Confirmation that we load & search xrefs for Mondo
    ],
)
def test_search_query_has_some_results(query: str):
    si = SolrImplementation()
    response = si.search(query)
    assert response
    assert response.total > 0


def test_search_sort():
    si = SolrImplementation()
    response = si.search("marfan", sort="name desc")
    assert response
    assert response.total > 0
    assert response.items[0].name > response.items[-1].name


def test_search_highlighting():
    si = SolrImplementation()
    response = si.search("fgf8a", highlighting=True)
    assert response
    assert response.total > 0
    first_doc = response.items[0]
    assert first_doc
    assert "name" in first_doc.highlighting


def test_facet_fields():
    si = SolrImplementation()
    response = si.search("syndrome", facet_fields=["category", "in_taxon"])
    assert response
    assert response.total > 0
    assert response.facet_fields
    category = [ff for ff in response.facet_fields if ff.label == "category"][0]
    assert category


def test_single_filter_queries():
    si = SolrImplementation()
    response = si.search("syndrome", category=[EntityCategory.DISEASE])
    assert response
    assert response.total > 0
    assert response.items[0].category == "biolink:Disease"


def test_multiple_filter_queries():
    si = SolrImplementation()
    response = si.search("eye", category=[EntityCategory.DISEASE, EntityCategory.PHENOTYPIC_FEATURE])
    assert response
    assert response.total > 0
    for i, item in enumerate(response.items):
        assert item.category in ["biolink:Disease", "biolink:PhenotypicFeature"]


def test_association_facets():
    si = SolrImplementation()
    response = si.get_association_facets(facet_fields=["category"])
    assert response
    assert response.facet_fields
    category = [ff for ff in response.facet_fields if ff.label == "category"][0]
    assert category
    d2p = [fv for fv in category.facet_values if fv.label == "biolink:DiseaseToPhenotypicFeatureAssociation"][0]
    assert d2p
    assert d2p.count > 100000


def test_association_facet_query():
    si = SolrImplementation()

    response = si.get_association_facets(
        subject_closure="MONDO:0007947",
        facet_queries=[
            'object_closure:"HP:0000924"',
            'object_closure:"HP:0000707"',
            'object_closure:"HP:0000152"',
            'object_closure:"HP:0001574"',
            'object_closure:"HP:0000478"',
        ],
    )
    assert response
    assert response.facet_queries
    hp924 = [fq for fq in response.facet_queries if fq.label == 'object_closure:"HP:0000924"'][0]
    assert hp924.count > 20

    hp707 = [fq for fq in response.facet_queries if fq.label == 'object_closure:"HP:0000707"'][0]
    assert hp707.count > 5

    hp152 = [fq for fq in response.facet_queries if fq.label == 'object_closure:"HP:0000152"'][0]
    assert hp152.count > 20


def test_association_counts_for_disease():
    si = SolrImplementation()
    association_counts = si.get_association_counts(entity="MONDO:0007947")
    assert association_counts
    assert len(association_counts.items) > 0

    causal_genes = [ac for ac in association_counts.items if ac.category == "biolink:CausalGeneToDiseaseAssociation"][0]
    assert causal_genes.label == "Causal Gene"

    disease_phenotype = [
        ac for ac in association_counts.items if ac.category == "biolink:DiseaseToPhenotypicFeatureAssociation"
    ][0]
    assert disease_phenotype.label == "Disease to Phenotype"


def test_association_counts_for_eds():
    si = SolrImplementation()
    association_counts = si.get_association_counts(entity="MONDO:0020066")
    assert association_counts
    assert len(association_counts.items) > 0


def test_association_counts_for_phenotype():
    si = SolrImplementation()
    association_counts = si.get_association_counts(entity="HP:0000707")  # HP:0025096 ?
    assert association_counts
    assert len(association_counts.items) > 0

    disease_phenotype = [
        ac for ac in association_counts.items if ac.category == "biolink:DiseaseToPhenotypicFeatureAssociation"
    ][0]
    assert disease_phenotype.label == "Disease to Phenotype"

    gene_phenotype = [
        ac for ac in association_counts.items if ac.category == "biolink:GeneToPhenotypicFeatureAssociation"
    ][0]
    assert gene_phenotype.label == "Gene to Phenotype"


def test_association_table():
    si = SolrImplementation()
    association_results = si.get_association_table(
        "MONDO:0007947", AssociationCategory.DISEASE_TO_PHENOTYPIC_FEATURE_ASSOCIATION
    )
    assert association_results
    assert association_results.total > 5
    assert association_results.items[0].direction == AssociationDirectionEnum.outgoing


@pytest.mark.parametrize(
    "id",
    [
        "MONDO:0007523",  # Ehlers-Danlos syndrome, hypermobility type
        "MONDO:0019391",  # Fanconi anemia
        "MONDO:0018954",  # Loeys-Dietz syndrome
        "MONDO:0011518",  # Wiedemann-Steiner syndrome
        "HGNC:4851",  # HTT
        "HGNC:3603",  # FBN1
        "HP:0001166",  # Arachnodactyly
        "HP:0001631",  # Atrial septal defect
        "UBERON:0000948",  # heart
        "UBERON:0006585",  # vestibular organ
    ],
)
def test_empty_search(id):
    si = SolrImplementation()
    response = si.autocomplete("*:*")
    assert response
    assert response.total > 0

    assert id in [x.id for x in response.items]
