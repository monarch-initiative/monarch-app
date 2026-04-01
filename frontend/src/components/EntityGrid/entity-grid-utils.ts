/** Utility functions for EntityGrid component */

import type {
  CellData,
  ColumnEntity,
  ColumnGroup,
  EntityGridMatrix,
  RowBin,
} from "@/api/entity-grid/types";

/**
 * Generate a cell key from column and row IDs
 *
 * @param columnId - The column entity ID
 * @param rowId - The row entity ID
 * @returns The cell key in format "columnId:rowId"
 */
export function getCellKey(columnId: string, rowId: string): string {
  return `${columnId}:${rowId}`;
}

/**
 * Parse a cell key back into column and row IDs
 *
 * @param cellKey - The cell key in format "columnId:rowId"
 * @returns Object with columnId and rowId
 */
export function parseCellKey(cellKey: string): {
  columnId: string;
  rowId: string;
} {
  const [columnId, rowId] = cellKey.split(":");
  return { columnId, rowId };
}

/**
 * Get a summary of cell data for a specific bin and column. Used for collapsed
 * bin rows to show aggregate information.
 *
 * @param matrix - The entity grid matrix
 * @param binId - The bin ID to summarize
 * @param columnId - The column ID to summarize
 * @returns Object with presentCount, negatedCount, and total
 */
export function getBinCellSummary(
  matrix: EntityGridMatrix,
  binId: string,
  columnId: string,
): { presentCount: number; negatedCount: number; total: number } {
  // Find the bin
  const bin = matrix.bins.find((b: RowBin) => b.id === binId);
  if (!bin) {
    return { presentCount: 0, negatedCount: 0, total: 0 };
  }

  let presentCount = 0;
  let negatedCount = 0;

  for (const rowId of bin.rowEntityIds) {
    const cellKey = getCellKey(columnId, rowId);
    const cellData = matrix.cells.get(cellKey) as CellData | undefined;

    if (cellData) {
      if (cellData.negated) {
        negatedCount++;
      } else if (cellData.hasData) {
        presentCount++;
      }
    }
  }

  return {
    presentCount,
    negatedCount,
    total: presentCount + negatedCount,
  };
}

/**
 * Get all row IDs that have data for a specific column
 *
 * @param matrix - The entity grid matrix
 * @param columnId - The column ID to check
 * @returns Array of row IDs that have data
 */
export function getRowsWithData(
  matrix: EntityGridMatrix,
  columnId: string,
): string[] {
  const rowIds: string[] = [];

  for (const row of matrix.rows) {
    const cellKey = getCellKey(columnId, row.id);
    if (matrix.cells.has(cellKey)) {
      rowIds.push(row.id);
    }
  }

  return rowIds;
}

/**
 * Get all column IDs that have data for a specific row
 *
 * @param matrix - The entity grid matrix
 * @param rowId - The row ID to check
 * @returns Array of column IDs that have data
 */
export function getColumnsWithData(
  matrix: EntityGridMatrix,
  rowId: string,
): string[] {
  const columnIds: string[] = [];

  for (const column of matrix.columns) {
    const cellKey = getCellKey(column.id, rowId);
    if (matrix.cells.has(cellKey)) {
      columnIds.push(column.id);
    }
  }

  return columnIds;
}

// =============================================================================
// Column Grouping Utilities
// =============================================================================

/** Human-readable labels for association categories */
const ASSOCIATION_CATEGORY_LABELS: Record<string, string> = {
  "biolink:CausalGeneToDiseaseAssociation": "Causal",
  "biolink:CorrelatedGeneToDiseaseAssociation": "Correlated",
  "biolink:CaseToDiseaseAssociation": "Cases",
  "biolink:GeneToGeneHomologyAssociation": "Orthologs",
  "biolink:DiseaseToPhenotypicFeatureAssociation": "Disease-Phenotype",
  "biolink:CaseToPhenotypicFeatureAssociation": "Case-Phenotype",
  "biolink:GeneToPhenotypicFeatureAssociation": "Gene-Phenotype",
};

/**
 * Get a human-readable label for an association category.
 *
 * @param category - The full association category URI
 * @returns Human-readable label
 */
export function getAssociationCategoryLabel(category: string): string {
  return (
    ASSOCIATION_CATEGORY_LABELS[category] ||
    category.replace("biolink:", "").replace(/Association$/, "")
  );
}

/**
 * Compute column groups from a list of columns. Groups are determined by
 * sourceAssociationCategory field.
 *
 * @param columns - List of column entities
 * @returns Array of column groups in display order
 */
export function computeColumnGroups(columns: ColumnEntity[]): ColumnGroup[] {
  if (columns.length === 0) {
    return [];
  }

  const groups: ColumnGroup[] = [];
  let currentCategory = columns[0].sourceAssociationCategory || "";
  let startIndex = 0;

  for (let i = 1; i <= columns.length; i++) {
    const col = columns[i];
    const category = col?.sourceAssociationCategory || "";

    if (i === columns.length || category !== currentCategory) {
      // End of current group
      groups.push({
        category: currentCategory,
        label: getAssociationCategoryLabel(currentCategory),
        startIndex,
        endIndex: i,
        count: i - startIndex,
      });

      if (i < columns.length) {
        currentCategory = category;
        startIndex = i;
      }
    }
  }

  return groups;
}

/**
 * Get the column indices where group boundaries occur. Used for drawing visual
 * separators between column groups.
 *
 * @param groups - Column groups computed by computeColumnGroups
 * @returns Set of column indices where separators should be drawn
 */
export function getColumnGroupBoundaries(groups: ColumnGroup[]): Set<number> {
  const boundaries = new Set<number>();

  // Add boundaries at the end of each group (except the last)
  for (let i = 0; i < groups.length - 1; i++) {
    boundaries.add(groups[i].endIndex);
  }

  return boundaries;
}

/**
 * Determine if a column index is at a group boundary.
 *
 * @param columnIndex - The column index to check
 * @param boundaries - Set of boundary indices from getColumnGroupBoundaries
 * @returns True if this column is followed by a boundary
 */
export function isColumnAtBoundary(
  columnIndex: number,
  boundaries: Set<number>,
): boolean {
  return boundaries.has(columnIndex + 1);
}
