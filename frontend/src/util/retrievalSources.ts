export type RetrievalSource = {
  resource_id?: string;
  resource_role?: string;
  upstream_resource_ids?: string[];
};

/**
 * Parse the `sources` field of an association into a flat list of
 * retrieval-source records. Each entry may be a JSON-encoded string holding an
 * array of records (as the API serializes it); malformed entries are skipped.
 */
export const parseRetrievalSources = (
  sources?: string[] | null,
): RetrievalSource[] => {
  const out: RetrievalSource[] = [];
  for (const entry of sources ?? []) {
    try {
      const parsed = typeof entry === "string" ? JSON.parse(entry) : entry;
      if (Array.isArray(parsed)) out.push(...parsed);
      else if (parsed) out.push(parsed);
    } catch {
      /* skip unparseable source entries */
    }
  }
  return out;
};
