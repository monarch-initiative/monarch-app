import { startCase } from "lodash";
import { getCategoryIcon, getCategoryLabel } from "@/api/categories";
import type { FacetValue } from "@/api/model";
import type { Option } from "@/components/AppSelectMulti.vue";

/**
 * Build a dropdown option for a search facet value.
 *
 * - `category` values get their biolink display label + icon.
 * - `in_taxon_label` (taxon) values keep the API's already-correct
 *   scientific-name casing (e.g. "Homo sapiens", "Saccharomyces cerevisiae
 *   S288C") and render italic — do NOT title-case them, which would produce
 *   "Homo Sapiens" and split strain suffixes ("S288C" -> "S 288 C").
 * - everything else is title-cased for display.
 */
export const buildFacetOption = (
  facetLabel: string | undefined,
  facetValue: FacetValue,
): Option => {
  const value = facetValue.label ?? "";
  const isCategory = facetLabel === "category";
  const isTaxon = facetLabel === "in_taxon_label";
  return {
    id: value,
    label: isCategory
      ? getCategoryLabel(value)
      : isTaxon
        ? value
        : startCase(value),
    icon: isCategory ? getCategoryIcon(value) : "",
    italic: isTaxon,
    count: facetValue.count,
  };
};
