import pytest

from monarch_py.datamodels.model import Node
from monarch_py.datamodels.solr import SolrQuery, SolrQueryResult
from monarch_py.implementations.solr.solr_parsers import parse_histopheno
from monarch_py.utils.utils import dict_diff

def test_parse_histopheno(histopheno_results, histopheno, node):
    """Test the parse_histopheno function"""
    histopheno_results["response"]["numFound"] = histopheno_results["response"].pop("num_found")
    solr_response = SolrQueryResult(**histopheno_results)
    parsed = parse_histopheno(solr_response, subject_closure=Node(**node).id)
    assert parsed == histopheno, f"Parsed result is not as expected. Difference: {dict_diff(parsed.dict(), histopheno.dict())}"

