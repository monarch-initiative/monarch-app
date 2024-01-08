import pytest
from unittest.mock import MagicMock

from monarch_py.datamodels.model import (
    AssociationCountList,
    AssociationResults,
    HistoPheno,
    Node,
    SearchResults,
    ExpandedCurie,
)
from monarch_py.utils.utils import (
    compare_dicts,
    dict_factory,
    dict_diff,
    escape,
    get_headers_from_obj,
    get_links_for_field,
    get_provided_by_link,
    strip_json,
    to_tsv_str,
)

### Test basic utility methods ###


def test_strip_json():
    doc = {"a": 1, "b": 2, "c": 3}
    assert strip_json(doc, "a", "b") == {"c": 3}


def test_strip_json_missing():
    doc = {"a": 1, "b": 2, "c": 3}
    assert strip_json(doc, "d") == {"a": 1, "b": 2, "c": 3}


def test_escape():
    assert escape("HP:123") == r"HP\:123"


def test_dict_factory():
    cursor = MagicMock()
    cursor.description = [("a",), ("b",), ("c",)]
    row = (1, 2, 3)
    assert dict_factory(cursor, row) == {"a": 1, "b": 2, "c": 3}


@pytest.mark.parametrize(
    "dict1,dict2",
    [
        ({"a": 1, "b": 2}, {"a": 1, "b": 2}),
        ({"a": 1, "b": 2}, {"b": 2, "a": 1}),
    ],
)
def test_compare_dicts(dict1, dict2):
    assert compare_dicts(dict1, dict2) is True


def test_compare_dicts_false():
    assert compare_dicts({"a": 1, "b": 2}, {"a": 1, "b": 3}) is False


@pytest.mark.parametrize(
    "d1, d2, expected",
    [
        ({"a": 1, "b": 2}, {"a": 1, "b": 2}, {}),
        ({"a": 1, "b": 2}, {"b": 2, "a": 1}, {}),
        ({"a": 1, "b": 2}, {"a": 1, "b": 3}, {"Dict-1-b": 2, "Dict-2-b": 3}),
    ],
)
def test_dict_diff(d1, d2, expected):
    assert dict_diff(d1, d2) == expected


### Test URL fetching methods ###


def test_get_links_for_field():
    field = ["PMID:123", "PMID:456"]
    assert get_links_for_field(field) == [
        ExpandedCurie(id="PMID:123", url="http://identifiers.org/pubmed/123"),
        ExpandedCurie(id="PMID:456", url="http://identifiers.org/pubmed/456"),
    ]


def test_get_provided_by_link():
    assert get_provided_by_link("alliance_gene_nodes") == ExpandedCurie(
        id="alliance_gene", url="https://monarch-initiative.github.io/monarch-ingest/Sources/alliance/#gene"
    )


### Test output conversion methods ###
# TODO


@pytest.mark.parametrize(
    "obj, expected",
    [
        (
            "node",
            [
                "id",
                "category",
                "name",
                "full_name",
                "deprecated",
                "description",
                "xref",
                "provided_by",
                "in_taxon",
                "in_taxon_label",
                "symbol",
                "synonym",
                "uri",
                "inheritance",
                "causal_gene",
                "causes_disease",
                "mappings",
                "external_links",
                "provided_by_link",
                "association_counts",
                "node_hierarchy",
            ],
        ),
        (
            "search",
            [
                "id",
                "category",
                "name",
                "full_name",
                "deprecated",
                "description",
                "xref",
                "provided_by",
                "in_taxon",
                "in_taxon_label",
                "symbol",
                "synonym",
                "uri",
                "highlight",
                "score",
            ],
        ),
        (
            "histopheno",
            ["label", "count", "id"],
        ),
        (
            "associations",
            [
                "id",
                "category",
                "subject",
                "original_subject",
                "subject_namespace",
                "subject_category",
                "subject_closure",
                "subject_label",
                "subject_closure_label",
                "subject_taxon",
                "subject_taxon_label",
                "predicate",
                "object",
                "original_object",
                "object_namespace",
                "object_category",
                "object_closure",
                "object_label",
                "object_closure_label",
                "object_taxon",
                "object_taxon_label",
                "primary_knowledge_source",
                "aggregator_knowledge_source",
                "negated",
                "pathway",
                "evidence_count",
                "has_evidence",
                "has_evidence_links",
                "grouping_key",
                "provided_by",
                "provided_by_link",
                "publications",
                "publications_links",
                "qualifiers",
                "frequency_qualifier",
                "onset_qualifier",
                "sex_qualifier",
                "stage_qualifier",
                "qualifiers_label",
                "qualifiers_namespace",
                "qualifiers_category",
                "qualifiers_closure",
                "qualifiers_closure_label",
                "frequency_qualifier_label",
                "frequency_qualifier_namespace",
                "frequency_qualifier_category",
                "frequency_qualifier_closure",
                "frequency_qualifier_closure_label",
                "onset_qualifier_label",
                "onset_qualifier_namespace",
                "onset_qualifier_category",
                "onset_qualifier_closure",
                "onset_qualifier_closure_label",
                "sex_qualifier_label",
                "sex_qualifier_namespace",
                "sex_qualifier_category",
                "sex_qualifier_closure",
                "sex_qualifier_closure_label",
                "stage_qualifier_label",
                "stage_qualifier_namespace",
                "stage_qualifier_category",
                "stage_qualifier_closure",
                "stage_qualifier_closure_label",
            ],
        ),
    ],
)
def test_get_headers_from_obj(obj, expected, request):
    if obj == "node":
        node = request.getfixturevalue(obj)
        obj = Node(**node)
    elif obj == "search":
        search = request.getfixturevalue(obj)
        obj = SearchResults(**search)
    elif obj == "histopheno":
        histopheno = request.getfixturevalue(obj)
        obj = HistoPheno(**histopheno)
    elif obj == "associations":
        associations = request.getfixturevalue(obj)
        obj = AssociationResults(**associations)

    headers = get_headers_from_obj(obj)
    print(headers)
    assert headers == expected
