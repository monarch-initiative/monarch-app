"""Row grouping configurations for entity grids.

This module defines how row entities (phenotypes, diseases, anatomy, etc.)
are grouped into bins for display in entity grids.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from monarch_py.datamodels.solr import HistoPhenoKeys, HISTOPHENO_BIN_LABELS


class GroupingType(Enum):
    """Type of grouping mechanism for row entities."""
    CLOSURE_ROOTS = "closure_roots"
    # All Alliance slims (HistoPheno, DO_AGR, UBERON, GO) use closure-based matching:
    # Check if any bin ID appears in the entity's object_closure field


@dataclass
class RowGroupingConfig:
    """Configuration for how to group row entities into bins.

    Attributes:
        grouping_type: The type of grouping mechanism to use
        bin_ids: Ordered list of bin IDs (determines display order)
        bin_labels: Mapping of bin IDs to human-readable labels
    """
    grouping_type: GroupingType
    bin_ids: List[str]
    bin_labels: Dict[str, str]


# Registry mapping row entity categories to their grouping configuration
ROW_GROUPING_REGISTRY: Dict[str, RowGroupingConfig] = {
    # Phenotypes: Use HistoPheno (closure-based) - 20 body system bins
    "biolink:PhenotypicFeature": RowGroupingConfig(
        grouping_type=GroupingType.CLOSURE_ROOTS,
        bin_ids=[k.value for k in HistoPhenoKeys],
        bin_labels=HISTOPHENO_BIN_LABELS,
    ),
    # Future groupings can be added here:
    # "biolink:Disease": RowGroupingConfig(...),  # DO_AGR_slim
    # "biolink:AnatomicalEntity": RowGroupingConfig(...),  # UBERON AGR slim
    # "biolink:BiologicalProcess": RowGroupingConfig(...),  # GO slim BP
    # "biolink:MolecularActivity": RowGroupingConfig(...),  # GO slim MF
    # "biolink:CellularComponent": RowGroupingConfig(...),  # GO slim CC
}


def get_row_grouping(row_category: str) -> RowGroupingConfig:
    """Get the grouping configuration for a row entity category.

    Args:
        row_category: The biolink category of the row entity

    Returns:
        RowGroupingConfig for the category

    Raises:
        ValueError: If no grouping is registered for the category
    """
    if row_category not in ROW_GROUPING_REGISTRY:
        raise ValueError(
            f"No grouping configuration registered for category: {row_category}. "
            f"Available categories: {list(ROW_GROUPING_REGISTRY.keys())}"
        )
    return ROW_GROUPING_REGISTRY[row_category]


def get_bin_label(row_category: str, bin_id: str) -> str:
    """Get the human-readable label for a bin.

    Args:
        row_category: The biolink category of the row entity
        bin_id: The bin ID

    Returns:
        Human-readable label for the bin
    """
    grouping = get_row_grouping(row_category)
    return grouping.bin_labels.get(bin_id, bin_id)


def get_empty_grouping() -> RowGroupingConfig:
    """Get an empty grouping configuration (no binning).

    Returns:
        RowGroupingConfig with no bins, suitable for flat display
    """
    return RowGroupingConfig(
        grouping_type=GroupingType.CLOSURE_ROOTS,
        bin_ids=[],
        bin_labels={},
    )
