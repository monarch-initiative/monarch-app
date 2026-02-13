import { computed } from "vue";
import { startCase } from "lodash";
import type { Node } from "@/api/model";

const HIDDEN_CATEGORIES = new Set([
  "biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation",
]);

export function useAssociationCategories(node: Node) {
  const options = computed(() => {
    const opts =
      node.association_counts?.map((ac) => ({
        id: ac.category || "",
        label: startCase(ac.label),
        count: ac.count,
      })) ?? [];

    const ordered = opts.filter((o) => !HIDDEN_CATEGORIES.has(o.id));

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
