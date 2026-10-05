"""How a query Solr refuses reaches the caller (#1458).

Solr answers a malformed or over-limit query with a 400 and an error message. The
service logged the message and then re-raised the `HTTPError` uncaught, so FastAPI
emitted a 500: the status said the server had broken when the query had been rejected,
which sends whoever reads it to the wrong place.
"""

import json
from unittest.mock import patch

import pytest
import requests
from fastapi.testclient import TestClient
from loguru import logger

from monarch_py.datamodels.solr import SolrQuery, core
from monarch_py.service.solr_service import SOLR_ERROR_MESSAGE_LIMIT, SolrQueryError, SolrService

TOO_MANY_CLAUSES = (
    "org.apache.solr.search.SyntaxError: Cannot parse 'subject:\"SGD:S000001393\" OR ...': too many boolean clauses"
)


def solr_response(status_code: int, body: dict) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response._content = json.dumps(body).encode()
    return response


def query_against(status_code: int, body: dict):
    service = SolrService(base_url="http://solr:8983/solr", core=core.ASSOCIATION)
    with patch("requests.post", return_value=solr_response(status_code, body)):
        return service.query(SolrQuery())


def test_a_rejected_query_raises_solr_query_error():
    with pytest.raises(SolrQueryError) as raised:
        query_against(400, {"error": {"msg": TOO_MANY_CLAUSES}})
    assert "too many boolean clauses" in raised.value.message


def test_a_failing_solr_is_not_reported_as_a_bad_query():
    """A 5xx is Solr being down or overloaded, which is ours and stays a 500."""
    with pytest.raises(requests.HTTPError):
        query_against(503, {"error": {"msg": "Service Unavailable"}})


def test_the_rejected_query_is_not_echoed_back_in_full():
    """Solr quotes the query it rejected, and the rejected ones are the long ones.

    The clause-limit failures ran past 50,000 characters, which is not a response body.
    The log keeps all of it; the exception carries an identifiable prefix.
    """
    logged: list[str] = []
    sink = logger.add(lambda message: logged.append(message.record["message"]), level="ERROR")
    long_message = "too many boolean clauses, parsing " + ('subject:"X" OR ' * 5000)
    try:
        with pytest.raises(SolrQueryError) as raised:
            query_against(400, {"error": {"msg": long_message}})
    finally:
        logger.remove(sink)

    assert len(raised.value.message) == SOLR_ERROR_MESSAGE_LIMIT
    assert raised.value.message.startswith("too many boolean clauses")
    assert any(long_message in entry for entry in logged), "the full message has to survive in the log"


def test_the_api_reports_a_rejected_query_as_a_bad_request():
    from monarch_py.api.main import app

    client = TestClient(app)
    with patch(
        "monarch_py.implementations.solr.solr_implementation.SolrImplementation.get_associations",
        side_effect=SolrQueryError(TOO_MANY_CLAUSES),
    ):
        response = client.get("/v3/api/association?entity=SGD:S000001393")

    assert response.status_code == 400, response.text
    assert "too many boolean clauses" in response.json()["detail"]
