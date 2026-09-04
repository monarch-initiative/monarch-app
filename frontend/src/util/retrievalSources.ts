export type RetrievalSource = {
  resource_id?: string;
  resource_role?: string;
  upstream_resource_ids?: string[];
};

/** normalize one parsed value into a RetrievalSource record */
const toRecord = (value: unknown): RetrievalSource | null => {
  if (typeof value === "string") return value ? { resource_id: value } : null;
  if (value && typeof value === "object") return value as RetrievalSource;
  return null;
};

/**
 * Parse the `sources` field of an association into a flat list of
 * retrieval-source records. Each entry may be a JSON-encoded string holding an
 * array of records or a single record (as the API serializes it), or a plain
 * CURIE string. Entries that don't parse as JSON fall back to a bare
 * resource_id so real provenance is never silently dropped.
 */
export const parseRetrievalSources = (
  sources?: string[] | null,
): RetrievalSource[] => {
  const out: RetrievalSource[] = [];
  for (const entry of sources ?? []) {
    let parsed: unknown = entry;
    if (typeof entry === "string") {
      try {
        parsed = JSON.parse(entry);
      } catch {
        // not JSON — treat the raw string as a plain CURIE resource_id
        parsed = entry;
      }
    }
    const values = Array.isArray(parsed) ? parsed : [parsed];
    for (const value of values) {
      const record = toRecord(value);
      if (record) out.push(record);
    }
  }
  return out;
};
