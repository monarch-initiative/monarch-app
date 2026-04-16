/** API client for generic entity grid endpoints */

import { apiUrl } from "@/api";
import type {
  EntityGridResponse,
  GridBin,
  GridCellData,
  GridColumnEntity,
  GridRowEntity,
} from "@/api/model";
import type {
  CellData,
  CellQualifier,
  ColumnEntity,
  EntityGridMatrix,
  RowBin,
  RowEntity,
} from "./types";

// =============================================================================
// API Parameters
// =============================================================================

export interface GetEntityGridOptions {
  /** Association category/categories for context → column (required) */
  columnAssociationCategory: string[];
  /** Association category/categories for column → row (required) */
  rowAssociationCategory: string[];
  /** Optional predicate filter(s) for context → column associations */
  columnPredicate?: string[];
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

function transformColumn(col: GridColumnEntity): ColumnEntity {
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

function transformRow(row: GridRowEntity): RowEntity {
  return {
    id: row.id,
    label: row.label,
    binId: row.bin_id,
  };
}

function transformBin(bin: GridBin, rows: RowEntity[]): RowBin {
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

function transformCell(cell: GridCellData): CellData {
  // Parse qualifiers from the backend response into CellQualifier[] for the modal
  const qualifiers: CellQualifier[] = [];
  if (cell.qualifiers) {
    for (const [key, qual] of Object.entries(cell.qualifiers)) {
      if (qual != null) {
        qualifiers.push({
          type: key,
          id: qual.value,
          label: qual.label || qual.value || key,
        });
      }
    }
  }

  // Build publicationLinks fallback from raw CURIEs so the modal can display them
  const publicationLinks =
    cell.publications?.map((curie) => ({ id: curie, url: "" })) ?? undefined;

  return {
    hasData: cell.present || cell.negated || false,
    negated: cell.negated,
    publications: cell.publications,
    publicationLinks,
    qualifiers: qualifiers.length > 0 ? qualifiers : undefined,
    details: {
      present: cell.present,
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

  // Add column predicate filters (can be multiple)
  if (options.columnPredicate) {
    for (const pred of options.columnPredicate) {
      params.append("column_predicate", pred);
    }
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

// =============================================================================
// Traversable Associations API
// =============================================================================

/**
 * Represents an association type that can be traversed from a given entity
 * category.
 */
export interface TraversableAssociation {
  /**
   * The biolink association category (e.g.,
   * "biolink:CausalGeneToDiseaseAssociation")
   */
  category: string;
  /** Human-readable label for UI display */
  label: string;
  /** Which field the context entity occupies ("subject" or "object") */
  contextField: "subject" | "object";
  /** The biolink category of entities at the other end of the association */
  targetCategory: string;
}

/**
 * Fetch associations that can be traversed from a given entity category.
 *
 * This enables dynamic UI that shows only valid association options based on
 * the selected entity type, supporting bidirectional traversal.
 *
 * @param entityCategory - The biolink category of the context entity (e.g.,
 *   "biolink:Gene")
 * @returns Promise resolving to list of traversable associations
 * @throws Error if the API request fails or no associations found
 */
export async function getTraversableAssociations(
  entityCategory: string,
): Promise<TraversableAssociation[]> {
  const url = `${apiUrl}/entity-grid/traversable-associations/${encodeURIComponent(entityCategory)}`;

  const response = await fetch(url);

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API error (${response.status}): ${errorText}`);
  }

  const data = await response.json();

  // Transform snake_case to camelCase
  return data.map(
    (item: {
      category: string;
      label: string;
      context_field: string;
      target_category: string;
    }) => ({
      category: item.category,
      label: item.label,
      contextField: item.context_field as "subject" | "object",
      targetCategory: item.target_category,
    }),
  );
}

// Re-export types from types.ts
export type { EntityGridConfig, ColumnGroup } from "./types";
// Note: EntityGridMatrix, ColumnEntity, RowEntity, RowBin, CellData are imported from types.ts
// GetEntityGridOptions is defined in this file
