/**
 * Types for Case-Phenotype Grid visualization.
 * These are UI-specific types, separate from the LinkML-generated model.ts.
 *
 * Note: Generic types are available in '@/api/entity-grid/types' for new use cases.
 */

import type { ExpandedCurie } from "./model";

// Re-export generic types for new code
export {
  type ColumnEntity,
  type RowEntity,
  type RowBin,
  type CellData,
  type CellQualifier,
  type EntityGridMatrix,
  type EntityGridConfig,
  HISTOPHENO_BINS,
  HISTOPHENO_BIN_IDS,
} from "./entity-grid/types";

/**
 * Case entity for case-phenotype grid (column in the grid).
 */
export interface CaseEntity {
  id: string;
  label?: string;
  fullId?: string;
  /** The actual disease ID this case is associated with */
  sourceDiseaseId?: string;
  /** The disease label for tooltip display */
  sourceDiseaseLabel?: string;
  /** True if directly associated with the queried disease (not via descendants) */
  isDirect?: boolean;
}

/**
 * HistoPheno bin for grouping phenotypes by body system.
 */
export interface HistoPhenoBin {
  id: string;
  label: string;
  phenotypeIds: string[];
  expanded: boolean;
  count: number;
}

/**
 * Phenotype entity for case-phenotype grid (row in the grid).
 */
export interface CasePhenotype {
  id: string;
  label?: string;
  binId: string;
}

/**
 * Cell data for case-phenotype grid.
 */
export interface CasePhenotypeCellData {
  present: boolean;
  negated?: boolean;
  onset?: string;
  onsetId?: string;
  frequency?: string;
  publications?: string[];
  publicationLinks?: ExpandedCurie[];
  source?: string;
}

/**
 * Complete matrix structure for case-phenotype grid visualization.
 */
export interface CasePhenotypeMatrix {
  diseaseId: string;
  diseaseName?: string;
  cases: CaseEntity[];
  bins: HistoPhenoBin[];
  phenotypes: CasePhenotype[];
  cells: Map<string, CasePhenotypeCellData>;
  totalCases: number;
  totalPhenotypes: number;
}
