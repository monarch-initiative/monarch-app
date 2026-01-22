/**
 * Utility functions for transforming case-phenotype association data into
 * matrix format
 */

import type {
  CaseEntity,
  CasePhenotype,
  CasePhenotypeCellData,
  CasePhenotypeMatrix,
  HistoPhenoBin,
} from "@/api/case-phenotype-types";
import {
  HISTOPHENO_BIN_IDS,
  HISTOPHENO_BINS,
} from "@/api/case-phenotype-types";
import type { Association } from "@/api/model";

/**
 * Find the appropriate histopheno bin for a phenotype based on its closure
 *
 * @param objectClosure - The closure array from the phenotype association
 * @returns The bin ID if found, or "OTHER" if no match
 */
export function findBinForPhenotype(
  objectClosure: string[] | undefined,
): string {
  if (!objectClosure) {
    return "OTHER";
  }

  for (const id of objectClosure) {
    if (HISTOPHENO_BIN_IDS.has(id)) {
      return id;
    }
  }

  return "OTHER";
}

/**
 * Build a CasePhenotypeMatrix from case and phenotype associations
 *
 * @param diseaseId - The disease ID
 * @param diseaseName - The disease name (optional)
 * @param caseAssociations - Associations where subject is case and object is
 *   disease
 * @param phenotypeAssociations - Associations where subject is case and object
 *   is phenotype
 * @returns A complete CasePhenotypeMatrix for visualization
 */
export function buildMatrix(
  diseaseId: string,
  diseaseName: string | undefined,
  caseAssociations: Association[],
  phenotypeAssociations: Association[],
): CasePhenotypeMatrix {
  // Build Map of caseId -> CaseEntity from caseAssociations
  const casesMap = new Map<string, CaseEntity>();
  for (const assoc of caseAssociations) {
    if (!casesMap.has(assoc.subject)) {
      // Track source disease info from the association
      // The association's object field contains the actual disease this case is linked to
      const isDirect = assoc.object === diseaseId;
      casesMap.set(assoc.subject, {
        id: assoc.subject,
        label: assoc.subject_label,
        fullId: assoc.original_subject,
        sourceDiseaseId: assoc.object,
        sourceDiseaseLabel: assoc.object_label,
        isDirect: isDirect,
      });
    }
  }

  // Build phenotypes map and cells map from phenotypeAssociations
  const phenotypesMap = new Map<string, CasePhenotype>();
  const cells = new Map<string, CasePhenotypeCellData>();
  const binPhenotypes = new Map<string, Set<string>>(); // binId -> Set of phenotypeIds

  for (const assoc of phenotypeAssociations) {
    const caseId = assoc.subject;
    const phenotypeId = assoc.object;
    const binId = findBinForPhenotype(assoc.object_closure);

    // Add phenotype if not already present
    if (!phenotypesMap.has(phenotypeId)) {
      phenotypesMap.set(phenotypeId, {
        id: phenotypeId,
        label: assoc.object_label,
        binId,
      });

      // Track phenotypes per bin
      if (!binPhenotypes.has(binId)) {
        binPhenotypes.set(binId, new Set());
      }
      binPhenotypes.get(binId)!.add(phenotypeId);
    }

    // Build cell key and data
    const cellKey = `${caseId}:${phenotypeId}`;
    const cellData: CasePhenotypeCellData = {
      present: !assoc.negated,
      negated: assoc.negated,
      onset: assoc.onset_qualifier_label,
      onsetId: assoc.onset_qualifier,
      frequency: assoc.frequency_qualifier_label,
      publications: assoc.publications,
      publicationLinks: assoc.publications_links,
      source: assoc.provided_by,
    };

    cells.set(cellKey, cellData);
  }

  // Build bins array, sorted by count descending
  const bins: HistoPhenoBin[] = [];

  for (const [binId, phenotypeIds] of binPhenotypes.entries()) {
    const label = binId === "OTHER" ? "Other" : HISTOPHENO_BINS[binId] || binId;
    bins.push({
      id: binId,
      label,
      phenotypeIds: Array.from(phenotypeIds),
      expanded: false,
      count: phenotypeIds.size,
    });
  }

  // Sort bins by count descending
  bins.sort((a, b) => b.count - a.count);

  // Convert maps to arrays
  const cases = Array.from(casesMap.values());
  const phenotypes = Array.from(phenotypesMap.values());

  return {
    diseaseId,
    diseaseName,
    cases,
    bins,
    phenotypes,
    cells,
    totalCases: cases.length,
    totalPhenotypes: phenotypes.length,
  };
}

/**
 * Get a summary of cell data for a specific bin and case Used for collapsed bin
 * rows to show aggregate information
 *
 * @param matrix - The case-phenotype matrix
 * @param binId - The bin ID to summarize
 * @param caseId - The case ID to summarize
 * @returns Object with presentCount, negatedCount, and total
 */
export function getBinCellSummary(
  matrix: CasePhenotypeMatrix,
  binId: string,
  caseId: string,
): { presentCount: number; negatedCount: number; total: number } {
  // Find the bin
  const bin = matrix.bins.find((b) => b.id === binId);
  if (!bin) {
    return { presentCount: 0, negatedCount: 0, total: 0 };
  }

  let presentCount = 0;
  let negatedCount = 0;

  for (const phenotypeId of bin.phenotypeIds) {
    const cellKey = `${caseId}:${phenotypeId}`;
    const cellData = matrix.cells.get(cellKey);

    if (cellData) {
      if (cellData.negated) {
        negatedCount++;
      } else if (cellData.present) {
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
