import pytest

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
