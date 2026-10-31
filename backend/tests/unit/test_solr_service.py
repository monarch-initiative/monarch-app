import json
from unittest.mock import patch

import pytest
import requests

from monarch_py.datamodels.solr import SolrQuery, core
from monarch_py.service.solr_service import SolrQueryError, SolrService, FIELD_TYPE_SUFFIXES


def test_consolidate_highlights():
    # Input highlights
    highlights = {
        "MONDO:123": {
            "name_t": ["<em>example</em> name", "another <em>example</em>"],
            "description_t": ["<em>example</em> description"],
            "name_ac": ["a third <em>example</em> name"],
        },
        "HGNC:456": {
            "name_t": ["<em>heart</em> gene"],
            "description_t": ["gene description about <em>heart</em>"],
            "name_ac": ["<em>heart</em> gene"],
        },
    }

    # Expected consolidated highlights
    expected = {
        "MONDO:123": {
            "name": ["<em>example</em> name", "a third <em>example</em> name", "another <em>example</em>"],
            "description": ["<em>example</em> description"],
        },
        "HGNC:456": {
            "name": ["<em>heart</em> gene"],
            "description": ["gene description about <em>heart</em>"],
        },
    }

    # Call the method
    result = SolrService._consolidate_highlights(highlights, FIELD_TYPE_SUFFIXES)

    # Assert the result matches the expected output
    assert result == expected


def test_strip_excluded_fields():
    # Input document
    doc = {
        "id": "123",
        "name_t": "example name",
        "description_t": "example description",
        "_version_": 1,
        "iri": "http://example.com",
        "frequency_computed_sortable_float": 0.5,
        "has_quotient_sortable_float": 0.3,
        "has_percentage_sortable_float": 0.7,
    }

    # Expected stripped document
    expected = {
        "id": "123",
    }

    # Call the method
    SolrService._strip_excluded_fields(doc)

    # Assert the result matches the expected output
    assert doc == expected


def test_strip_json():
    # Input document
    doc = {
        "id": "123",
        "name": "example name",
        "_version_": 1,
        "iri": "http://example.com",
    }

    # Expected stripped document
    expected = {
        "id": "123",
        "name": "example name",
    }

    # Call the method
    SolrService._strip_json(doc, "_version_", "iri")

    # Assert the result matches the expected output
    assert doc == expected


def test_strip_json_by_suffix():
    # Input document
    doc = {
        "id": "123",
        "name_t": "example name",
        "description_t": "example description",
        "name": "example name",
    }

    # Expected stripped document
    expected = {
        "id": "123",
        "name": "example name",
    }

    # Call the method
    SolrService._strip_json_by_suffix(doc, "_t")

    # Assert the result matches the expected output
    assert doc == expected


def _solr_response(status_code: int, text: str) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response._content = text.encode()
    return response


def test_query_raises_solr_query_error_with_solr_message_on_4xx():
    body = json.dumps({"responseHeader": {"status": 400, "QTime": 0}, "error": {"msg": "undefined field nope"}})
    solr = SolrService(base_url="http://solr", core=core.ASSOCIATION)
    with patch("requests.post", return_value=_solr_response(400, body)):
        with pytest.raises(SolrQueryError, match="undefined field nope"):
            solr.query(SolrQuery())


@pytest.mark.parametrize(
    "status_code,text",
    [
        (500, json.dumps({"responseHeader": {"status": 500, "QTime": 0}, "error": {"msg": "boom"}})),
        (502, "<html>Bad Gateway</html>"),  # e.g. from a proxy; not JSON
    ],
)
def test_query_keeps_server_errors_as_http_errors(status_code, text):
    solr = SolrService(base_url="http://solr", core=core.ASSOCIATION)
    with patch("requests.post", return_value=_solr_response(status_code, text)):
        with pytest.raises(requests.HTTPError) as excinfo:
            solr.query(SolrQuery())
    assert not isinstance(excinfo.value, SolrQueryError)
