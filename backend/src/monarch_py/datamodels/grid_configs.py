"""Grid type configurations for entity grids.

This module defines the configuration for each type of entity grid,
specifying the 2-hop traversal pattern from context entity to row entities.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from monarch_py.datamodels.category_enums import AssociationCategory, EntityCategory


@dataclass
class GridTypeConfig:
    """Configuration for a specific grid type.

    Defines the 2-hop traversal pattern:
    1. Context Entity -> Column Entities (via column_assoc_category/categories)
    2. Column Entities -> Row Entities (via row_assoc_category)

    Attributes:
        name: Human-readable name for the grid type
        context_category: Expected category of the context entity
        column_assoc_category: Single association category (backwards compat)
        column_assoc_categories: List of association categories for context -> column
        row_assoc_category: Association category for column -> row hop
        row_entity_category: Category of row entities (for grouping lookup)
        column_entity_category: Category of column entities
        context_field: Field in column associations containing context ID
        column_field: Field in column associations containing column entity ID
        row_context_field: Field in row associations to join on (column entity)
        row_entity_field: Field in row associations containing row entity ID
        context_closure_field: Field for indirect context matching
    """
    name: str
    context_category: EntityCategory
    row_assoc_category: AssociationCategory
    row_entity_category: EntityCategory
    column_entity_category: EntityCategory
    # Support both single category (backwards compat) and multiple categories
    column_assoc_category: Optional[AssociationCategory] = None
    column_assoc_categories: Optional[List[AssociationCategory]] = None
    context_field: str = "object"
    column_field: str = "subject"
    row_context_field: str = "subject"
    row_entity_field: str = "object"
    context_closure_field: str = "object_closure"

    def get_column_assoc_categories(self) -> List[AssociationCategory]:
        """Get list of column association categories.

        Returns categories as a list, handling both single and multi-category configs.
        """
        if self.column_assoc_categories:
            return self.column_assoc_categories
        if self.column_assoc_category:
            return [self.column_assoc_category]
        raise ValueError(f"Grid config '{self.name}' has no column association categories defined")


# Registry of grid type configurations
GRID_TYPE_CONFIGS: Dict[str, GridTypeConfig] = {
    # Disease -> Case × Phenotype
    # Context: Disease, Columns: Cases, Rows: Phenotypes
    "case-phenotype": GridTypeConfig(
        name="Case-Phenotype",
        context_category=EntityCategory.DISEASE,
        column_assoc_category=AssociationCategory.CASE_TO_DISEASE_ASSOCIATION,
        row_assoc_category=AssociationCategory.CASE_TO_PHENOTYPIC_FEATURE_ASSOCIATION,
        row_entity_category=EntityCategory.PHENOTYPIC_FEATURE,
        column_entity_category=EntityCategory.CASE,
        context_field="object",
        column_field="subject",
        row_context_field="subject",
        row_entity_field="object",
        context_closure_field="object_closure",
    ),
    # Gene -> Disease × Phenotype
    # Context: Gene, Columns: Diseases, Rows: Phenotypes
    "disease-phenotype": GridTypeConfig(
        name="Disease-Phenotype",
        context_category=EntityCategory.GENE,
        column_assoc_category=AssociationCategory.CAUSAL_GENE_TO_DISEASE_ASSOCIATION,
        row_assoc_category=AssociationCategory.DISEASE_TO_PHENOTYPIC_FEATURE_ASSOCIATION,
        row_entity_category=EntityCategory.PHENOTYPIC_FEATURE,
        column_entity_category=EntityCategory.DISEASE,
        context_field="subject",
        column_field="object",
        row_context_field="subject",
        row_entity_field="object",
        context_closure_field="subject_closure",
    ),
    # Gene -> Ortholog × Phenotype
    # Context: Gene, Columns: Orthologs, Rows: Phenotypes
    "ortholog-phenotype": GridTypeConfig(
        name="Ortholog-Phenotype",
        context_category=EntityCategory.GENE,
        column_assoc_category=AssociationCategory.GENE_TO_GENE_HOMOLOGY_ASSOCIATION,
        row_assoc_category=AssociationCategory.GENE_TO_PHENOTYPIC_FEATURE_ASSOCIATION,
        row_entity_category=EntityCategory.PHENOTYPIC_FEATURE,
        column_entity_category=EntityCategory.GENE,
        context_field="subject",
        column_field="object",
        row_context_field="subject",
        row_entity_field="object",
        context_closure_field="subject_closure",
    ),
}


def get_grid_config(grid_type: str) -> GridTypeConfig:
    """Get the configuration for a grid type.

    Args:
        grid_type: The grid type identifier

    Returns:
        GridTypeConfig for the grid type

    Raises:
        ValueError: If no configuration exists for the grid type
    """
    if grid_type not in GRID_TYPE_CONFIGS:
        raise ValueError(
            f"Unknown grid type: {grid_type}. "
            f"Available types: {list(GRID_TYPE_CONFIGS.keys())}"
        )
    return GRID_TYPE_CONFIGS[grid_type]
