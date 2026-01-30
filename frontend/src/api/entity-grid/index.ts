/** API client for generic entity grid endpoints */

import { apiUrl } from "@/api";
import type {
  CellData,
  ColumnEntity,
  EntityGridMatrix,
  RowBin,
  RowEntity,
} from "./types";

// =============================================================================
// API Response Types (from backend)
// =============================================================================

interface GridColumnEntityResponse {
  id: string;
  label?: string;
  category: string;
  is_direct: boolean;
  source_id?: string;
  source_label?: string;
  taxon?: string;
  taxon_label?: string;
  source_association_category?: string;
  source_association_predicate?: string;
  source_association_publications?: string[];
  source_association_evidence_count?: number;
  source_association_primary_knowledge_source?: string;
}

interface GridRowEntityResponse {
  id: string;
  label?: string;
  category: string;
  bin_id: string;
}

interface GridBinResponse {
  id: string;
  label: string;
  count: number;
}

interface GridCellDataResponse {
  present: boolean;
  negated?: boolean;
  qualifiers?: Record<string, unknown>;
  publications?: string[];
  evidence_count?: number;
}

interface EntityGridResponse {
  context_id: string;
  context_name?: string;
  context_category: string;
  total_columns: number;
  total_rows: number;
  columns: GridColumnEntityResponse[];
  rows: GridRowEntityResponse[];
  bins: GridBinResponse[];
  cells: Record<string, GridCellDataResponse>;
}

// =============================================================================
// API Parameters
// =============================================================================

export interface GetEntityGridOptions {
  /** Association category/categories for context → column (required) */
  columnAssociationCategory: string[];
  /** Association category/categories for column → row (required) */
  rowAssociationCategory: string[];
  /** How to group rows (default: "histopheno") */
  rowGrouping?: "histopheno" | "none";
  /** Sort columns by association category (default: false) */
  groupColumnsByCategory?: boolean;
  /** Only include direct associations (default: true) */
  direct?: boolean;
  /** Maximum number of column entities (default: 500) */
  limit?: number;
}

// =============================================================================
// Transform Functions
// =============================================================================

function transformColumn(col: GridColumnEntityResponse): ColumnEntity {
  return {
    id: col.id,
    label: col.label,
    isDirect: col.is_direct,
    sourceEntityId: col.source_id,
    sourceEntityLabel: col.source_label,
    taxonId: col.taxon,
    taxonLabel: col.taxon_label,
    sourceAssociationCategory: col.source_association_category,
    sourceAssociationPredicate: col.source_association_predicate,
    sourceAssociationPublications: col.source_association_publications,
    sourceAssociationEvidenceCount: col.source_association_evidence_count,
    sourceAssociationPrimaryKnowledgeSource:
      col.source_association_primary_knowledge_source,
  };
}

function transformRow(row: GridRowEntityResponse): RowEntity {
  return {
    id: row.id,
    label: row.label,
    binId: row.bin_id,
  };
}

function transformBin(bin: GridBinResponse, rows: RowEntity[]): RowBin {
  // Find all rows in this bin
  const rowEntityIds = rows.filter((r) => r.binId === bin.id).map((r) => r.id);

  return {
    id: bin.id,
    label: bin.label,
    rowEntityIds,
    count: bin.count,
    expanded: false,
  };
}

function transformCell(cell: GridCellDataResponse): CellData {
  return {
    hasData: cell.present || cell.negated || false,
    negated: cell.negated,
    publications: cell.publications,
    details: {
      present: cell.present,
      qualifiers: cell.qualifiers,
      evidenceCount: cell.evidence_count,
    },
  };
}

function transformResponse(response: EntityGridResponse): EntityGridMatrix {
  const columns = response.columns.map(transformColumn);
  const rows = response.rows.map(transformRow);
  const bins = response.bins.map((bin) => transformBin(bin, rows));

  // Transform cells from object to Map
  const cells = new Map<string, CellData>();
  if (response.cells) {
    for (const [key, cellData] of Object.entries(response.cells)) {
      cells.set(key, transformCell(cellData));
    }
  }

  return {
    contextId: response.context_id,
    contextName: response.context_name,
    columns,
    bins,
    rows,
    cells,
    totalColumns: response.total_columns,
    totalRows: response.total_rows,
  };
}

// =============================================================================
// API Functions
// =============================================================================

/**
 * Fetch a generic entity grid with configurable association categories.
 *
 * @param contextId - The context entity ID (e.g., gene ID, disease ID)
 * @param options - Grid configuration options
 * @returns Promise resolving to the entity grid matrix
 * @throws Error if the API request fails
 */
export async function getEntityGrid(
  contextId: string,
  options: GetEntityGridOptions,
): Promise<EntityGridMatrix> {
  const params = new URLSearchParams();

  // Add column association categories (can be multiple)
  for (const cat of options.columnAssociationCategory) {
    params.append("column_association_category", cat);
  }

  // Add row association categories (can be multiple)
  for (const cat of options.rowAssociationCategory) {
    params.append("row_association_category", cat);
  }

  if (options.rowGrouping) {
    params.append("row_grouping", options.rowGrouping);
  }

  if (options.groupColumnsByCategory !== undefined) {
    params.append(
      "group_columns_by_category",
      String(options.groupColumnsByCategory),
    );
  }

  if (options.direct !== undefined) {
    params.append("direct", String(options.direct));
  }

  if (options.limit !== undefined) {
    params.append("limit", String(options.limit));
  }

  const url = `${apiUrl}/entity-grid/${encodeURIComponent(contextId)}?${params}`;

  const response = await fetch(url);

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API error (${response.status}): ${errorText}`);
  }

  const data: EntityGridResponse = await response.json();
  return transformResponse(data);
}

// Re-export types from types.ts
export type { EntityGridConfig, ColumnGroup } from "./types";
// Note: EntityGridMatrix, ColumnEntity, RowEntity, RowBin, CellData are imported from types.ts
// GetEntityGridOptions is defined in this file
