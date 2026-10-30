"""Clause-count limits on association queries (#1458).

Solr parses every `fq` and every `facet.query` under `maxBooleanClauses`, and a query
that exceeds it fails to parse -- the whole request 400s, which the API surfaced as a
500. Because the clause count follows the size of the entity's closure/ortholog
expansion rather than anything about the request, an affected entity failed on every
attempt. These tests pin the property that avoids it: clause counts that do not grow
with the number of IDs.

They need no Solr: the ceiling is a property of the query string.
"""

import re

import pytest

from monarch_py.implementations.solr.solr_query_utils import (
    build_association_counts_query,
    build_association_query,
    build_terms_filter,
)

# The stock solrconfig value, which our deployment does not raise. Kept here rather
# than read from Solr so the test states the budget it is checking against.
SOLR_MAX_BOOLEAN_CLAUSES = 1024

# What ortholog traversal fetches at most, so the widest expansion a request can reach.
MAX_ORTHOLOGS = 500


def leaf_clauses(query_string: str) -> int:
    """How many boolean clauses Solr counts in a filter or facet query.

    A nested `_query_` is one clause however many values it carries, so splitting on
    the boolean operators counts what the parser counts.
    """
    return len(re.split(r"\s+(?:OR|AND)\s+", query_string))


def synthetic_ids(n: int) -> list[str]:
    return [f"NCBIGene:{i:07d}" for i in range(n)]


@pytest.mark.parametrize("n", [1, 2, 171, 220, MAX_ORTHOLOGS + 1, 5000])
@pytest.mark.parametrize("direct", [True, False])
def test_entity_filter_stays_under_the_clause_limit(n, direct):
    """The failing query in #1458 carried ~220 IDs across six fields: 1,320 clauses."""
    query = build_association_query(entity=synthetic_ids(n), direct=direct)
    for fq in query.filter_queries:
        assert leaf_clauses(fq) <= SOLR_MAX_BOOLEAN_CLAUSES, f"{leaf_clauses(fq)} clauses in {fq[:120]}..."


@pytest.mark.parametrize("field_arg", ["subject", "object", "entity"])
def test_clause_count_does_not_depend_on_how_many_ids_arrive(field_arg):
    """The property, not just the current margin.

    An OR chain satisfies the limit check above at small N and fails it at large N, so
    checking a ceiling alone would pass again if this reverted to a chain. Clause count
    being flat in N is what makes the ceiling unreachable.
    """
    counts = {
        n: [leaf_clauses(fq) for fq in build_association_query(**{field_arg: synthetic_ids(n)}).filter_queries]
        for n in (1, 10, 1000)
    }
    assert counts[1] == counts[10] == counts[1000], counts


def test_ortholog_facet_queries_stay_under_the_clause_limit():
    """Facet queries have their own budget, and the counts query is the wider fan-out.

    An ortholog-traversed count spans every association type times six count levels,
    and the ortholog levels name every expanded entity, so this was over the limit at
    roughly half the entity count the table query needed.
    """
    entities = synthetic_ids(MAX_ORTHOLOGS + 1)
    query = build_association_counts_query(entities)
    assert query.facet_queries, "no facet queries to check"
    for fq in query.facet_queries:
        assert leaf_clauses(fq) <= SOLR_MAX_BOOLEAN_CLAUSES, f"{leaf_clauses(fq)} clauses in {fq[:120]}..."
    for fq in query.filter_queries:
        assert leaf_clauses(fq) <= SOLR_MAX_BOOLEAN_CLAUSES, f"{leaf_clauses(fq)} clauses in {fq[:120]}..."


def test_every_id_reaches_the_query():
    """A bounded clause count is worthless if it is bounded by dropping IDs."""
    ids = synthetic_ids(300)
    fq = build_terms_filter(["subject", "subject_closure"], ids)
    for entity_id in ids:
        assert f"{entity_id}," in fq or f'{entity_id}"' in fq, f"{entity_id} missing from the terms list"


def test_a_single_string_is_not_iterated_character_by_character():
    """`build_terms_filter("subject", "HP:0000001")`-shaped calls come from the CLI."""
    assert build_terms_filter(["subject"], "HP:0000001") == '_query_:"{!terms f=subject}HP:0000001"'


def test_a_value_containing_the_separator_is_not_split():
    """`entity` is caller-supplied, so `A,B` has to go on meaning `A,B`.

    Packed into the terms list it would silently become a match on either half.
    """
    fq = build_terms_filter(["subject"], ["HP:0000001", "WEIRD:a,b"])
    assert fq == '_query_:"{!terms f=subject}HP:0000001" OR subject:"WEIRD:a,b"'


def test_a_value_containing_a_quote_cannot_escape_the_nested_query():
    """A quote in the value would end the `_query_` string and leave the remainder to
    be parsed as query syntax."""
    fq = build_terms_filter(["subject"], ['BAD:" OR subject:*'])
    assert "_query_" not in fq
    assert fq == 'subject:"BAD:\\" OR subject:*"'
