import pytest

from monarch_py.datamodels.model import Node
from monarch_py.datamodels.solr import SolrQuery, SolrQueryResult
from monarch_py.implementations.solr.solr_parsers import (
    parse_autocomplete,
    parse_associations,
    parse_association_counts,
    parse_histopheno,
    parse_search,
    )
from monarch_py.utils.utils import dict_diff


def test_parse_associations(association_results, associations):
    association_results["response"]["numFound"] = association_results["response"].pop("num_found")
    solr_response = SolrQueryResult(**association_results)
    parsed = parse_associations(solr_response)
    assert parsed == associations, \
        f"Parsed result is not as expected. Difference: {dict_diff(parsed.dict(), associations)}"


def test_parse_association_counts(association_counts_results, association_counts):
    association_counts_results["response"]["numFound"] = association_counts_results["response"].pop("num_found")
    solr_response = SolrQueryResult(**association_counts_results)
    parsed = parse_associations(solr_response)
    assert parsed == association_counts, \
        f"Parsed result is not as expected. Difference: {dict_diff(parsed.dict(), association_counts)}"


def test_parse_histopheno(histopheno_results, histopheno, node):
    histopheno_results["response"]["numFound"] = histopheno_results["response"].pop("num_found")
    solr_response = SolrQueryResult(**histopheno_results)
    parsed = parse_histopheno(solr_response, subject_closure=Node(**node).id)
    assert parsed == histopheno, \
        f"Parsed result is not as expected. Difference: {dict_diff(parsed.dict(), histopheno)}"


def test_parse_search(search_results, search):
    search_results["response"]["numFound"] = search_results["response"].pop("num_found")
    solr_response = SolrQueryResult(**search_results)
    parsed = parse_search(solr_response)
    assert parsed == search, \
        f"Parsed result is not as expected. Difference: {dict_diff(parsed.dict(), search)}"
    

def test_parse_autocomplete(autocomplete_results, autocomplete):
    autocomplete_results["response"]["numFound"] = autocomplete_results["response"].pop("num_found")
    solr_response = SolrQueryResult(**autocomplete_results)
    parsed = parse_autocomplete(solr_response)
    assert parsed == autocomplete, \
        f"Parsed result is not as expected. Difference: {dict_diff(parsed.dict(), autocomplete)}"