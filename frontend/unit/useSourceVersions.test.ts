import { beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises } from "@vue/test-utils";
import {
  MONARCH_AGGREGATOR_INFORES,
  type SourcesVersionsResponse,
} from "@/api/source-versions";

/**
 * Synthetic receipt mirroring the backend test fixture: covers the three
 * resolution cases this composable has to handle.
 *
 * - alliance-ingest: aggregator (`infores:agr`) WITH per-MOD nesting.
 * - alliance-disease-association-ingest: aggregator WITHOUT per-MOD nesting —
 *   exercises the bundle-level fallback.
 * - hgnc-ingest: direct primary ingest (only monarch as aggregator).
 * - kg-phenio: ontology terms reached via phenio.
 */
const receipt = (): SourcesVersionsResponse => ({
  release: "2026-05-07",
  generated_at: "2026-05-07T16:11:30Z",
  by_producer: {
    "alliance-ingest": {
      "infores:agr": {
        infores: "infores:agr",
        name: "Alliance of Genome Resources",
        version: "8.3.0",
        version_method: "alliance_fms_api",
        retrieved_at: "",
        urls: [],
        via: [],
      },
      "infores:zfin": {
        infores: "infores:zfin",
        name: "ZFIN",
        version: "2026-04-15",
        version_method: "alliance_fms_submission",
        retrieved_at: "",
        urls: [],
        via: ["infores:agr"],
      },
    },
    "alliance-disease-association-ingest": {
      "infores:agr": {
        infores: "infores:agr",
        name: "Alliance of Genome Resources",
        version: "8.3.0",
        version_method: "alliance_fms_api",
        retrieved_at: "",
        urls: [],
        via: [],
      },
    },
    "hgnc-ingest": {
      "infores:hgnc": {
        infores: "infores:hgnc",
        name: "HUGO Gene Nomenclature Committee",
        version: "2026-05-01",
        version_method: "http_last_modified",
        retrieved_at: "",
        urls: [],
        via: [],
      },
    },
    "kg-phenio": {
      "infores:mondo": {
        infores: "infores:mondo",
        name: "MONDO",
        version: "2026-04-01",
        version_method: "owl_version_iri",
        retrieved_at: "",
        urls: [],
        via: ["phenio"],
      },
    },
  },
  canonical_producer: {
    "infores:agr": "alliance-ingest",
    "infores:zfin": "alliance-ingest",
    "infores:hgnc": "hgnc-ingest",
    "infores:mondo": "kg-phenio",
  },
});

vi.mock("@/api/source-versions", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/api/source-versions")>();
  return {
    ...actual,
    getSourcesVersions: vi.fn(),
  };
});

/** Reimport composable + api with a fresh module-level cache per test. */
async function loadFresh() {
  vi.resetModules();
  const api = await import("@/api/source-versions");
  (
    api.getSourcesVersions as unknown as ReturnType<typeof vi.fn>
  ).mockResolvedValue(receipt());
  const { useSourceVersions } =
    await import("@/composables/use-source-versions");
  const composable = useSourceVersions();
  // Let `ensureLoaded()` resolve and populate the cache.
  await flushPromises();
  return composable;
}

describe("useSourceVersions", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("resolves a nested per-MOD edge through the aggregator", async () => {
    const { versionForEdge } = await loadFresh();
    const result = versionForEdge({
      primary_knowledge_source: "infores:zfin",
      aggregator_knowledge_source: ["infores:agr", MONARCH_AGGREGATOR_INFORES],
    });
    expect(result?.primary.infores).toBe("infores:zfin");
    expect(result?.primary.version).toBe("2026-04-15");
    expect(result?.aggregator?.infores).toBe("infores:agr");
    expect(result?.aggregator?.version).toBe("8.3.0");
  });

  it("falls back to bundle-level aggregator when primary isn't nested", async () => {
    const { versionForEdge } = await loadFresh();
    // Edge claims AGR aggregation but the producing ingest doesn't expose
    // a per-MOD nesting for `infores:zfin` — should fall through to AGR
    // itself rather than reaching into alliance-ingest.
    const result = versionForEdge({
      primary_knowledge_source: "infores:mgi",
      aggregator_knowledge_source: ["infores:agr"],
    });
    // alliance-ingest is listed first in by_producer and has infores:agr,
    // so it wins as the producer. `infores:mgi` isn't there → bundle fallback.
    expect(result?.primary.infores).toBe("infores:agr");
    expect(result?.primary.version).toBe("8.3.0");
  });

  it("resolves a direct ingest edge with no real aggregator", async () => {
    const { versionForEdge } = await loadFresh();
    const result = versionForEdge({
      primary_knowledge_source: "infores:hgnc",
      aggregator_knowledge_source: [MONARCH_AGGREGATOR_INFORES],
    });
    expect(result?.primary.infores).toBe("infores:hgnc");
    expect(result?.primary.version).toBe("2026-05-01");
    expect(result?.aggregator).toBeUndefined();
  });

  it("accepts aggregator_knowledge_source as a single string", async () => {
    const { versionForEdge } = await loadFresh();
    const result = versionForEdge({
      primary_knowledge_source: "infores:zfin",
      aggregator_knowledge_source: "infores:agr",
    });
    expect(result?.primary.infores).toBe("infores:zfin");
    expect(result?.aggregator?.infores).toBe("infores:agr");
  });

  it("returns null when primary is unknown and an aggregator is named", async () => {
    const { versionForEdge } = await loadFresh();
    // Unknown aggregator → no producer match → null.
    const result = versionForEdge({
      primary_knowledge_source: "infores:zfin",
      aggregator_knowledge_source: ["infores:nope"],
    });
    expect(result).toBeNull();
  });

  it("resolves an ontology infores via the phenio canonical producer", async () => {
    const { versionForInfores } = await loadFresh();
    const result = versionForInfores("infores:mondo");
    expect(result?.version).toBe("2026-04-01");
    expect(result?.via).toEqual(["phenio"]);
  });

  it("resolves a data-source infores via its self-named ingest", async () => {
    const { versionForInfores } = await loadFresh();
    expect(versionForInfores("infores:hgnc")?.version).toBe("2026-05-01");
  });

  it("returns null for unknown infores", async () => {
    const { versionForInfores } = await loadFresh();
    expect(versionForInfores("infores:never-heard-of")).toBeNull();
    expect(versionForInfores(null)).toBeNull();
    expect(versionForInfores(undefined)).toBeNull();
  });

  it("allows a retry after a rejected fetch (inFlight is cleared)", async () => {
    vi.resetModules();
    const api = await import("@/api/source-versions");
    const fetchMock = api.getSourcesVersions as unknown as ReturnType<
      typeof vi.fn
    >;
    fetchMock.mockRejectedValueOnce(new Error("network"));
    fetchMock.mockResolvedValueOnce(receipt());

    const { useSourceVersions } =
      await import("@/composables/use-source-versions");

    // First consumer triggers the failing fetch.
    const first = useSourceVersions();
    await flushPromises().catch(() => {});
    expect(first.isLoaded.value).toBe(false);

    // Second consumer should kick off a fresh fetch, which succeeds.
    const second = useSourceVersions();
    await flushPromises();
    expect(second.isLoaded.value).toBe(true);
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
});
