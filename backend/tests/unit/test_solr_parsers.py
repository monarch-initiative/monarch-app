from typing import Optional, List, Union

import pytest
from pydantic import BaseModel

from monarch_py.datamodels.model import AssociationDirectionEnum, Node
from monarch_py.datamodels.solr import SolrQueryResult
from monarch_py.implementations.solr.solr_parsers import (
    _is_scalar_type,
    convert_facet_fields,
    convert_facet_queries,
    get_association_direction,
    normalize_solr_doc_for_model,
    parse_association_counts,
    parse_association_table,
    parse_associations,
    parse_autocomplete,
    parse_entity,
    parse_histopheno,
    parse_mappings,
    parse_search,
)
from monarch_py.utils.utils import dict_diff


def test_parse_associations(association_response, associations):
    association_response["response"]["numFound"] = association_response["response"].pop("num_found")
    solr_response = SolrQueryResult(**association_response)
    parsed = parse_associations(solr_response).model_dump()
    assert parsed == associations, f"Parsed result is not as expected. Difference: {dict_diff(parsed, associations)}"


def test_parse_associations_compact(association_response, associations_compact):
    association_response["response"]["numFound"] = association_response["response"].pop("num_found")
    solr_response = SolrQueryResult(**association_response)
    parsed = parse_associations(solr_response, compact=True).model_dump()
    assert parsed == associations_compact, (
        f"Parsed result is not as expected. Difference: {dict_diff(parsed, associations_compact)}"
    )


def test_parse_association_counts(association_counts_response, association_counts, node):
    association_counts_response["response"]["numFound"] = association_counts_response["response"].pop("num_found")
    solr_response = SolrQueryResult(**association_counts_response)
    parsed = parse_association_counts(solr_response, entities=[Node(**node).id]).model_dump()
    assert parsed == association_counts, (
        f"Parsed result is not as expected. Difference: {dict_diff(parsed, association_counts)}"
    )


def test_parse_association_table(association_table_response, association_table, node):
    association_table_response["response"]["numFound"] = association_table_response["response"].pop("num_found")
    solr_response = SolrQueryResult(**association_table_response)
    parsed = parse_association_table(solr_response, entity=[Node(**node).id], offset=0, limit=5).model_dump()
    assert parsed == association_table, (
        f"Parsed result is not as expected. Difference: {dict_diff(parsed, association_table)}"
    )


def test_parse_entity(entity_response, node):
    parsed = parse_entity(entity_response).model_dump()
    assert all(parsed[k] == v for k, v in parsed.items() if k in node)


def test_parse_entity_strips_descendant_lists(entity_response):
    """has_descendant and has_descendant_label should be stripped to avoid multi-MB responses."""
    assert entity_response.get("has_descendant"), "fixture should have has_descendant to test stripping"
    entity = parse_entity(entity_response)
    assert entity.has_descendant is None
    assert entity.has_descendant_label is None
    assert entity.has_descendant_count is not None  # count (integer) should be preserved


def test_parse_histopheno(histopheno_response, histopheno, node):
    histopheno_response["response"]["numFound"] = histopheno_response["response"].pop("num_found")
    solr_response = SolrQueryResult(**histopheno_response)
    parsed = parse_histopheno(solr_response, subject_closure=Node(**node).id).model_dump()
    assert parsed == histopheno, f"Parsed result is not as expected. Difference: {dict_diff(parsed, histopheno)}"


def test_parse_search(search_response, search):
    search_response["response"]["numFound"] = search_response["response"].pop("num_found")
    solr_response = SolrQueryResult(**search_response)
    parsed = parse_search(solr_response).model_dump()
    # assert that top level keys are the same
    assert set(parsed.keys()) == set(search.keys()), (
        f"Parsed result keys are not as expected. Difference: {dict_diff(parsed, search)}"
    )
    # compare the first document (parsed.items[0]), assert that all of the keys in expected search (search.items[0])
    for key in search["items"][0].keys():
        assert key in parsed["items"][0], f"Key {key} not found in parsed result."


def test_parse_autocomplete(autocomplete_response, autocomplete):
    autocomplete_response["response"]["numFound"] = autocomplete_response["response"].pop("num_found")
    solr_response = SolrQueryResult(**autocomplete_response)
    parsed = parse_autocomplete(solr_response).model_dump()
    # assert that top level keys are the same
    assert set(parsed.keys()) == set(autocomplete.keys()), (
        f"Parsed result keys are not as expected. Difference: {dict_diff(parsed, autocomplete)}"
    )
    # compare the first document (parsed.items[0]), assert that all of the keys in expected autocomplete (autocomplete.items[0])
    for key in autocomplete["items"][0].keys():
        assert key in parsed["items"][0], f"Key {key} not found in parsed result."


def test_parse_mappings(mapping_response, mappings):
    mapping_response["response"]["numFound"] = mapping_response["response"].pop("num_found")
    solr_response = SolrQueryResult(**mapping_response)
    parsed = parse_mappings(solr_response).model_dump()
    assert parsed == mappings, f"Parsed result is not as expected. Difference: {dict_diff(parsed, mappings)}"


# =====================================================================
# Tests for _is_scalar_type
# =====================================================================


@pytest.mark.parametrize(
    "type_hint,expected",
    [
        (str, True),
        (int, True),
        (float, True),
        (bool, True),
        (Optional[str], True),
        (Optional[int], True),
        (List[str], False),
        (list, False),
        (Optional[List[str]], False),
        (Union[str, int], False),
        (dict, False),
    ],
    ids=[
        "str",
        "int",
        "float",
        "bool",
        "Optional[str]",
        "Optional[int]",
        "List[str]",
        "list",
        "Optional[List]",
        "Union[str,int]",
        "dict",
    ],
)
def test_is_scalar_type(type_hint, expected):
    assert _is_scalar_type(type_hint) is expected


# =====================================================================
# Tests for normalize_solr_doc_for_model
# =====================================================================


def test_normalize_converts_single_list_to_scalar():
    class MyModel(BaseModel):
        name: str
        count: int

    doc = {"name": ["Alice"], "count": [42]}
    result = normalize_solr_doc_for_model(doc, MyModel)
    assert result["name"] == "Alice"
    assert result["count"] == 42


def test_normalize_leaves_list_fields_as_lists():
    class MyModel(BaseModel):
        tags: List[str]

    doc = {"tags": ["a", "b", "c"]}
    result = normalize_solr_doc_for_model(doc, MyModel)
    assert result["tags"] == ["a", "b", "c"]


def test_normalize_leaves_non_list_values_unchanged():
    class MyModel(BaseModel):
        name: str

    doc = {"name": "Alice"}
    result = normalize_solr_doc_for_model(doc, MyModel)
    assert result["name"] == "Alice"


def test_normalize_converts_empty_list_to_none():
    class MyModel(BaseModel):
        name: Optional[str] = None

    doc = {"name": []}
    result = normalize_solr_doc_for_model(doc, MyModel)
    assert result["name"] is None


def test_normalize_ignores_unknown_fields():
    class MyModel(BaseModel):
        name: str

    doc = {"name": "Alice", "extra_field": ["ignored"]}
    result = normalize_solr_doc_for_model(doc, MyModel)
    assert result["extra_field"] == ["ignored"]


def test_normalize_handles_optional_scalar():
    class MyModel(BaseModel):
        label: Optional[str] = None

    doc = {"label": ["Test Label"]}
    result = normalize_solr_doc_for_model(doc, MyModel)
    assert result["label"] == "Test Label"


# =====================================================================
# Tests for convert_facet_fields and convert_facet_queries
# =====================================================================


def test_convert_facet_fields():
    solr_facet_fields = {"category": ["biolink:Gene", 10, "biolink:Disease", 5]}
    result = convert_facet_fields(solr_facet_fields)
    assert len(result) == 1
    assert result[0].label == "category"
    assert len(result[0].facet_values) == 2
    assert result[0].facet_values[0].label == "biolink:Gene"
    assert result[0].facet_values[0].count == 10


def test_convert_facet_fields_empty():
    assert convert_facet_fields({}) == []


def test_convert_facet_queries():
    solr_facet_queries = {'category:"biolink:Gene"': 10, 'category:"biolink:Disease"': 5}
    result = convert_facet_queries(solr_facet_queries)
    assert len(result) == 2
    assert result[0].label == 'category:"biolink:Gene"'
    assert result[0].count == 10


def test_convert_facet_queries_empty():
    assert convert_facet_queries({}) == []


# =====================================================================
# Tests for get_association_direction
# =====================================================================


@pytest.mark.parametrize(
    "entity,doc,expected",
    [
        (
            ["HGNC:4851"],
            {"subject": "HGNC:4851", "object": "MONDO:0007078"},
            AssociationDirectionEnum.outgoing,
        ),
        (
            ["MONDO:0007078"],
            {"subject": "HGNC:4851", "object": "MONDO:0007078"},
            AssociationDirectionEnum.incoming,
        ),
        (
            ["HGNC:parent"],
            {"subject": "HGNC:4851", "subject_closure": ["HGNC:4851", "HGNC:parent"], "object": "MONDO:0007078"},
            AssociationDirectionEnum.outgoing,
        ),
        (
            ["MONDO:parent"],
            {"subject": "HGNC:4851", "object": "MONDO:0007078", "object_closure": ["MONDO:0007078", "MONDO:parent"]},
            AssociationDirectionEnum.incoming,
        ),
        (
            ["MONDO:0007078"],
            {"subject": "DRUG:001", "object": "HP:001", "disease_context_qualifier": "MONDO:0007078"},
            AssociationDirectionEnum.incoming,
        ),
        (
            ["MONDO:parent"],
            {
                "subject": "DRUG:001",
                "object": "HP:001",
                "disease_context_qualifier": "MONDO:child",
                "disease_context_qualifier_closure": ["MONDO:child", "MONDO:parent"],
            },
            AssociationDirectionEnum.incoming,
        ),
    ],
    ids=[
        "outgoing-subject",
        "incoming-object",
        "outgoing-subject-closure",
        "incoming-object-closure",
        "incoming-disease-qualifier",
        "incoming-disease-qualifier-closure",
    ],
)
def test_get_association_direction(entity, doc, expected):
    assert get_association_direction(entity, doc) == expected


def test_get_association_direction_raises_when_not_found():
    doc = {"subject": "HGNC:4851", "object": "MONDO:0007078"}
    with pytest.raises(ValueError, match="not found in association"):
        get_association_direction(["UNKNOWN:001"], doc)
