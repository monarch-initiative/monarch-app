"""Unit tests for entity grid utilities."""

from monarch_py.utils.entity_grid_utils import (
    _build_columns,
    _build_rows,
    _build_cells,
    _build_bins,
    _find_bin_for_entity,
    build_entity_grid,
    make_cell_key,
    sort_columns_by_category,
)
from monarch_py.datamodels.grid_configs import get_grid_config
from monarch_py.datamodels.grid_groupings import RowGroupingConfig, GroupingType
from monarch_py.datamodels.model import GridColumnEntity, EntityGridResponse
from monarch_py.implementations.solr.solr_query_utils import (
    build_grid_column_query,
    build_grid_row_query,
    build_multi_category_column_query,
    build_multi_category_row_query,
)


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
# Tests for _find_bin_for_entity
# =====================================================================


def test_find_bin_returns_matching():
    assert (
        _find_bin_for_entity(["HP:root", "BIN:001", "HP:child"], {"BIN:001", "BIN:002"}, ["BIN:001", "BIN:002"])
        == "BIN:001"
    )


def test_find_bin_returns_none_when_no_match():
    assert _find_bin_for_entity(["HP:root", "HP:child"], {"BIN:001", "BIN:002"}, ["BIN:001", "BIN:002"]) is None


def test_find_bin_returns_first_ordered_when_multiple():
    assert _find_bin_for_entity(["BIN:002", "BIN:001"], {"BIN:001", "BIN:002"}, ["BIN:002", "BIN:001"]) == "BIN:002"


def test_find_bin_empty_closure():
    assert _find_bin_for_entity([], {"BIN:001"}, ["BIN:001"]) is None


def test_find_bin_empty_bin_ids():
    assert _find_bin_for_entity(["HP:root", "BIN:001"], set(), []) is None


# =====================================================================
# Tests for _build_rows
# =====================================================================


def test_build_rows_from_docs():
    config = get_grid_config("case-phenotype")
    grouping = RowGroupingConfig(
        grouping_type=GroupingType.CLOSURE_ROOTS,
        bin_ids=["BIN:001", "BIN:002"],
        bin_labels={"BIN:001": "Bin 1", "BIN:002": "Bin 2"},
    )
    docs = [
        {
            "object": "HP:001",
            "object_label": "Phenotype 1",
            "object_closure": ["HP:root", "BIN:001", "HP:001"],
            "subject": "CASE:001",
        },
        {
            "object": "HP:002",
            "object_label": "Phenotype 2",
            "object_closure": ["HP:root", "BIN:002", "HP:002"],
            "subject": "CASE:001",
        },
    ]
    rows = _build_rows(docs, config, grouping)
    assert len(rows) == 2
    assert rows[0].id == "HP:001"
    assert rows[0].bin_id == "BIN:001"
    assert rows[1].id == "HP:002"
    assert rows[1].bin_id == "BIN:002"


def test_build_rows_deduplicates():
    config = get_grid_config("case-phenotype")
    grouping = RowGroupingConfig(
        grouping_type=GroupingType.CLOSURE_ROOTS, bin_ids=["BIN:001"], bin_labels={"BIN:001": "Bin 1"}
    )
    docs = [
        {"object": "HP:001", "object_label": "P1", "object_closure": ["BIN:001"], "subject": "CASE:001"},
        {"object": "HP:001", "object_label": "P1", "object_closure": ["BIN:001"], "subject": "CASE:002"},
    ]
    rows = _build_rows(docs, config, grouping)
    assert len(rows) == 1


def test_build_rows_skips_no_bin_match():
    config = get_grid_config("case-phenotype")
    grouping = RowGroupingConfig(
        grouping_type=GroupingType.CLOSURE_ROOTS, bin_ids=["BIN:001"], bin_labels={"BIN:001": "Bin 1"}
    )
    docs = [{"object": "HP:001", "object_label": "P1", "object_closure": ["HP:root"], "subject": "CASE:001"}]
    rows = _build_rows(docs, config, grouping)
    assert len(rows) == 0


def test_build_rows_skips_missing_row_id():
    config = get_grid_config("case-phenotype")
    grouping = RowGroupingConfig(
        grouping_type=GroupingType.CLOSURE_ROOTS, bin_ids=["BIN:001"], bin_labels={"BIN:001": "Bin 1"}
    )
    docs = [{"subject": "CASE:001", "object_closure": ["BIN:001"]}]
    rows = _build_rows(docs, config, grouping)
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
    config = get_grid_config("case-phenotype")
    grouping = RowGroupingConfig(
        grouping_type=GroupingType.CLOSURE_ROOTS,
        bin_ids=["BIN:001", "BIN:002"],
        bin_labels={"BIN:001": "Bin One", "BIN:002": "Bin Two"},
    )
    facet_counts = {'object_closure:"BIN:001"': 5, 'object_closure:"BIN:002"': 3}
    bins = _build_bins(facet_counts, grouping, config)
    assert len(bins) == 2
    assert bins[0].id == "BIN:001"
    assert bins[0].label == "Bin One"
    assert bins[0].count == 5
    assert bins[1].count == 3


def test_build_bins_zero_counts():
    config = get_grid_config("case-phenotype")
    grouping = RowGroupingConfig(
        grouping_type=GroupingType.CLOSURE_ROOTS, bin_ids=["BIN:001"], bin_labels={"BIN:001": "Bin 1"}
    )
    bins = _build_bins({}, grouping, config)
    assert len(bins) == 1
    assert bins[0].count == 0


def test_build_bins_id_as_label_fallback():
    config = get_grid_config("case-phenotype")
    grouping = RowGroupingConfig(grouping_type=GroupingType.CLOSURE_ROOTS, bin_ids=["BIN:001"], bin_labels={})
    bins = _build_bins({'object_closure:"BIN:001"': 1}, grouping, config)
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
    facet_counts = {'object_closure:"BIN:001"': 1}

    grid = build_entity_grid(
        context_id="MONDO:0007078",
        context_name="Achondroplasia",
        context_category="biolink:Disease",
        config=config,
        grouping=grouping,
        column_docs=column_docs,
        row_docs=row_docs,
        facet_counts=facet_counts,
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
        facet_counts={},
    )

    assert grid.total_columns == 0
    assert grid.total_rows == 0
    assert len(grid.cells) == 0


# =====================================================================
# Tests for predicate filtering in query builders
# =====================================================================


def test_build_grid_column_query_without_predicate():
    """Column query without predicate should not include predicate filter."""
    config = get_grid_config("case-phenotype")
    result = build_grid_column_query("MONDO:0007078", config, direct_only=True)
    # fq should not contain any predicate filter
    fq_str = str(result["fq"])
    assert "predicate:" not in fq_str


def test_build_grid_column_query_with_config_predicate():
    """Column query should include predicate from config.column_predicate."""
    config = get_grid_config("child-disease-phenotype")
    result = build_grid_column_query("MONDO:0021060", config, direct_only=True)
    fq_str = str(result["fq"])
    assert 'predicate:"biolink:subclass_of"' in fq_str


def test_build_grid_column_query_with_explicit_predicate():
    """Column query should include explicitly passed predicates."""
    config = get_grid_config("case-phenotype")
    result = build_grid_column_query(
        "MONDO:0007078", config, direct_only=True,
        column_predicates=["biolink:has_phenotype"],
    )
    fq_str = str(result["fq"])
    assert 'predicate:"biolink:has_phenotype"' in fq_str


def test_build_grid_row_query_without_predicate():
    """Row query without predicate should not include predicate in JOIN."""
    config = get_grid_config("case-phenotype")
    grouping = RowGroupingConfig(
        grouping_type=GroupingType.CLOSURE_ROOTS, bin_ids=["BIN:001"], bin_labels={"BIN:001": "Bin 1"},
    )
    result = build_grid_row_query("MONDO:0007078", config, grouping, direct_only=True)
    assert "predicate:" not in result["q"]


def test_build_grid_row_query_with_config_predicate():
    """Row query should include predicate from config.column_predicate in JOIN."""
    config = get_grid_config("child-disease-phenotype")
    grouping = RowGroupingConfig(
        grouping_type=GroupingType.CLOSURE_ROOTS, bin_ids=["BIN:001"], bin_labels={"BIN:001": "Bin 1"},
    )
    result = build_grid_row_query("MONDO:0021060", config, grouping, direct_only=True)
    assert 'predicate:"biolink:subclass_of"' in result["q"]


def test_build_multi_category_column_query_with_predicate():
    """Multi-category column query should include predicate filter."""
    result = build_multi_category_column_query(
        context_id="MONDO:0021060",
        column_assoc_categories=["biolink:Association"],
        context_field="object",
        context_closure_field="object_closure",
        column_field="subject",
        direct_only=True,
        column_predicates=["biolink:subclass_of"],
    )
    fq_str = str(result["fq"])
    assert 'predicate:"biolink:subclass_of"' in fq_str


def test_build_multi_category_column_query_without_predicate():
    """Multi-category column query without predicate should not filter."""
    result = build_multi_category_column_query(
        context_id="MONDO:0021060",
        column_assoc_categories=["biolink:Association"],
        context_field="object",
        context_closure_field="object_closure",
        column_field="subject",
        direct_only=True,
    )
    fq_str = str(result["fq"])
    assert "predicate:" not in fq_str


def test_build_multi_category_row_query_with_predicate():
    """Multi-category row query should include predicate in JOIN."""
    grouping = RowGroupingConfig(
        grouping_type=GroupingType.CLOSURE_ROOTS, bin_ids=["BIN:001"], bin_labels={"BIN:001": "Bin 1"},
    )
    result = build_multi_category_row_query(
        context_id="MONDO:0021060",
        column_assoc_categories=["biolink:Association"],
        row_assoc_categories=["biolink:DiseaseToPhenotypicFeatureAssociation"],
        context_field="object",
        context_closure_field="object_closure",
        column_field="subject",
        row_context_field="subject",
        row_entity_field="object",
        grouping=grouping,
        direct_only=True,
        column_predicates=["biolink:subclass_of"],
    )
    assert 'predicate:"biolink:subclass_of"' in result["q"]


def test_build_multi_category_row_query_without_predicate():
    """Multi-category row query without predicate should not filter."""
    grouping = RowGroupingConfig(
        grouping_type=GroupingType.CLOSURE_ROOTS, bin_ids=["BIN:001"], bin_labels={"BIN:001": "Bin 1"},
    )
    result = build_multi_category_row_query(
        context_id="MONDO:0021060",
        column_assoc_categories=["biolink:Association"],
        row_assoc_categories=["biolink:DiseaseToPhenotypicFeatureAssociation"],
        context_field="object",
        context_closure_field="object_closure",
        column_field="subject",
        row_context_field="subject",
        row_entity_field="object",
        grouping=grouping,
        direct_only=True,
    )
    assert "predicate:" not in result["q"]
