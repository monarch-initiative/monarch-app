/** API functions for fetching case-phenotype data for grid visualization */

import { apiUrl, request } from "./";
import type { CasePhenotypeMatrix } from "./case-phenotype-types";
import type { Association, AssociationResults } from "./model";
import { buildMatrix } from "../util/case-phenotype-matrix";

/**
 * Batch size for case phenotype requests. Keep small due to URL length limits
 * with unicode characters in case IDs.
 */
const CASE_BATCH_SIZE = 5;

/**
 * Fetch CaseToDiseaseAssociations where disease is the object
 *
 * @param diseaseId - The disease ID to fetch cases for
 * @param direct - If true, only return direct associations; if false, include
 *   descendants via closure query
 * @returns Association results containing cases associated with the disease
 */
export const getCasesForDisease = async (
  diseaseId: string,
  direct: boolean = true,
): Promise<AssociationResults> => {
  const params = {
    category: "biolink:CaseToDiseaseAssociation",
    object: diseaseId,
    limit: 500,
    direct: direct,
  };

  const url = `${apiUrl}/association`;
  return await request<AssociationResults>(url, params);
};

/**
 * Fetch CaseToPhenotypicFeatureAssociations for multiple cases Batches requests
 * in groups of 50 case IDs to avoid URL length limits
 *
 * @param caseIds - Array of case IDs to fetch phenotypes for
 * @returns Flattened array of all associations from all batches
 */
export const getCasePhenotypes = async (
  caseIds: string[],
): Promise<Association[]> => {
  if (caseIds.length === 0) {
    return [];
  }

  const allAssociations: Association[] = [];
  const limit = 500;

  /** Batch requests to avoid URL length limits */
  for (let i = 0; i < caseIds.length; i += CASE_BATCH_SIZE) {
    const batchIds = caseIds.slice(i, i + CASE_BATCH_SIZE);
    let offset = 0;
    let hasMore = true;

    /** Paginate through results for this batch */
    while (hasMore) {
      const params = {
        category: "biolink:CaseToPhenotypicFeatureAssociation",
        subject: batchIds,
        limit,
        offset,
      };

      const url = `${apiUrl}/association`;
      const response = await request<AssociationResults>(url, params);
      allAssociations.push(...response.items);

      /** Check if there are more results */
      hasMore = offset + response.items.length < response.total;
      offset += limit;
    }
  }

  return allAssociations;
};

/**
 * Orchestrate fetching and building the case-phenotype matrix for a disease
 *
 * @param diseaseId - The disease ID to build the matrix for
 * @param diseaseName - Optional disease name for display
 * @param direct - If true, only include direct cases; if false, include
 *   descendants
 * @returns The case-phenotype matrix or null if no cases found
 */
export const getCasePhenotypeMatrix = async (
  diseaseId: string,
  diseaseName?: string,
  direct: boolean = true,
): Promise<CasePhenotypeMatrix | null> => {
  /** Fetch cases associated with the disease */
  const casesResponse = await getCasesForDisease(diseaseId, direct);

  if (casesResponse.items.length === 0) {
    return null;
  }

  /** Extract case IDs from the associations */
  const caseIds = casesResponse.items.map((assoc) => assoc.subject);

  /** Fetch phenotypes for all cases */
  const phenotypeAssociations = await getCasePhenotypes(caseIds);

  /** Build and return the matrix */
  return buildMatrix(
    diseaseId,
    diseaseName,
    casesResponse.items,
    phenotypeAssociations,
  );
};
