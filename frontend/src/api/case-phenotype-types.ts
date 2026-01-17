/**
 * Types for Case-Phenotype Grid visualization These are UI-specific types,
 * separate from the LinkML-generated model.ts
 */

import type { ExpandedCurie } from "./model";

export interface CaseEntity {
  id: string;
  label?: string;
  fullId?: string;
}

export interface HistoPhenoBin {
  id: string; // UPHENO/HP ID
  label: string; // Human-readable label
  phenotypeIds: string[];
  expanded: boolean;
  count: number;
}

export interface CasePhenotype {
  id: string;
  label?: string;
  binId: string;
}

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

export interface CasePhenotypeMatrix {
  diseaseId: string;
  diseaseName?: string;
  cases: CaseEntity[];
  bins: HistoPhenoBin[];
  phenotypes: CasePhenotype[];
  cells: Map<string, CasePhenotypeCellData>; // key: "caseId:phenotypeId"
  totalCases: number;
  totalPhenotypes: number;
}

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
