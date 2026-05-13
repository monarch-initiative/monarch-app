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
   * Path of intermediate-build ids between the producing ingest and this entry.
   * e.g. ["infores:agr"] when this is `infores:zfin` nested under `infores:agr`
   * in alliance-ingest's subtree.
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
}

/**
 * `infores:monarchinitiative` is always present as an aggregator on edges we
 * produced; consumers strip it before edge resolution.
 */
export const MONARCH_AGGREGATOR_INFORES = "infores:monarchinitiative";

export const getSourcesVersions = async (
  release?: string,
  dev?: boolean,
): Promise<SourcesVersionsResponse> => {
  // Both params are intentionally optional: the backend defaults `release` to
  // the deployed `MONARCH_KG_VERSION` (so each environment reads its own
  // build's receipt) and `dev` to its `MONARCH_KG_USE_DEV` env var. Passing
  // them here would override those deploy-time decisions.
  const params: Record<string, string> = {};
  if (release !== undefined) params.release = release;
  if (dev !== undefined) params.dev = dev ? "true" : "false";
  return await request<SourcesVersionsResponse>(
    `${apiUrl}/sources/versions`,
    params,
  );
};
