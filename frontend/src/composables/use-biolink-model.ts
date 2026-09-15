import { ref, shallowRef } from "vue";
import yaml from "js-yaml";

export interface PredicateInfo {
  name: string;
  description?: string;
  domain?: string;
  range?: string;
  aliases?: string[];
  is_a?: string;
  symmetric?: boolean;
  inverse?: string;
  mixins?: string[];
  exact_mappings?: string[];
  narrow_mappings?: string[];
  broad_mappings?: string[];
  related_mappings?: string[];
}

interface BiolinkModel {
  slots?: Record<string, any>;
  classes?: Record<string, any>;
}

const BIOLINK_MODEL_URL = "https://w3id.org/biolink/biolink-model.yaml";
const CACHE_KEY = "biolink-model-cache";
const CACHE_TIMESTAMP_KEY = "biolink-model-cache-timestamp";
const CACHE_DURATION_MS = 24 * 60 * 60 * 1000; // 24 hours

/**
 * Module-level shared state: the biolink model is large, so it is fetched and
 * parsed at most once per session and reused by every caller of
 * useBiolinkModel() (e.g. the predicate explainer on every association row),
 * rather than re-parsed per component instance. shallowRef avoids deep-proxying
 * the large model tree (nothing mutates it reactively; it's read-only lookup).
 */
const model = shallowRef<BiolinkModel | null>(null);
const isLoading = ref(false);
const error = ref<string | null>(null);
/** in-flight load, so concurrent callers share a single fetch/parse */
let loadPromise: Promise<void> | null = null;

/** Check if cached model is still valid */
const isCacheValid = (): boolean => {
  try {
    const timestamp = localStorage.getItem(CACHE_TIMESTAMP_KEY);
    if (!timestamp) return false;
    const cacheAge = Date.now() - parseInt(timestamp, 10);
    return cacheAge < CACHE_DURATION_MS;
  } catch {
    return false;
  }
};

/** Load model from cache */
const loadFromCache = (): BiolinkModel | null => {
  try {
    const cached = localStorage.getItem(CACHE_KEY);
    if (!cached) return null;
    return JSON.parse(cached) as BiolinkModel;
  } catch {
    return null;
  }
};

/** Save model to cache */
const saveToCache = (data: BiolinkModel): void => {
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify(data));
    localStorage.setItem(CACHE_TIMESTAMP_KEY, Date.now().toString());
  } catch (err) {
    console.warn("Failed to cache biolink model:", err);
  }
};

/** Fetch and parse the Biolink Model YAML (once per session) */
const loadBiolinkModel = async (): Promise<void> => {
  if (model.value) return;
  if (loadPromise) return loadPromise;

  loadPromise = (async () => {
    // Check cache first
    if (isCacheValid()) {
      const cached = loadFromCache();
      if (cached) {
        model.value = cached;
        return;
      }
    }

    isLoading.value = true;
    error.value = null;
    try {
      const response = await fetch(BIOLINK_MODEL_URL);
      if (!response.ok) {
        throw new Error(
          `Failed to fetch biolink model: ${response.statusText}`,
        );
      }
      const yamlText = await response.text();
      const parsed = yaml.load(yamlText) as BiolinkModel;
      model.value = parsed;
      saveToCache(parsed);
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : "Failed to load biolink model";
      console.error("Error loading biolink model:", err);
    } finally {
      isLoading.value = false;
      // allow a retry if the load failed to populate the model
      if (!model.value) loadPromise = null;
    }
  })();

  return loadPromise;
};

/**
 * Get predicate information by name
 *
 * @param predicateName - Name with or without 'biolink:' prefix
 */
const getPredicateInfo = (predicateName: string): PredicateInfo | null => {
  if (!model.value?.slots) return null;

  // Remove biolink: prefix if present
  const cleanName = predicateName.replace(/^biolink:/, "");

  // Try exact match first
  let slotData = model.value.slots[cleanName];

  // Try with underscores replaced by spaces
  if (!slotData) {
    const spaceName = cleanName.replace(/_/g, " ");
    slotData = model.value.slots[spaceName];
  }

  // Try to find by alias
  if (!slotData) {
    for (const value of Object.values(model.value.slots)) {
      if (value?.aliases && Array.isArray(value.aliases)) {
        if (value.aliases.includes(cleanName)) {
          slotData = value;
          break;
        }
      }
    }
  }

  if (!slotData) return null;

  return {
    name: cleanName,
    description: slotData.description,
    domain: slotData.domain,
    range: slotData.range,
    aliases: slotData.aliases,
    is_a: slotData.is_a,
    symmetric: slotData.symmetric,
    inverse: slotData.inverse,
    mixins: slotData.mixins,
    exact_mappings: slotData.exact_mappings,
    narrow_mappings: slotData.narrow_mappings,
    broad_mappings: slotData.broad_mappings,
    related_mappings: slotData.related_mappings,
  };
};

/**
 * Walk the is_a chain upward to build a partial predicate hierarchy, from the
 * immediate parent outward (most specific first).
 */
const getPredicateAncestors = (
  predicateName: string,
  depth = 3,
): PredicateInfo[] => {
  const ancestors: PredicateInfo[] = [];
  const seen = new Set<string>();
  let current = getPredicateInfo(predicateName);
  let steps = 0;
  while (current?.is_a && steps < depth) {
    const parent = getPredicateInfo(current.is_a);
    // stop on a missing parent or an is_a cycle
    if (!parent || seen.has(parent.name)) break;
    seen.add(parent.name);
    ancestors.push(parent);
    current = parent;
    steps++;
  }
  return ancestors;
};

/**
 * Find the direct child predicates. Biolink attaches sub-predicates via `is_a`
 * (single inheritance) and `mixins` (multiple inheritance) — e.g. "ameliorates
 * condition" and "preventative for condition" have their own `is_a` but mix in
 * "treats" — so both are considered here.
 */
const getPredicateChildren = (predicateName: string): PredicateInfo[] => {
  if (!model.value?.slots) return [];
  const cleanName = predicateName.replace(/^biolink:/, "");
  const targetNames = new Set([cleanName, cleanName.replace(/_/g, " ")]);
  const children: PredicateInfo[] = [];
  for (const [key, value] of Object.entries(model.value.slots)) {
    if (!value) continue;
    const parents = [
      value.is_a,
      ...(Array.isArray(value.mixins) ? value.mixins : []),
    ];
    if (parents.some((parent) => parent && targetNames.has(parent))) {
      children.push({
        name: key,
        description: value.description,
        is_a: value.is_a,
      });
    }
  }
  return children.sort((a, b) => a.name.localeCompare(b.name));
};

/** Clear the cache (and the loaded model) */
const clearCache = (): void => {
  try {
    localStorage.removeItem(CACHE_KEY);
    localStorage.removeItem(CACHE_TIMESTAMP_KEY);
  } catch (err) {
    console.warn("Failed to clear cache:", err);
  }
  model.value = null;
  loadPromise = null;
};

export function useBiolinkModel() {
  return {
    isLoading,
    error,
    model,
    loadBiolinkModel,
    getPredicateInfo,
    getPredicateAncestors,
    getPredicateChildren,
    clearCache,
  };
}
