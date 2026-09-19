"""Utilities for building generic entity grids."""

from typing import Any, Dict, List, Optional

from monarch_py.datamodels.model import (
    EntityGridResponse,
    GridColumnEntity,
    GridRowEntity,
    GridBin,
    GridCellData,
    Qualifier,
)
from monarch_py.datamodels.grid_configs import GridTypeConfig
from monarch_py.datamodels.grid_groupings import RowGroupingConfig, bin_facet_key


def parse_bin_facets(
    facets: Dict[str, Any],
    ordered_bin_ids: List[str],
) -> tuple[Dict[str, int], Dict[str, str]]:
    """Read the grid bin facet into per-bin counts and a row-entity -> bin assignment.

    Replaces deriving bins from a `_closure` field on every row association. The
    closure describes the row entity, not the edge, so fetching it per association
    re-sent the same ancestor lists once per edge.

    A bin with no matches has a count but no `entities` sub-facet, so its absence is
    normal and not an error.

    Returns:
        (bin_id -> association count, row entity ID -> bin ID)
    """
    counts: Dict[str, int] = {}
    entity_bins: Dict[str, str] = {}

    for index, bin_id in enumerate(ordered_bin_ids):
        facet = facets.get(bin_facet_key(index)) or {}
        counts[bin_id] = facet.get("count", 0)
        for bucket in facet.get("entities", {}).get("buckets", []):
            entity_id = bucket.get("val")
            # Bins are checked in grouping order and the first match wins, so an entity
            # under several bins lands in the same one the closure scan used to pick.
            if entity_id and entity_id not in entity_bins:
                entity_bins[entity_id] = bin_id

    return counts, entity_bins


def bin_members(facets: Dict[str, Any], ordered_bin_ids: List[str]) -> Dict[str, List[str]]:
    """Row entity IDs per bin, including entities that fall under more than one bin."""
    members: Dict[str, List[str]] = {}
    for index, bin_id in enumerate(ordered_bin_ids):
        facet = facets.get(bin_facet_key(index)) or {}
        buckets = facet.get("entities", {}).get("buckets", [])
        members[bin_id] = sorted(b["val"] for b in buckets if b.get("val"))
    return members


def build_entity_grid(
    context_id: str,
    context_name: Optional[str],
    context_category: str,
    config: GridTypeConfig,
    grouping: RowGroupingConfig,
    column_docs: List[dict],
    row_docs: List[dict],
    facets: Dict[str, Any],
) -> EntityGridResponse:
    """Build entity grid from Solr documents.

    Args:
        context_id: The context entity ID
        context_name: Human-readable name of the context entity
        context_category: Biolink category of the context entity
        config: Grid type configuration
        grouping: Row grouping configuration
        column_docs: List of column association Solr documents
        row_docs: List of row association Solr documents
        facets: The `facets` block of the row query's JSON Facet response

    Returns:
        EntityGridResponse with columns, rows, bins, and cells
    """
    bin_counts, entity_bins = parse_bin_facets(facets, grouping.bin_ids)

    columns = _build_columns(column_docs, context_id, config)
    column_map = {c.id: c for c in columns}
    rows = _build_rows(row_docs, config, entity_bins)
    cells = _build_cells(row_docs, column_map, config)
    bins = _build_bins(bin_counts, grouping)

    return EntityGridResponse(
        context_id=context_id,
        context_name=context_name,
        context_category=context_category,
        total_columns=len(columns),
        total_rows=len(rows),
        columns=columns,
        rows=rows,
        bins=bins,
        cells=cells,
    )


def _build_columns(
    column_docs: List[dict],
    context_id: str,
    config: GridTypeConfig,
) -> List[GridColumnEntity]:
    """Extract unique column entities from Solr documents.

    Args:
        column_docs: List of column association Solr documents
        context_id: The context entity ID (for direct/indirect determination)
        config: Grid type configuration

    Returns:
        List of GridColumnEntity objects, deduplicated by column ID
    """
    seen_columns: Dict[str, GridColumnEntity] = {}

    for doc in column_docs:
        column_id = doc.get(config.column_field)
        if not column_id or column_id in seen_columns:
            continue

        # Determine if this is a direct association
        context_value = doc.get(config.context_field)
        is_direct = context_value == context_id

        # Get taxon info (field depends on whether column is subject or object)
        if config.column_field == "subject":
            taxon = doc.get("subject_taxon")
            taxon_label = doc.get("subject_taxon_label")
        else:
            taxon = doc.get("object_taxon")
            taxon_label = doc.get("object_taxon_label")

        # Get source association data
        source_assoc_category = doc.get("category")
        source_assoc_predicate = doc.get("predicate")
        source_assoc_publications = doc.get("publications")
        source_assoc_primary_ks = doc.get("primary_knowledge_source")

        # Count evidence if available
        has_evidence = doc.get("has_evidence")
        evidence_count = len(has_evidence) if has_evidence else None

        column = GridColumnEntity(
            id=column_id,
            label=doc.get(f"{config.column_field}_label"),
            category=config.column_entity_category.value,
            is_direct=is_direct,
            source_id=None if is_direct else context_value,
            source_label=None if is_direct else doc.get(f"{config.context_field}_label"),
            taxon=taxon,
            taxon_label=taxon_label,
            source_association_category=source_assoc_category,
            source_association_predicate=source_assoc_predicate,
            source_association_publications=source_assoc_publications,
            source_association_evidence_count=evidence_count,
            source_association_primary_knowledge_source=source_assoc_primary_ks,
        )
        seen_columns[column_id] = column

    return list(seen_columns.values())


def sort_columns_by_category(
    columns: List[GridColumnEntity],
    category_order: List[str],
) -> List[GridColumnEntity]:
    """Sort columns by their source association category.

    Args:
        columns: List of column entities to sort
        category_order: Ordered list of category values (first = highest priority)

    Returns:
        New list of columns sorted by category, preserving order within category
    """
    if not columns or not category_order:
        return columns

    # Create a mapping of category to sort index
    category_index = {cat: i for i, cat in enumerate(category_order)}
    default_index = len(category_order)  # Unknown categories go last

    # Store original indices to preserve order within same category
    indexed_columns = list(enumerate(columns))

    def sort_key(item: tuple) -> tuple:
        original_idx, col = item
        cat = col.source_association_category or ""
        return (category_index.get(cat, default_index), original_idx)

    sorted_items = sorted(indexed_columns, key=sort_key)
    return [col for _, col in sorted_items]


def _build_rows(
    row_docs: List[dict],
    config: GridTypeConfig,
    entity_bins: Dict[str, str],
) -> List[GridRowEntity]:
    """Extract unique row entities and assign to bins.

    Args:
        row_docs: List of row association Solr documents
        config: Grid type configuration
        entity_bins: Row entity ID -> bin ID, from `parse_bin_facets`

    Returns:
        List of GridRowEntity objects, deduplicated by row ID. Entities that fall in
        no bin are dropped, as they were when bins came from the closure field.
    """
    seen_rows: Dict[str, GridRowEntity] = {}

    for doc in row_docs:
        row_id = doc.get(config.row_entity_field)
        if not row_id or row_id in seen_rows:
            continue

        bin_id = entity_bins.get(row_id)
        if bin_id is None:
            continue

        row = GridRowEntity(
            id=row_id,
            label=doc.get(f"{config.row_entity_field}_label"),
            category=config.row_entity_category.value,
            bin_id=bin_id,
        )
        seen_rows[row_id] = row

    return list(seen_rows.values())


def _build_cells(
    row_docs: List[dict],
    column_map: Dict[str, GridColumnEntity],
    config: GridTypeConfig,
) -> Dict[str, GridCellData]:
    """Build cell data for each column-row pair.

    Args:
        row_docs: List of row association Solr documents
        column_map: Dict mapping column IDs to GridColumnEntity objects
        config: Grid type configuration

    Returns:
        Dict mapping cell keys (column_id:row_id) to GridCellData
    """
    cells: Dict[str, GridCellData] = {}

    for doc in row_docs:
        column_id = doc.get(config.row_context_field)
        row_id = doc.get(config.row_entity_field)

        if not column_id or not row_id:
            continue
        if column_id not in column_map:
            continue

        cell_key = make_cell_key(column_id, row_id)

        # Build qualifiers dict from available qualifier fields
        qualifiers = {}
        if doc.get("onset_qualifier"):
            qualifiers["onset_qualifier"] = Qualifier(
                id="onset_qualifier",
                value=doc.get("onset_qualifier"),
                label=doc.get("onset_qualifier_label"),
            )

        cell = GridCellData(
            id=cell_key,
            present=True,
            negated=doc.get("negated"),
            qualifiers=qualifiers if qualifiers else None,
            publications=doc.get("publications"),
        )
        cells[cell_key] = cell

    return cells


def _build_bins(
    bin_counts: Dict[str, int],
    grouping: RowGroupingConfig,
) -> List[GridBin]:
    """Build bin list from parsed bin facet counts.

    Args:
        bin_counts: Bin ID -> association count, from `parse_bin_facets`
        grouping: Row grouping configuration

    Returns:
        List of GridBin objects in grouping order
    """
    bins = []

    for bin_id in grouping.bin_ids:
        count = bin_counts.get(bin_id, 0)

        bin_obj = GridBin(
            id=bin_id,
            label=grouping.bin_labels.get(bin_id, bin_id),
            count=count,
        )
        bins.append(bin_obj)

    return bins


def make_cell_key(column_id: str, row_id: str) -> str:
    """Create a cell key for looking up cell data.

    Args:
        column_id: The column entity ID
        row_id: The row entity ID

    Returns:
        Cell key in format "column_id:row_id"
    """
    return f"{column_id}:{row_id}"
