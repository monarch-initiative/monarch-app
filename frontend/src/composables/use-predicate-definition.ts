import { computed, ref, toValue, watch, type MaybeRefOrGetter } from "vue";
import {
  useBiolinkModel,
  type PredicateInfo,
} from "@/composables/use-biolink-model";

/**
 * A predicate's human-readable label, biolink docs link, and definition.
 *
 * Three components derived these separately, and the docs-URL builders had
 * already drifted: the explainer converts spaces to underscores, because
 * biolink slot keys are space-separated ("treats or applied or studied to
 * treat"), while the two detail views only stripped the prefix, because they
 * are handed CURIEs. Each was right for its own input and wrong for the
 * other's. This handles both.
 */
/** e.g. "biolink:applied_to_treat" or "applied to treat" -> "applied to treat" */
export const predicateLabel = (name?: string): string =>
  (name ?? "").replace(/^biolink:/, "").replace(/_/g, " ");

/**
 * A predicate's page in the biolink model docs.
 *
 * Slugs use underscores. Callers pass either a CURIE
 * (`biolink:applied_to_treat`) or a biolink slot key, which is space-separated
 * (`applied to treat`), so both separators have to be handled here -- the two
 * spellings of this that existed before each handled only one.
 */
export const predicateDocsUrl = (name?: string): string =>
  `https://biolink.github.io/biolink-model/${(name ?? "")
    .replace(/^biolink:/, "")
    .replace(/ /g, "_")}/`;

export function usePredicateDefinition(predicate: MaybeRefOrGetter<string>) {
  const { loadBiolinkModel, getPredicateInfo, isLoading, error } =
    useBiolinkModel();

  const info = ref<PredicateInfo | null>(null);

  const value = computed(() => toValue(predicate) ?? "");

  const label = computed(() => predicateLabel(value.value));
  const docsUrl = computed(() => predicateDocsUrl(value.value));

  /**
   * Fetch the definition for the current predicate.
   *
   * Callers with an explicit open event should call this then, not only rely on
   * the watch: the watch keys on the predicate, so reopening the _same_ one
   * after a failed model fetch would otherwise never retry.
   */
  async function load() {
    const predicateValue = value.value;
    if (!predicateValue) {
      info.value = null;
      return;
    }
    await loadBiolinkModel();
    // Guard against a slow load resolving after the caller moved on.
    if (value.value !== predicateValue) return;
    info.value = getPredicateInfo(predicateValue);
  }

  watch(
    value,
    () => {
      info.value = null;
      void load();
    },
    { immediate: true },
  );

  return { label, docsUrl, info, isLoading, error, load };
}
