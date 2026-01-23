/**
 * API functions for fetching case-phenotype data for grid visualization. Uses
 * the single backend endpoint that handles all the complex Solr queries.
 */

import { apiUrl } from "./";
import type {
  CaseEntity,
  CasePhenotype,
  CasePhenotypeCellData,
  CasePhenotypeMatrix,
  HistoPhenoBin,
} from "./case-phenotype-types";

/** Response type from the backend API */
interface BackendMatrixResponse {
  disease_id: string;
  disease_name: string | null;
  total_cases: number;
  total_phenotypes: number;
  cases: Array<{
    id: string;
    label: string | null;
    full_id?: string | null;
    source_disease_id?: string | null;
    source_disease_label?: string | null;
    is_direct: boolean;
  }>;
  phenotypes: Array<{
    id: string;
    label: string | null;
    bin_id: string;
  }>;
  bins: Array<{
    id: string;
    label: string;
    phenotype_count: number;
  }>;
  cells: Record<
    string,
    {
      present: boolean;
      negated?: boolean | null;
      onset_qualifier?: string | null;
      onset_qualifier_label?: string | null;
      publications?: string[] | null;
    }
  >;
}

/** Options for the getCasePhenotypeMatrix function */
export interface CasePhenotypeMatrixOptions {
  /** Only include cases directly associated with this disease (default: true) */
  direct?: boolean;
  /** Maximum number of cases allowed (default: 1000) */
  limit?: number;
}

/** Error thrown when case count exceeds the configured limit */
export class CaseLimitExceededError extends Error {
  constructor(
    public actual: number,
    public limit: number,
    public diseaseId: string,
  ) {
    super(
      `Disease ${diseaseId} has ${actual} cases, exceeding limit of ${limit}. ` +
        `Use direct=true to filter to direct cases only, or increase the limit.`,
    );
    this.name = "CaseLimitExceededError";
  }
}

/**
 * Fetch case-phenotype matrix from the backend.
 *
 * This replaces the old batched approach with a single API call that handles
 * all the Solr queries server-side.
 *
 * @param diseaseId - MONDO disease ID to fetch matrix for
 * @param options - Options for the request
 * @returns The case-phenotype matrix or null if no cases found
 * @throws CaseLimitExceededError if case count exceeds limit
 * @throws Error for other API errors
 */
export async function getCasePhenotypeMatrix(
  diseaseId: string,
  options: CasePhenotypeMatrixOptions = {},
): Promise<CasePhenotypeMatrix | null> {
  const { direct = true, limit = 1000 } = options;

  const params = new URLSearchParams();
  params.set("direct", String(direct));
  params.set("limit", String(limit));

  const url = `${apiUrl}/case-phenotype-matrix/${encodeURIComponent(diseaseId)}?${params}`;
  const response = await fetch(url);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const detail = errorData.detail || "Unknown error";

    // Parse case limit exceeded errors
    if (response.status === 400 && detail.includes("exceeds limit")) {
      const match = detail.match(/\((\d+)\).*\((\d+)\)/);
      if (match) {
        throw new CaseLimitExceededError(
          parseInt(match[1]),
          parseInt(match[2]),
          diseaseId,
        );
      }
    }

    throw new Error(`API error (${response.status}): ${detail}`);
  }

  const data: BackendMatrixResponse = await response.json();

  // Return null if no cases found
  if (data.total_cases === 0) {
    return null;
  }

  // Transform backend response to frontend types
  return transformResponse(data);
}

/**
 * Transform backend response to frontend CasePhenotypeMatrix format. Handles
 * snake_case to camelCase conversion and Map creation.
 */
function transformResponse(data: BackendMatrixResponse): CasePhenotypeMatrix {
  // Transform cases
  const cases: CaseEntity[] = data.cases.map((c) => ({
    id: c.id,
    label: c.label ?? undefined,
    fullId: c.full_id ?? undefined,
    sourceDiseaseId: c.source_disease_id ?? undefined,
    sourceDiseaseLabel: c.source_disease_label ?? undefined,
    isDirect: c.is_direct,
  }));

  // Transform phenotypes
  const phenotypes: CasePhenotype[] = data.phenotypes.map((p) => ({
    id: p.id,
    label: p.label ?? undefined,
    binId: p.bin_id,
  }));

  // Transform bins - group phenotypes by bin
  const phenotypesByBin = new Map<string, string[]>();
  for (const p of phenotypes) {
    const list = phenotypesByBin.get(p.binId) || [];
    list.push(p.id);
    phenotypesByBin.set(p.binId, list);
  }

  const bins: HistoPhenoBin[] = data.bins.map((b) => ({
    id: b.id,
    label: b.label,
    phenotypeIds: phenotypesByBin.get(b.id) || [],
    expanded: false,
    count: b.phenotype_count,
  }));

  // Transform cells - convert object to Map
  const cells = new Map<string, CasePhenotypeCellData>();
  for (const [key, cell] of Object.entries(data.cells)) {
    cells.set(key, {
      present: cell.present,
      negated: cell.negated ?? undefined,
      onset: cell.onset_qualifier_label ?? undefined,
      onsetId: cell.onset_qualifier ?? undefined,
      publications: cell.publications ?? undefined,
    });
  }

  return {
    diseaseId: data.disease_id,
    diseaseName: data.disease_name ?? undefined,
    cases,
    bins,
    phenotypes,
    cells,
    totalCases: data.total_cases,
    totalPhenotypes: data.total_phenotypes,
  };
}

/**
 * Create a cell lookup key from case and phenotype IDs. Must match the format
 * used by the backend.
 */
export function makeCellKey(caseId: string, phenotypeId: string): string {
  return `${caseId}:${phenotypeId}`;
}

/**
 * Fetch case counts for a disease (used for tab labels). Makes lightweight
 * requests just to get counts without full matrix data.
 *
 * @param diseaseId - MONDO disease ID
 * @returns Object with direct and all case counts
 */
export async function getCaseCounts(
  diseaseId: string,
): Promise<{ direct: number; all: number }> {
  // Use limit=1 to minimize data transfer, we just want the count
  const [directResponse, allResponse] = await Promise.all([
    fetch(
      `${apiUrl}/case-phenotype-matrix/${encodeURIComponent(diseaseId)}?direct=true&limit=1000`,
    ),
    fetch(
      `${apiUrl}/case-phenotype-matrix/${encodeURIComponent(diseaseId)}?direct=false&limit=1000`,
    ),
  ]);

  let directCount = 0;
  let allCount = 0;

  if (directResponse.ok) {
    const data = await directResponse.json();
    directCount = data.total_cases;
  } else if (directResponse.status === 400) {
    // Case limit exceeded - parse from error message
    const errorData = await directResponse.json().catch(() => ({}));
    const match = errorData.detail?.match(/\((\d+)\)/);
    if (match) {
      directCount = parseInt(match[1]);
    }
  }

  if (allResponse.ok) {
    const data = await allResponse.json();
    allCount = data.total_cases;
  } else if (allResponse.status === 400) {
    // Case limit exceeded - parse from error message
    const errorData = await allResponse.json().catch(() => ({}));
    const match = errorData.detail?.match(/\((\d+)\)/);
    if (match) {
      allCount = parseInt(match[1]);
    }
  }

  return { direct: directCount, all: allCount };
}
