import { apiUrl, request } from "@/api";

/** One resolved version record from the build receipt. */
export interface SourceVersion {
  infores: string;
  name: string;
  version: string;
  version_method: string;
  retrieved_at: string;
  urls: string[];
  /**
   * Path of intermediate-build ids between the producing ingest and this
   * entry. e.g. ["infores:agr"] when this is `infores:zfin` nested under
   * `infores:agr` in alliance-ingest's subtree.
   */
  via: string[];
}

/** Response from GET /sources/versions. */
export interface SourcesVersionsResponse {
  release: string;
  generated_at: string;
  /** producer-ingest id → infores → SourceVersion */
  by_producer: Record<string, Record<string, SourceVersion>>;
  /** infores → producer-ingest id chosen as canonical for node-level lookup */
  canonical_producer: Record<string, string>;
  disagreements: Array<Record<string, unknown>>;
  version_drift: Array<Record<string, unknown>>;
}

/** `infores:monarchinitiative` is always present as an aggregator on edges
 * we produced; consumers strip it before edge resolution. */
export const MONARCH_AGGREGATOR_INFORES = "infores:monarchinitiative";

export const getSourcesVersions = async (
  release = "latest",
): Promise<SourcesVersionsResponse> => {
  const url = `${apiUrl}/sources/versions?release=${encodeURIComponent(release)}`;
  return await request<SourcesVersionsResponse>(url);
};
