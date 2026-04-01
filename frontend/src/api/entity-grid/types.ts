/**
 * Generic types for Entity × Grouped-Class Grid visualization. These are
 * UI-specific types for the EntityGrid component.
 */

import type { ExpandedCurie } from "../model";

// =============================================================================
// Core Generic Types
// =============================================================================

/**
 * Represents a column entity in the grid (e.g., case, disease, ortholog).
 * Extended by use-case specific types.
 */
export interface ColumnEntity {
  id: string;
  label?: string;
  fullId?: string;
  /** True if directly associated with the context entity (not via descendants) */
  isDirect?: boolean;
  taxonId?: string;
  taxonLabel?: string;
  /** ID of the source entity this column is associated with */
  sourceEntityId?: string;
  /** Label of the source entity for tooltip display */
  sourceEntityLabel?: string;
  // Source association fields (context -> column)
  /**
   * Association category of the source association (e.g.,
   * "biolink:CausalGeneToDiseaseAssociation")
   */
  sourceAssociationCategory?: string;
  /** Predicate of the source association (e.g., "biolink:causes") */
  sourceAssociationPredicate?: string;
  /** Publication CURIEs supporting the source association */
  sourceAssociationPublications?: string[];
  /** Number of evidence items supporting the source association */
  sourceAssociationEvidenceCount?: number;
  /** Primary knowledge source for the source association */
  sourceAssociationPrimaryKnowledgeSource?: string;
  metadata?: Record<string, unknown>;
}

/** Represents a row entity in the grid (e.g., phenotype, anatomy term, GO term). */
export interface RowEntity {
  id: string;
  label?: string;
  /** ID of the bin this row belongs to */
  binId: string;
  metadata?: Record<string, unknown>;
}

/** Represents a grouping bin for row entities (e.g., body system, slim term). */
export interface RowBin {
  id: string;
  label: string;
  /** IDs of row entities in this bin */
  rowEntityIds: string[];
  /** Number of row entities in this bin */
  count: number;
  /** UI state: whether this bin is expanded to show individual rows */
  expanded?: boolean;
}

/** Qualifier attached to a cell (e.g., onset, frequency, severity). */
export interface CellQualifier {
  type: "onset" | "frequency" | "severity" | "sex" | "stage" | string;
  id?: string;
  label: string;
}

/**
 * Represents data for a single cell in the grid. Extended by use-case specific
 * types for additional fields.
 */
export interface CellData {
  hasData: boolean;
  count?: number;
  negated?: boolean;
  qualifiers?: CellQualifier[];
  publications?: string[];
  publicationLinks?: ExpandedCurie[];
  source?: string;
  details?: Record<string, unknown>;
}

/**
 * Generic matrix structure for entity grid visualization.
 *
 * @template TColumn - Type of column entities
 * @template TRow - Type of row entities
 * @template TCell - Type of cell data
 */
export interface EntityGridMatrix<
  TColumn extends ColumnEntity = ColumnEntity,
  TRow extends RowEntity = RowEntity,
  TCell extends CellData = CellData,
> {
  /** ID of the context entity (e.g., disease ID, gene ID) */
  contextId: string;
  /** Name of the context entity */
  contextName?: string;
  /** Column entities */
  columns: TColumn[];
  /** Row grouping bins */
  bins: RowBin[];
  /** Row entities */
  rows: TRow[];
  /** Cell data map, keyed by "columnId:rowId" */
  cells: Map<string, TCell>;
  /** Total number of columns */
  totalColumns: number;
  /** Total number of rows */
  totalRows: number;
}

// =============================================================================
// Grid Display Configuration
// =============================================================================

/** Configuration for grid display and behavior. */
export interface EntityGridConfig {
  /** Singular label for columns (e.g., "Case", "Disease") */
  columnLabel: string;
  /** Plural label for columns (e.g., "Cases", "Diseases") */
  columnLabelPlural: string;
  /** Singular label for rows (e.g., "Phenotype", "Anatomy") */
  rowLabel: string;
  /** Plural label for rows (e.g., "Phenotypes", "Anatomy terms") */
  rowLabelPlural: string;
  /** Label for bin groupings (e.g., "Body System", "Slim term") */
  binLabel: string;
  /** Custom tooltip formatter for column headers */
  columnTooltipFormatter?: (column: ColumnEntity, index: number) => string;
  /** Custom tooltip formatter for cells */
  cellTooltipFormatter?: (
    column: ColumnEntity,
    row: RowEntity,
    cell: CellData | null,
  ) => string;
  /** How to display cell values */
  cellDisplayMode: "binary" | "count" | "percentage";
  /** Whether to show negated/excluded cells with distinct styling */
  showNegated: boolean;
  // Display mode options
  /** How to display column headers */
  columnDisplayMode?: "numeric" | "labeled";
  /** Angle for diagonal column labels (degrees, default 45) */
  columnLabelAngle?: number;
  /** Whether to show visual separators between column groups */
  showColumnGroupSeparators?: boolean;
}

// =============================================================================
// Column Grouping Types
// =============================================================================

/** Represents a group of columns with the same source association category. */
export interface ColumnGroup {
  /** The association category for this group */
  category: string;
  /** Human-readable label for the category */
  label: string;
  /** Starting column index (0-based) */
  startIndex: number;
  /** Ending column index (exclusive) */
  endIndex: number;
  /** Number of columns in the group */
  count: number;
}

// =============================================================================
// Bin Definitions
// =============================================================================

/** HistoPheno bin IDs mapped to human-readable labels */
export const HISTOPHENO_BINS: Record<string, string> = {
  "UPHENO:0002964": "Skeletal System",
  "UPHENO:0004523": "Nervous System",
  "UPHENO:0002764": "Head and Neck",
  "UPHENO:0002635": "Integument",
  "UPHENO:0003020": "Eye",
  "UPHENO:0080362": "Cardiovascular System",
  "HP:0001939": "Metabolism and Homeostasis",
  "UPHENO:0002642": "Genitourinary System",
  "UPHENO:0002833": "Digestive System",
  "HP:0002664": "Neoplasm",
  "UPHENO:0004459": "Blood",
  "UPHENO:0002948": "Immune System",
  "UPHENO:0003116": "Endocrine",
  "UPHENO:0002816": "Musculature",
  "UPHENO:0004536": "Respiratory",
  "HP:0000598": "Ear",
  "UPHENO:0002712": "Connective Tissue",
  "UPHENO:0075949": "Prenatal or Birth",
  "UPHENO:0049874": "Growth",
  "UPHENO:0003013": "Breast",
};

/** Set of all histopheno bin IDs for quick lookup */
export const HISTOPHENO_BIN_IDS = new Set(Object.keys(HISTOPHENO_BINS));
