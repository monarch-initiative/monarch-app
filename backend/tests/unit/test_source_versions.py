"""Tests for monarch_py.utils.source_versions."""

from monarch_py.utils.source_versions import (
    MONARCH_AGGREGATOR_INFORES,
    index_receipt,
    resolve_for_edge,
    resolve_for_infores,
)


def _receipt():
    """Synthetic receipt covering the three resolution cases.

    - alliance-ingest: aggregator (`infores:agr`) WITH per-MOD nesting (the
      target shape after alliance-ingest#10 lands).
    - hgnc-ingest: direct primary ingest (no aggregator chain).
    - kg-phenio: composite ingest with phenio nested under it; phenio in
      turn carries ontology leaves.
    - alliance-disease-association-ingest: aggregator WITHOUT per-MOD
      nesting (today's shape — exercises the bundle-level fallback).
    """
    return {
        "id": "monarch-kg",
        "version": "2026-05-07",
        "generated_at": "2026-05-07T16:11:30Z",
        "sources": [
            {
                "id": "alliance-ingest",
                "version": "8.3.0",
                "sources": [
                    {
                        "id": "infores:agr",
                        "name": "Alliance of Genome Resources",
                        "version": "8.3.0",
                        "version_method": "alliance_fms_api",
                        "sources": [
                            {
                                "id": "infores:zfin",
                                "name": "ZFIN",
                                "version": "2026-04-15",
                                "version_method": "alliance_fms_submission",
                                "urls": ["https://fms.alliancegenome.org/.../zfin"],
                            },
                            {
                                "id": "infores:mgi",
                                "name": "MGI",
                                "version": "2026-04-08",
                                "version_method": "alliance_fms_submission",
                            },
                        ],
                    },
                ],
            },
            {
                "id": "hgnc-ingest",
                "version": "2026-05-01",
                "sources": [
                    {
                        "id": "infores:hgnc",
                        "name": "HUGO Gene Nomenclature Committee",
                        "version": "2026-05-01",
                        "version_method": "http_last_modified",
                    },
                ],
            },
            {
                "id": "alliance-disease-association-ingest",
                "version": "8.3.0",
                "sources": [
                    {
                        "id": "infores:agr",
                        "name": "Alliance of Genome Resources",
                        "version": "8.3.0",
                        "version_method": "alliance_fms_api",
                        # Crucially, no per-MOD nesting yet.
                    },
                ],
            },
            {
                "id": "kg-phenio",
                "version": "v2026-05-06",
                "sources": [
                    {
                        "id": "phenio",
                        "name": "PHENIO",
                        "version": "v2026-05-06",
                        "version_method": "github_release_api",
                        "sources": [
                            {
                                "id": "infores:mondo",
                                "name": "MONDO",
                                "version": "2026-04-01",
                                "version_method": "owl_version_iri",
                            },
                            {
                                "id": "infores:hp",
                                "name": "HP",
                                "version": "2026-04-15",
                                "version_method": "owl_version_iri",
                            },
                        ],
                    },
                ],
            },
        ],
        "disagreements": [],
        "version_drift": [],
    }


def test_index_receipt_groups_by_producer():
    receipt = index_receipt(_receipt())
    assert set(receipt.by_producer) == {
        "alliance-ingest",
        "hgnc-ingest",
        "alliance-disease-association-ingest",
        "kg-phenio",
    }
    # alliance-ingest's flat index should include both the aggregator entry
    # AND its per-MOD nested entries.
    alliance = receipt.by_producer["alliance-ingest"]
    assert "infores:agr" in alliance
    assert "infores:zfin" in alliance
    assert "infores:mgi" in alliance
    # kg-phenio's index reaches the ontology leaves through phenio.
    kgp = receipt.by_producer["kg-phenio"]
    assert "infores:mondo" in kgp
    assert kgp["infores:mondo"].via == ("phenio",)


def test_canonical_producer_prefers_self_named_ingest():
    receipt = index_receipt(_receipt())
    assert receipt.canonical_producer["infores:hgnc"] == "hgnc-ingest"


def test_canonical_producer_prefers_phenio_for_ontologies():
    receipt = index_receipt(_receipt())
    assert receipt.canonical_producer["infores:mondo"] == "kg-phenio"
    assert receipt.canonical_producer["infores:hp"] == "kg-phenio"


def test_resolve_for_edge_aggregator_with_nested_mod():
    """ZFIN edge via AGR — picks the per-MOD entry from alliance-ingest."""
    receipt = index_receipt(_receipt())
    sv = resolve_for_edge(
        receipt,
        primary_knowledge_source="infores:zfin",
        aggregator_knowledge_sources=["infores:agr", MONARCH_AGGREGATOR_INFORES],
    )
    assert sv is not None
    assert sv.infores == "infores:zfin"
    assert sv.version == "2026-04-15"
    assert sv.version_method == "alliance_fms_submission"
    assert sv.via == ("infores:agr",)


def test_resolve_for_edge_aggregator_without_nesting():
    """ZFIN edge via an aggregator path with no per-MOD nesting — falls back
    to AGR's bundle-level entry. Built as its own receipt rather than
    mutating the shared fixture, so the test can't accidentally corrupt
    cached state (`ResolvedReceipt.by_producer` is a live dict)."""
    receipt = index_receipt(
        {
            "id": "monarch-kg",
            "version": "2026-05-07",
            "sources": [
                {
                    "id": "alliance-disease-association-ingest",
                    "version": "8.3.0",
                    "sources": [
                        {
                            "id": "infores:agr",
                            "name": "Alliance of Genome Resources",
                            "version": "8.3.0",
                            "version_method": "alliance_fms_api",
                            # No per-MOD nesting.
                        },
                    ],
                },
            ],
        }
    )
    sv = resolve_for_edge(
        receipt,
        primary_knowledge_source="infores:zfin",
        aggregator_knowledge_sources=["infores:agr", MONARCH_AGGREGATOR_INFORES],
    )
    assert sv is not None
    assert sv.infores == "infores:agr"  # fell through to bundle-level
    assert sv.version == "8.3.0"


def test_resolve_for_edge_direct_ingest_no_aggregator():
    """HGNC gene from hgnc-ingest — only monarch is the aggregator."""
    receipt = index_receipt(_receipt())
    sv = resolve_for_edge(
        receipt,
        primary_knowledge_source="infores:hgnc",
        aggregator_knowledge_sources=[MONARCH_AGGREGATOR_INFORES],
    )
    assert sv is not None
    assert sv.infores == "infores:hgnc"
    assert sv.version == "2026-05-01"


def test_resolve_for_edge_no_aggregators_at_all():
    receipt = index_receipt(_receipt())
    sv = resolve_for_edge(
        receipt,
        primary_knowledge_source="infores:hgnc",
        aggregator_knowledge_sources=None,
    )
    assert sv is not None
    assert sv.infores == "infores:hgnc"


def test_resolve_for_edge_unknown_primary_returns_none():
    receipt = index_receipt(_receipt())
    sv = resolve_for_edge(
        receipt,
        primary_knowledge_source="infores:never-heard-of",
        aggregator_knowledge_sources=[MONARCH_AGGREGATOR_INFORES],
    )
    assert sv is None


def test_resolve_for_infores_ontology():
    receipt = index_receipt(_receipt())
    sv = resolve_for_infores(receipt, "infores:mondo")
    assert sv is not None
    assert sv.version == "2026-04-01"
    assert sv.via == ("phenio",)


def test_resolve_for_infores_data_source():
    receipt = index_receipt(_receipt())
    sv = resolve_for_infores(receipt, "infores:hgnc")
    assert sv is not None
    assert sv.version == "2026-05-01"
    assert sv.via == ()


