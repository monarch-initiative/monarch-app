import { computed } from "vue";
import { startCase } from "lodash";
import { TRAVERSE_ORTHOLOG_CATEGORIES } from "@/api/associations";
import type { Node } from "@/api/model";

/** section keys (ac.key) to hide from node pages */
const HIDDEN_CATEGORIES = new Set<string>([]);

export function useAssociationCategories(node: Node) {
  const options = computed(() => {
    const opts =
      node.association_counts?.map((ac) => ({
        /**
         * stable section key; the backend defaults it to the category for plain
         * single-category sections, so this stays category-compatible while
         * also distinguishing sections that share one category (e.g.
         * biolink:Association)
         */
        id: ac.key || ac.category || "",
        label: startCase(ac.label),
        count: TRAVERSE_ORTHOLOG_CATEGORIES.has(ac.category || "")
          ? (ac.count_with_orthologs ?? ac.count)
          : (ac.count ?? 0),
      })) ?? [];

    const ordered = opts.filter(
      (o) => !HIDDEN_CATEGORIES.has(o.id) && (o.count ?? 0) > 0,
    );

    // keep current special-order rule exactly
    const idxCausal = ordered.findIndex(
      (i) => i.id === "biolink:CausalGeneToDiseaseAssociation",
    );
    const idxGenePh = ordered.findIndex(
      (i) => i.id === "biolink:GeneToPhenotypicFeatureAssociation",
    );
    if (idxCausal > -1 && idxGenePh > -1 && idxCausal > idxGenePh) {
      const [causal] = ordered.splice(idxCausal, 1);
      ordered.splice(idxGenePh, 0, causal);
    }
    return ordered;
  });
  return { options };
}
