from monarch_py.datamodels.model import Node
from monarch_py.datamodels.solr import SolrQueryResult
from monarch_py.implementations.solr.solr_parsers import (
    parse_association_counts,
    parse_association_table,
    parse_associations,
    parse_autocomplete,
    parse_entity,
    parse_histopheno,
    parse_mappings,
    parse_search,
)
from monarch_py.utils.utils import dict_diff


def test_parse_associations(association_response, associations):
    association_response["response"]["numFound"] = association_response["response"].pop("num_found")
    solr_response = SolrQueryResult(**association_response)
    parsed = parse_associations(solr_response).model_dump()
    assert parsed == associations, f"Parsed result is not as expected. Difference: {dict_diff(parsed, associations)}"


def test_parse_associations_compact(association_response, associations_compact):
    association_response["response"]["numFound"] = association_response["response"].pop("num_found")
    solr_response = SolrQueryResult(**association_response)
    parsed = parse_associations(solr_response, compact=True).model_dump()
    assert parsed == associations_compact, (
        f"Parsed result is not as expected. Difference: {dict_diff(parsed, associations_compact)}"
    )


def test_parse_association_counts(association_counts_response, association_counts, node):
    association_counts_response["response"]["numFound"] = association_counts_response["response"].pop("num_found")
    solr_response = SolrQueryResult(**association_counts_response)
    parsed = parse_association_counts(solr_response, entity=Node(**node).id).model_dump()
    assert parsed == association_counts, (
        f"Parsed result is not as expected. Difference: {dict_diff(parsed, association_counts)}"
    )


def test_parse_association_table(association_table_response, association_table, node):
    association_table_response["response"]["numFound"] = association_table_response["response"].pop("num_found")
    solr_response = SolrQueryResult(**association_table_response)
    parsed = parse_association_table(solr_response, entity=[Node(**node).id], offset=0, limit=5).model_dump()
    assert parsed == association_table, (
        f"Parsed result is not as expected. Difference: {dict_diff(parsed, association_table)}"
    )


def test_parse_entity(entity_response, node):
    parsed = parse_entity(entity_response).model_dump()
    assert all(parsed[k] == v for k, v in parsed.items() if k in node)


def test_parse_histopheno(histopheno_response, histopheno, node):
    histopheno_response["response"]["numFound"] = histopheno_response["response"].pop("num_found")
    solr_response = SolrQueryResult(**histopheno_response)
    parsed = parse_histopheno(solr_response, subject_closure=Node(**node).id).model_dump()
    assert parsed == histopheno, f"Parsed result is not as expected. Difference: {dict_diff(parsed, histopheno)}"


def test_parse_search(search_response, search):
    search_response["response"]["numFound"] = search_response["response"].pop("num_found")
    solr_response = SolrQueryResult(**search_response)
    parsed = parse_search(solr_response).model_dump()
    # assert that top level keys are the same
    assert set(parsed.keys()) == set(search.keys()), (
        f"Parsed result keys are not as expected. Difference: {dict_diff(parsed, search)}"
    )
    # compare the first document (parsed.items[0]), assert that all of the keys in expected search (search.items[0])
    for key in search["items"][0].keys():
        assert key in parsed["items"][0], f"Key {key} not found in parsed result."


def test_parse_autocomplete(autocomplete_response, autocomplete):
    autocomplete_response["response"]["numFound"] = autocomplete_response["response"].pop("num_found")
    solr_response = SolrQueryResult(**autocomplete_response)
    parsed = parse_autocomplete(solr_response).model_dump()
    # assert that top level keys are the same
    assert set(parsed.keys()) == set(autocomplete.keys()), (
        f"Parsed result keys are not as expected. Difference: {dict_diff(parsed, autocomplete)}"
    )
    # compare the first document (parsed.items[0]), assert that all of the keys in expected autocomplete (autocomplete.items[0])
    for key in autocomplete["items"][0].keys():
        assert key in parsed["items"][0], f"Key {key} not found in parsed result."


def test_parse_mappings(mapping_response, mappings):
    mapping_response["response"]["numFound"] = mapping_response["response"].pop("num_found")
    solr_response = SolrQueryResult(**mapping_response)
    parsed = parse_mappings(solr_response).model_dump()
    assert parsed == mappings, f"Parsed result is not as expected. Difference: {dict_diff(parsed, mappings)}"
