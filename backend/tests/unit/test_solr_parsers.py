import pytest

from monarch_py.datamodels.solr import SolrQuery, SolrQueryResult
from monarch_py.implementations.solr.solr_parsers import parse_histopheno
from monarch_py.utils.utils import dict_diff

def test_parse_histopheno(histopheno_results, histopheno, node):
    """Test the parse_histopheno function"""
    parsed = parse_histopheno(SolrQueryResult(**histopheno_results), subject_closure=node.id)
    assert parsed == histopheno, f"Parsed result is not as expected. Difference: {dict_diff(parsed.dict(), histopheno.dict())}"