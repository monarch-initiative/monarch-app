import { computed, ref } from "vue";
import {
  MONARCH_AGGREGATOR_INFORES,
  type SourceVersion,
  type SourcesVersionsResponse,
  getSourcesVersions,
} from "@/api/source-versions";

/**
 * Edge-level resolution: given an edge's primary + aggregator knowledge
 * sources, return the most precise version we can claim about the bytes
 * actually in the KG.
 *
 * Priority:
 *   1. The first non-monarch aggregator identifies the producing ingest.
 *      Look up the primary inside that ingest's subtree → per-component
 *      version (the `(producer, primary)` composite key).
 *   2. If the primary isn't nested there, fall back to the aggregator's
 *      bundle-level entry — accurate as a date-bound on the data.
 *   3. If only monarch is the aggregator, the edge came from a direct
 *      ingest; look the primary up under its canonical producer.
 */
function lookupForEdge(
  data: SourcesVersionsResponse | null,
  primary: string | null | undefined,
  aggregators: ReadonlyArray<string> | null | undefined,
): SourceVersion | null {
  if (!data) return null;

  const realAggregators = (aggregators ?? []).filter(
    (a) => a && a !== MONARCH_AGGREGATOR_INFORES,
  );

  if (realAggregators.length > 0) {
    for (const agg of realAggregators) {
      const producer = producerWith(data, agg);
      if (!producer) continue;
      const inner = data.by_producer[producer] ?? {};
      if (primary && inner[primary]) return inner[primary];
      return inner[agg] ?? null;
    }
    return null;
  }

  if (!primary) return null;
  const canonical = data.canonical_producer[primary];
  if (!canonical) return null;
  return data.by_producer[canonical]?.[primary] ?? null;
}

/** Node-level resolution by infores using the canonical-producer heuristic. */
function lookupForInfores(
  data: SourcesVersionsResponse | null,
  infores: string | null | undefined,
): SourceVersion | null {
  if (!data || !infores) return null;
  const canonical = data.canonical_producer[infores];
  if (!canonical) return null;
  return data.by_producer[canonical]?.[infores] ?? null;
}

function producerWith(
  data: SourcesVersionsResponse,
  infores: string,
): string | null {
  for (const [producer, fmap] of Object.entries(data.by_producer)) {
    if (fmap[infores]) return producer;
  }
  return null;
}

/**
 * Module-level cache. The receipt is small and changes only between KG
 * releases; one fetch per session is plenty.
 */
const cache = ref<SourcesVersionsResponse | null>(null);
const inFlight = ref<Promise<SourcesVersionsResponse> | null>(null);

async function ensureLoaded(): Promise<SourcesVersionsResponse> {
  if (cache.value) return cache.value;
  if (!inFlight.value) {
    inFlight.value = getSourcesVersions().then((r) => {
      cache.value = r;
      return r;
    });
  }
  return await inFlight.value;
}

export interface ResolvedEdgeVersion {
  /** The thing we're claiming a version for (e.g. `infores:zfin`). */
  primary: SourceVersion;
  /** Filled when `primary` was reached through an aggregator; e.g. AGR. */
  aggregator?: SourceVersion;
}

/**
 * Composable consumed by association detail / table / node pages.
 *
 * Returns lazy lookup helpers; the underlying receipt is fetched once on
 * first call and cached for the rest of the session.
 */
export function useSourceVersions() {
  const data = computed(() => cache.value);
  const isLoaded = computed(() => cache.value !== null);

  // Kick off the fetch on first call; consumers can ignore the promise and
  // just react to `data` once it populates.
  void ensureLoaded();

  function versionForEdge(
    edge: {
      primary_knowledge_source?: string | null;
      aggregator_knowledge_source?: ReadonlyArray<string> | string | null;
    },
  ): ResolvedEdgeVersion | null {
    const aggregators =
      typeof edge.aggregator_knowledge_source === "string"
        ? [edge.aggregator_knowledge_source]
        : edge.aggregator_knowledge_source ?? [];
    const primary = lookupForEdge(
      cache.value,
      edge.primary_knowledge_source,
      aggregators,
    );
    if (!primary) return null;
    // If the resolved primary came from inside an aggregator (`via` non-empty)
    // OR the bundle-level fallback fired (resolved infores != requested
    // primary), surface the aggregator alongside.
    const realAggregators = aggregators.filter(
      (a) => a && a !== MONARCH_AGGREGATOR_INFORES,
    );
    let aggregator: SourceVersion | undefined;
    for (const agg of realAggregators) {
      const producer = cache.value && producerWith(cache.value, agg);
      if (!producer) continue;
      aggregator = cache.value!.by_producer[producer]?.[agg];
      if (aggregator) break;
    }
    return { primary, aggregator };
  }

  function versionForInfores(infores: string | null | undefined): SourceVersion | null {
    return lookupForInfores(cache.value, infores);
  }

  return {
    data,
    isLoaded,
    versionForEdge,
    versionForInfores,
  };
}
