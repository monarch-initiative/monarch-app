"""Unit tests for entity grid utilities."""

from monarch_py.utils.entity_grid_utils import (
    _build_columns,
    _build_rows,
    _build_cells,
    _build_bins,
    bin_members,
    build_entity_grid,
    parse_bin_facets,
    make_cell_key,
    sort_columns_by_category,
)
from monarch_py.datamodels.grid_configs import get_grid_config
from monarch_py.datamodels.grid_groupings import RowGroupingConfig, GroupingType, bin_facet_key
from monarch_py.datamodels.model import GridColumnEntity, EntityGridResponse


def facets_for(bins: dict, ordered_bin_ids: list, counts: dict = None) -> dict:
    """A `facets` response block: {bin_id: [row entity ids]} in `ordered_bin_ids` order.

    Mirrors what Solr's JSON Facet API returns for `build_bin_facet`, including the
    `count` per bin and the omission of `entities` for a bin with no matches.

    A bin's `count` is its *association* count, independent of how many distinct row
    entities it holds. Pass `counts` to set it; it defaults to one per entity.
    """
    counts = counts or {}
    out = {}
    for index, bin_id in enumerate(ordered_bin_ids):
        members = bins.get(bin_id, [])
        facet = {"count": counts.get(bin_id, len(members))}
        if members:
            facet["entities"] = {"buckets": [{"val": m, "count": 1} for m in members]}
        out[bin_facet_key(index)] = facet
    return out


# =====================================================================
# Tests for _build_columns
# =====================================================================


def test_columns_include_source_association_data():
    config = get_grid_config("case-phenotype")
    docs = [
        {
            "subject": "CASE:001",
            "subject_label": "Case 1",
            "object": "MONDO:0007078",
            "object_label": "Achondroplasia",
            "category": "biolink:CaseToDiseaseAssociation",
            "predicate": "biolink:has_phenotype",
            "publications": ["PMID:12345"],
            "primary_knowledge_source": "infores:hpo",
        },
        {
            "subject": "CASE:002",
            "subject_label": "Case 2",
            "object": "MONDO:0007078",
            "object_label": "Achondroplasia",
            "category": "biolink:CaseToDiseaseAssociation",
            "predicate": "biolink:has_phenotype",
            "publications": ["PMID:67890", "PMID:11111"],
            "primary_knowledge_source": "infores:hpo",
        },
    ]

    columns = _build_columns(docs, "MONDO:0007078", config)

    assert len(columns) == 2
    col1 = columns[0]
    assert col1.source_association_category == "biolink:CaseToDiseaseAssociation"
    assert col1.source_association_predicate == "biolink:has_phenotype"
    assert col1.source_association_publications == ["PMID:12345"]
    assert col1.source_association_primary_knowledge_source == "infores:hpo"


def test_columns_handle_missing_association_fields():
    config = get_grid_config("case-phenotype")
    docs = [
        {
            "subject": "CASE:001",
            "object": "MONDO:0007078",
        }
    ]

    columns = _build_columns(docs, "MONDO:0007078", config)

    assert len(columns) == 1
    assert columns[0].source_association_category is None
    assert columns[0].source_association_predicate is None


# =====================================================================
# Tests for sort_columns_by_category
# =====================================================================


def test_sort_columns_by_category():
    columns = [
        GridColumnEntity(
            id="MONDO:001",
            category="biolink:Disease",
            is_direct=True,
            source_association_category="biolink:CorrelatedGeneToDiseaseAssociation",
        ),
        GridColumnEntity(
            id="MONDO:002",
            category="biolink:Disease",
            is_direct=True,
            source_association_category="biolink:CausalGeneToDiseaseAssociation",
        ),
        GridColumnEntity(
            id="MONDO:003",
            category="biolink:Disease",
            is_direct=True,
            source_association_category="biolink:CorrelatedGeneToDiseaseAssociation",
        ),
    ]

    category_order = [
        "biolink:CausalGeneToDiseaseAssociation",
        "biolink:CorrelatedGeneToDiseaseAssociation",
    ]

    sorted_cols = sort_columns_by_category(columns, category_order)
    assert sorted_cols[0].id == "MONDO:002"
    assert sorted_cols[1].source_association_category == "biolink:CorrelatedGeneToDiseaseAssociation"
    assert sorted_cols[2].source_association_category == "biolink:CorrelatedGeneToDiseaseAssociation"


def test_sort_preserves_order_within_category():
    columns = [
        GridColumnEntity(
            id="A", category="biolink:Disease", is_direct=True, source_association_category="biolink:Causal"
        ),
        GridColumnEntity(
            id="B", category="biolink:Disease", is_direct=True, source_association_category="biolink:Causal"
        ),
        GridColumnEntity(
            id="C", category="biolink:Disease", is_direct=True, source_association_category="biolink:Causal"
        ),
    ]

    sorted_cols = sort_columns_by_category(columns, ["biolink:Causal"])
    assert [c.id for c in sorted_cols] == ["A", "B", "C"]


def test_sort_empty_list():
    assert sort_columns_by_category([], ["biolink:Causal"]) == []


def test_sort_empty_category_order():
    columns = [
        GridColumnEntity(id="A", category="biolink:Disease", is_direct=True),
        GridColumnEntity(id="B", category="biolink:Disease", is_direct=True),
    ]
    sorted_cols = sort_columns_by_category(columns, [])
    assert [c.id for c in sorted_cols] == ["A", "B"]


# =====================================================================
# Tests for make_cell_key
# =====================================================================


def test_make_cell_key():
    assert make_cell_key("COL:001", "ROW:001") == "COL:001:ROW:001"


def test_make_cell_key_with_different_ids():
    assert make_cell_key("CASE:123", "HP:0001234") == "CASE:123:HP:0001234"


# =====================================================================
# Tests for parse_bin_facets
# =====================================================================


def test_parse_bin_facets_assigns_entities_to_bins():
    facets = facets_for({"BIN:001": ["HP:001"], "BIN:002": ["HP:002"]}, ["BIN:001", "BIN:002"])
    counts, entity_bins = parse_bin_facets(facets, ["BIN:001", "BIN:002"])
    assert counts == {"BIN:001": 1, "BIN:002": 1}
    assert entity_bins == {"HP:001": "BIN:001", "HP:002": "BIN:002"}


def test_parse_bin_facets_first_bin_in_order_wins():
    """An entity under several bins lands in the earliest one, which is what the
    closure scan this replaced did via its ordered bin list."""
    facets = facets_for({"BIN:002": ["HP:001"], "BIN:001": ["HP:001"]}, ["BIN:002", "BIN:001"])
    _, entity_bins = parse_bin_facets(facets, ["BIN:002", "BIN:001"])
    assert entity_bins == {"HP:001": "BIN:002"}


def test_parse_bin_facets_empty_bin_has_no_entities_key():
    """Solr omits the sub-facet for a bin with no matches; that is not an error."""
    facets = facets_for({"BIN:001": []}, ["BIN:001"])
    counts, entity_bins = parse_bin_facets(facets, ["BIN:001"])
    assert counts == {"BIN:001": 0}
    assert entity_bins == {}


def test_parse_bin_facets_missing_bin_counts_zero():
    counts, entity_bins = parse_bin_facets({}, ["BIN:001", "BIN:002"])
    assert counts == {"BIN:001": 0, "BIN:002": 0}
    assert entity_bins == {}


def test_bin_members_keeps_an_entity_in_every_bin_it_matches():
    """Unlike the row's own `bin_id`, per-bin membership is not exclusive."""
    facets = facets_for({"BIN:001": ["HP:001"], "BIN:002": ["HP:001", "HP:002"]}, ["BIN:001", "BIN:002"])
    assert bin_members(facets, ["BIN:001", "BIN:002"]) == {
        "BIN:001": ["HP:001"],
        "BIN:002": ["HP:001", "HP:002"],
    }


# =====================================================================
# Tests for _build_rows
# =====================================================================


def test_build_rows_from_docs():
    config = get_grid_config("case-phenotype")
    docs = [
        {"object": "HP:001", "object_label": "Phenotype 1", "subject": "CASE:001"},
        {"object": "HP:002", "object_label": "Phenotype 2", "subject": "CASE:001"},
    ]
    rows = _build_rows(docs, config, {"HP:001": "BIN:001", "HP:002": "BIN:002"})
    assert len(rows) == 2
    assert rows[0].id == "HP:001"
    assert rows[0].bin_id == "BIN:001"
    assert rows[1].id == "HP:002"
    assert rows[1].bin_id == "BIN:002"


def test_build_rows_deduplicates():
    config = get_grid_config("case-phenotype")
    docs = [
        {"object": "HP:001", "object_label": "P1", "subject": "CASE:001"},
        {"object": "HP:001", "object_label": "P1", "subject": "CASE:002"},
    ]
    rows = _build_rows(docs, config, {"HP:001": "BIN:001"})
    assert len(rows) == 1


def test_build_rows_skips_no_bin_match():
    """An entity in no bin has nowhere to render, so it is dropped rather than shown
    unbinned -- the same thing that happened when its closure hit no bin."""
    config = get_grid_config("case-phenotype")
    docs = [{"object": "HP:001", "object_label": "P1", "subject": "CASE:001"}]
    rows = _build_rows(docs, config, {})
    assert len(rows) == 0


def test_build_rows_skips_missing_row_id():
    config = get_grid_config("case-phenotype")
    docs = [{"subject": "CASE:001"}]
    rows = _build_rows(docs, config, {"HP:001": "BIN:001"})
    assert len(rows) == 0


# =====================================================================
# Tests for _build_cells
# =====================================================================


def test_build_cells_from_docs():
    config = get_grid_config("case-phenotype")
    column_map = {
        "CASE:001": GridColumnEntity(id="CASE:001", category="biolink:Case", is_direct=True),
        "CASE:002": GridColumnEntity(id="CASE:002", category="biolink:Case", is_direct=True),
    }
    docs = [
        {"subject": "CASE:001", "object": "HP:001"},
        {"subject": "CASE:002", "object": "HP:001"},
    ]
    cells = _build_cells(docs, column_map, config)
    assert len(cells) == 2
    assert "CASE:001:HP:001" in cells
    assert cells["CASE:001:HP:001"].present is True


def test_build_cells_with_qualifiers():
    config = get_grid_config("case-phenotype")
    column_map = {"CASE:001": GridColumnEntity(id="CASE:001", category="biolink:Case", is_direct=True)}
    docs = [
        {
            "subject": "CASE:001",
            "object": "HP:001",
            "onset_qualifier": "HP:0003577",
            "onset_qualifier_label": "Congenital onset",
        }
    ]
    cells = _build_cells(docs, column_map, config)
    cell = cells["CASE:001:HP:001"]
    assert cell.qualifiers is not None
    assert cell.qualifiers["onset_qualifier"].value == "HP:0003577"
    assert cell.qualifiers["onset_qualifier"].label == "Congenital onset"


def test_build_cells_without_qualifiers():
    config = get_grid_config("case-phenotype")
    column_map = {"CASE:001": GridColumnEntity(id="CASE:001", category="biolink:Case", is_direct=True)}
    docs = [{"subject": "CASE:001", "object": "HP:001"}]
    cells = _build_cells(docs, column_map, config)
    assert cells["CASE:001:HP:001"].qualifiers is None


def test_build_cells_negated():
    config = get_grid_config("case-phenotype")
    column_map = {"CASE:001": GridColumnEntity(id="CASE:001", category="biolink:Case", is_direct=True)}
    docs = [{"subject": "CASE:001", "object": "HP:001", "negated": True}]
    cells = _build_cells(docs, column_map, config)
    assert cells["CASE:001:HP:001"].negated is True


def test_build_cells_skips_missing_ids():
    config = get_grid_config("case-phenotype")
    column_map = {"CASE:001": GridColumnEntity(id="CASE:001", category="biolink:Case", is_direct=True)}
    docs = [{"subject": "CASE:001"}, {"object": "HP:001"}]
    cells = _build_cells(docs, column_map, config)
    assert len(cells) == 0


def test_build_cells_skips_unknown_column():
    config = get_grid_config("case-phenotype")
    column_map = {"CASE:001": GridColumnEntity(id="CASE:001", category="biolink:Case", is_direct=True)}
    docs = [{"subject": "CASE:999", "object": "HP:001"}]
    cells = _build_cells(docs, column_map, config)
    assert len(cells) == 0


# =====================================================================
# Tests for _build_bins
# =====================================================================


def test_build_bins_from_facet_counts():
    grouping = RowGroupingConfig(
        grouping_type=GroupingType.CLOSURE_ROOTS,
        bin_ids=["BIN:001", "BIN:002"],
        bin_labels={"BIN:001": "Bin One", "BIN:002": "Bin Two"},
    )
    bins = _build_bins({"BIN:001": 5, "BIN:002": 3}, grouping)
    assert len(bins) == 2
    assert bins[0].id == "BIN:001"
    assert bins[0].label == "Bin One"
    assert bins[0].count == 5
    assert bins[1].count == 3


def test_build_bins_zero_counts():
    grouping = RowGroupingConfig(
        grouping_type=GroupingType.CLOSURE_ROOTS, bin_ids=["BIN:001"], bin_labels={"BIN:001": "Bin 1"}
    )
    bins = _build_bins({}, grouping)
    assert len(bins) == 1
    assert bins[0].count == 0


def test_build_bins_id_as_label_fallback():
    grouping = RowGroupingConfig(grouping_type=GroupingType.CLOSURE_ROOTS, bin_ids=["BIN:001"], bin_labels={})
    bins = _build_bins({"BIN:001": 1}, grouping)
    assert bins[0].label == "BIN:001"


# =====================================================================
# Tests for build_entity_grid
# =====================================================================


def test_build_entity_grid_complete():
    config = get_grid_config("case-phenotype")
    grouping = RowGroupingConfig(
        grouping_type=GroupingType.CLOSURE_ROOTS, bin_ids=["BIN:001"], bin_labels={"BIN:001": "Bin 1"}
    )

    column_docs = [
        {"subject": "CASE:001", "subject_label": "Case 1", "object": "MONDO:0007078", "object_label": "Achondroplasia"}
    ]
    row_docs = [
        {
            "subject": "CASE:001",
            "object": "HP:001",
            "object_label": "Phenotype 1",
            "object_closure": ["BIN:001", "HP:001"],
        }
    ]

    grid = build_entity_grid(
        context_id="MONDO:0007078",
        context_name="Achondroplasia",
        context_category="biolink:Disease",
        config=config,
        grouping=grouping,
        column_docs=column_docs,
        row_docs=row_docs,
        facets=facets_for({"BIN:001": ["HP:001"]}, grouping.bin_ids),
    )

    assert isinstance(grid, EntityGridResponse)
    assert grid.context_id == "MONDO:0007078"
    assert grid.total_columns == 1
    assert grid.total_rows == 1
    assert len(grid.bins) == 1
    assert "CASE:001:HP:001" in grid.cells


def test_build_entity_grid_empty():
    config = get_grid_config("case-phenotype")
    grouping = RowGroupingConfig(
        grouping_type=GroupingType.CLOSURE_ROOTS, bin_ids=["BIN:001"], bin_labels={"BIN:001": "Bin 1"}
    )

    grid = build_entity_grid(
        context_id="MONDO:0007078",
        context_name="Achondroplasia",
        context_category="biolink:Disease",
        config=config,
        grouping=grouping,
        column_docs=[],
        row_docs=[],
        facets={},
    )

    assert grid.total_columns == 0
    assert grid.total_rows == 0
    assert len(grid.cells) == 0
