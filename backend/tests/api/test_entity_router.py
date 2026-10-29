from unittest.mock import MagicMock, patch

import pytest
import requests
from fastapi import HTTPException

from fastapi.testclient import TestClient

from monarch_py.api.entity import router
from monarch_py.datamodels.association_summary import AssociationSummary
from monarch_py.datamodels.model import Node
from monarch_py.service.solr_service import SolrQueryError
from monarch_py.datamodels.category_enums import AssociationCategory

client = TestClient(router)


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.get_entity")
def test_entity(mock_get_entity, node):
    mock_get_entity.return_value = Node(**node)
    client.get("/MONDO:0019391")
    mock_get_entity.assert_called_with("MONDO:0019391", extra=True)


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.get_association_table")
def test_association_table(mock_get_assoc_table):
    mock_get_assoc_table.return_value = MagicMock()
    client.get("/MONDO:0019391/biolink:DiseaseToPhenotypicFeatureAssociation")
    mock_get_assoc_table.assert_called_with(
        entity="MONDO:0019391",
        # The path param is a section *key*, not an AssociationCategory: a section can
        # combine several categories (LOINC) or span them (MEDIC+CTD), so it reaches the
        # implementation as a plain string. Legacy sections key on their category, which is
        # why this value is unchanged. This assertion was passing an enum until now only
        # because the API suite could not be collected when that change was made.
        category=AssociationCategory.DISEASE_TO_PHENOTYPIC_FEATURE_ASSOCIATION.value,
        q=None,
        traverse_orthologs=False,
        direct=False,
        facet_fields=None,
        facet_queries=None,
        filter_queries=None,
        sort=None,
        offset=0,
        limit=20,
    )


@pytest.mark.parametrize(
    "key",
    [
        "*",  # `escape()` only escapes ':', so this reached Solr as `category:*`
        "case-phenotype-grid",  # shadowed grid route; used to 422, briefly returned an empty 200
        "biolink:Bogus",
        'a"b',
    ],
)
def test_association_table_rejects_unknown_section_key(key):
    """The path param can no longer be the AssociationCategory enum, since a section key may
    be free-form. Validating against the configured keys restores what the enum gave us: an
    unknown value fails loudly rather than reaching Solr, where `/entity/{id}/*` returned
    every category's associations instead of one section's."""
    # TestClient wraps the bare router, which has no exception handler mounted, so the
    # 422 surfaces as a raise. Against the mounted app it is an HTTP 422 response.
    with pytest.raises(HTTPException) as excinfo:
        client.get(f"/MONDO:0019391/{key}")
    assert excinfo.value.status_code == 422


@pytest.mark.parametrize(
    "key",
    ["biolink:DiseaseToPhenotypicFeatureAssociation", "biolink:CausalGeneToDiseaseAssociation"],
)
@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.get_association_table")
def test_association_table_accepts_configured_section_keys(mock_get_assoc_table, key):
    mock_get_assoc_table.return_value = MagicMock()
    assert client.get(f"/MONDO:0019391/{key}").status_code == 200


SUMMARY_SECTION = "biolink:DiseaseToPhenotypicFeatureAssociation"


@patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation.get_association_summary")
def test_association_summary_parses_facet_labels(mock_get_summary):
    mock_get_summary.return_value = AssociationSummary(total=0, group_by="subject", group_total=0)
    response = client.get(
        f"/MONDO:0019391/{SUMMARY_SECTION}/summary",
        params={"group_by": "subject", "facet_labels": ["object:object_label", "subject:subject_label"]},
    )
    assert response.status_code == 200
    kwargs = mock_get_summary.call_args.kwargs
    assert kwargs["facet_labels"] == {"object": "object_label", "subject": "subject_label"}
    assert kwargs["category"] == SUMMARY_SECTION


def test_association_summary_rejects_malformed_facet_labels():
    with pytest.raises(HTTPException) as excinfo:
        client.get(f"/MONDO:0019391/{SUMMARY_SECTION}/summary", params={"group_by": "subject", "facet_labels": "x"})
    assert excinfo.value.status_code == 422


@pytest.mark.parametrize(
    "params",
    [
        {"group_by": "subject", "group_sort": "object"},  # not count, index or a unique field
        {"group_by": "subject) OR (*"},  # not a field name
    ],
)
@patch("monarch_py.service.solr_service.SolrService.query")
def test_association_summary_bad_input_is_422(mock_query, params):
    with pytest.raises(HTTPException) as excinfo:
        client.get(f"/MONDO:0019391/{SUMMARY_SECTION}/summary", params=params)
    assert excinfo.value.status_code == 422
    mock_query.assert_not_called()


@patch("monarch_py.service.solr_service.SolrService.query")
def test_association_summary_solr_rejection_is_422(mock_query):
    # Solr 400s on e.g. an unknown or unindexed field; its message becomes the detail.
    mock_query.side_effect = SolrQueryError("undefined field: nonexistent_field")
    with pytest.raises(HTTPException) as excinfo:
        client.get(f"/MONDO:0019391/{SUMMARY_SECTION}/summary", params={"group_by": "nonexistent_field"})
    assert excinfo.value.status_code == 422
    assert excinfo.value.detail == "undefined field: nonexistent_field"


@patch("monarch_py.service.solr_service.SolrService.query")
def test_association_summary_solr_server_error_is_not_422(mock_query):
    mock_query.side_effect = requests.HTTPError("500 Server Error")
    with pytest.raises(requests.HTTPError):
        client.get(f"/MONDO:0019391/{SUMMARY_SECTION}/summary", params={"group_by": "subject"})
