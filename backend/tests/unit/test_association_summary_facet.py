import json
from unittest.mock import patch
from urllib.parse import parse_qs

import pytest
import requests

from monarch_py.implementations.solr.solr_implementation import SolrImplementation
from monarch_py.implementations.solr.solr_query_utils import build_association_summary_facet


def test_summary_facet_shape():
    facet = build_association_summary_facet(
        group_by="subject",
        unique_fields=["grouping_key"],
        stat_fields=["medic_approval_date"],
        label_fields=["subject_label"],
        facet_fields=["medic_jurisdiction", "object"],
        facet_labels={"object": "object_label"},
        group_sort="grouping_key",
        offset=10,
        limit=5,
    )
    assert facet["unique_grouping_key"] == "unique(grouping_key)"
    assert facet["groups_count"] == "unique(subject)"
    assert facet["facet_object"]["facet"] == {
        "label": {"type": "terms", "field": "object_label", "limit": 1, "mincount": 1}
    }
    assert "facet" not in facet["facet_medic_jurisdiction"]
    groups = facet["groups"]
    assert (groups["field"], groups["offset"], groups["limit"]) == ("subject", 10, 5)
    assert groups["sort"] == "unique_grouping_key desc"
    assert set(groups["facet"]) == {
        "unique_grouping_key",
        "min_medic_approval_date",
        "max_medic_approval_date",
        "label_subject_label",
        "facet_medic_jurisdiction",
        "facet_object",
    }


@pytest.mark.parametrize(
    "kwargs",
    [
        {"group_by": "subject) OR (*"},
        {"group_by": "subject", "facet_fields": ["object label"]},
        {"group_by": "subject", "facet_labels": {"object": "x:y"}},
        {"group_by": "subject", "group_sort": "object"},
    ],
)
def test_summary_facet_rejects_bad_input(kwargs):
    with pytest.raises(ValueError):
        build_association_summary_facet(**kwargs)


# Every field list rejects id, closure, closure-label and ancestor-path fields: grouping,
# counting or faceting on them makes Solr build a bucket per row or per ancestor.
@pytest.mark.parametrize(
    "kwargs",
    [
        {"group_by": "id"},
        {"group_by": "object_closure"},
        {"group_by": "subject", "unique_fields": ["id"]},
        {"group_by": "subject", "unique_fields": ["object_closure"]},
        {"group_by": "subject", "stat_fields": ["subject_closure"]},
        {"group_by": "subject", "label_fields": ["object_closure_label"]},
        {"group_by": "subject", "facet_fields": ["id"]},
        {"group_by": "subject", "facet_fields": ["subject_taxon_closure"]},
        {"group_by": "subject", "facet_fields": ["object_ancestor_path"]},
        {"group_by": "subject", "facet_labels": {"id": "subject_label"}},
        {"group_by": "subject", "facet_labels": {"object": "object_closure_label"}},
    ],
)
def test_summary_facet_rejects_unbounded_fields(kwargs):
    with pytest.raises(ValueError, match="cannot be used in an association summary"):
        build_association_summary_facet(**kwargs)


# The summaries SectionDrugUses.vue requests, on a disease page (side = subject) and a
# drug page (side = object); none of them may trip the guard.
@pytest.mark.parametrize(
    "side, secondary",
    [("subject", "object"), ("object", "disease_context_qualifier")],
)
def test_summary_facet_allows_drug_uses_requests(side, secondary):
    build_association_summary_facet(
        group_by=side,
        unique_fields=["grouping_key", secondary],
        stat_fields=["medic_approval_date"],
        label_fields=[f"{side}_label", f"{side}_category"],
        facet_fields=["medic_jurisdiction", secondary, "agent_type", "knowledge_level"],
        facet_labels={secondary: f"{secondary}_label"},
    )
    build_association_summary_facet(group_by="medic_jurisdiction", unique_fields=[side])
    build_association_summary_facet(group_by="predicate")
    build_association_summary_facet(
        group_by="grouping_key",
        stat_fields=["medic_approval_date"],
        label_fields=["predicate", "object", "object_label", "object_category"],
        facet_fields=[
            "medic_jurisdiction",
            "disease_context_qualifier",
            "population_context_qualifier",
            "agent_type",
            "knowledge_level",
        ],
        facet_labels={"disease_context_qualifier": "disease_context_qualifier_label"},
    )


SUMMARY_FACETS = {
    "count": 7,
    "unique_grouping_key": 4,
    "groups_count": 12,
    "facet_object": {
        "buckets": [
            {"val": "MONDO:0005148", "count": 5, "label": {"buckets": [{"val": "type 2 diabetes", "count": 5}]}},
            {"val": "MONDO:0005015", "count": 2, "label": {"buckets": []}},
        ]
    },
    "groups": {
        "buckets": [
            {
                "val": "CHEBI:6801",
                "count": 5,
                "unique_grouping_key": 3,
                "min_medic_approval_date": "19950303",
                "max_medic_approval_date": "20240624",
                "label_subject_label": {"buckets": [{"val": "metformin", "count": 5}]},
                "facet_object": {
                    "buckets": [
                        {"val": "MONDO:0005148", "count": 5, "label": {"buckets": [{"val": "type 2 diabetes"}]}}
                    ]
                },
            },
            # A group with none of the fields: no stats, no label, empty facet.
            {"val": "CHEBI:40237", "count": 2},
        ]
    },
}


def _get_summary(facets):
    """Run a summary against a mocked Solr HTTP response; return it and the posted params."""
    body = {
        "responseHeader": {"status": 0, "QTime": 1, "params": {}},
        "response": {"numFound": 7, "start": 0, "docs": []},
    }
    if facets is not None:
        body["facets"] = facets
    response = requests.Response()
    response.status_code = 200
    response._content = json.dumps(body).encode()
    with patch("monarch_py.service.solr_service.requests.post", return_value=response) as mock_post:
        summary = SolrImplementation().get_association_summary(
            entity="MONDO:0005148",
            category="biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation",
            group_by="subject",
            unique_fields=["grouping_key"],
            stat_fields=["medic_approval_date"],
            label_fields=["subject_label"],
            facet_fields=["object"],
            facet_labels={"object": "object_label"},
            offset=10,
            limit=2,
        )
    return summary, parse_qs(mock_post.call_args.kwargs["data"])


def test_summary_posts_a_rows_free_json_facet_query():
    _, params = _get_summary(SUMMARY_FACETS)
    assert params["rows"] == ["0"]
    assert params["facet"] == ["false"]
    assert "sort" not in params
    groups = json.loads(params["json.facet"][0])["groups"]
    assert (groups["field"], groups["offset"], groups["limit"]) == ("subject", 10, 2)


def test_summary_parses_facet_response():
    summary, _ = _get_summary(SUMMARY_FACETS)
    assert (summary.total, summary.group_total, summary.offset, summary.limit) == (7, 12, 10, 2)
    assert summary.unique == {"grouping_key": 4}
    assert [(f.value, f.count, f.label) for f in summary.facets["object"]] == [
        ("MONDO:0005148", 5, "type 2 diabetes"),
        ("MONDO:0005015", 2, None),
    ]
    full, empty = summary.groups
    assert (full.value, full.count, full.unique) == ("CHEBI:6801", 5, {"grouping_key": 3})
    assert (full.stats["medic_approval_date"].min, full.stats["medic_approval_date"].max) == ("19950303", "20240624")
    assert full.fields == {"subject_label": "metformin"}
    assert [(f.value, f.label) for f in full.facets["object"]] == [("MONDO:0005148", "type 2 diabetes")]
    assert empty.unique == {"grouping_key": 0}
    assert (empty.stats["medic_approval_date"].min, empty.stats["medic_approval_date"].max) == (None, None)
    assert empty.fields == {"subject_label": None}
    assert empty.facets == {"object": []}


def test_summary_without_facets_is_empty():
    # Solr omits `facets` when no row matches.
    summary, _ = _get_summary(None)
    assert (summary.total, summary.group_total, summary.groups) == (0, 0, [])
