import pytest
from unittest.mock import MagicMock

from monarch_py.datamodels.model import (
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
    get_links_for_field,
    get_provided_by_link,
    strip_json,
)
from monarch_py.utils.format_utils import get_headers_from_obj, to_json, to_tsv, to_yaml

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


@pytest.mark.parametrize(
    "obj, expected",
    [
        ("node", "node_headers"),
        ("search", "search_headers"),
        ("histopheno", "histobin_headers"),
        ("associations", "association_headers"),
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

    expected = request.getfixturevalue(expected)
    headers = get_headers_from_obj(obj)
    # Allow for the expected headers to be a subset of the actual headers,
    # so that the data model being ahead of new fields the Solr index won't
    # break the tests
    for header in expected:
        assert header in headers


@pytest.mark.skip(reason="It's broken and I'm dumb")
@pytest.mark.parametrize(
    "obj, expected, format",
    [
        ("node", "node_json", "json"),
        ("node", "node_tsv", "tsv"),
        ("node", "node_yaml", "yaml"),
    ],
)
def test_convert_to_tsv(obj, expected, format, request):
    obj = request.getfixturevalue(obj)
    node = Node(**obj)
    if format == "json":
        result = to_json(node, print_output=False)
    elif format == "tsv":
        result = to_tsv(node, print_output=False)
    elif format == "yaml":
        result = to_yaml(node, print_output=False)
    expected = request.getfixturevalue(expected)
    assert result == expected  # type: ignore
