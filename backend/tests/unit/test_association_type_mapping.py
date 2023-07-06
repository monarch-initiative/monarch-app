import pytest
from monarch_py.datamodels.model import AssociationTypeMapping
from monarch_py.utils.association_type_utils import (
    get_solr_query_fragment,
    get_sql_query_fragment,
    parse_query_string_for_category,
)


@pytest.fixture()
def basic_mapping():
    return AssociationTypeMapping(
        subject_label="Genes",
        object_label="Phenotypes",
        category="biolink:GeneToPhenotypeAssociation",
    )


def test_solr_basic_mapping(basic_mapping):
    query_fragment = get_solr_query_fragment(basic_mapping)
    assert query_fragment == 'category:"biolink:GeneToPhenotypeAssociation"'


def test_sql_basic_mapping(basic_mapping):
    query_fragment = get_sql_query_fragment(basic_mapping)
    assert query_fragment == 'category = "biolink:GeneToPhenotypeAssociation"'


def test_parse_association_type_query_string_single_category():
    query_string = 'category:"biolink:GeneToPhenotypeAssociation"'
    category = parse_query_string_for_category(query_string)
    assert category == "biolink:GeneToPhenotypeAssociation"


def test_parse_association_type_query_string_multiple_categories():
    query_string = 'category:"biolink:GeneToDiseaseAssociation" AND (predicate:"biolink:gene_associated_with_condition" OR predicate:"biolink:contributes_to")'
    category = parse_query_string_for_category(query_string)
    assert category == "biolink:GeneToDiseaseAssociation"
