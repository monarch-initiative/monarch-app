import { computed, reactive, watch, type ComputedRef, type Ref } from "vue";
import {
  getAssociations,
  getDirectAssociationFacetCounts,
} from "@/api/associations";
import { useQuery } from "@/composables/use-query";

type CategoryOption = { id: string; count?: number };

export function useAssociationCounts(
  nodeId: Ref<string> | ComputedRef<string>,
  categoryOptions: Ref<CategoryOption[]> | ComputedRef<CategoryOption[]>,
) {
  // direct-only facet counts
  const {
    query: queryDirectFacetCount,
    data: directFacetData,
    isLoading: isLoadingDirectCount,
    isError: isErrorDirectCount,
  } = useQuery(
    async () => {
      return await getDirectAssociationFacetCounts(nodeId.value);
    },
    { facet_field: "category", facet_counts: [] },
  );

  // map of all/inferred counts from categoryOptions
  const allCountByCategory = computed(() => {
    const out = new Map<string, number>();
    for (const c of categoryOptions.value) out.set(c.id, c.count ?? 0);
    return out;
  });

  // map of direct-only counts from facet API
  const directCountByCategory = computed(() => {
    const out = new Map<string, number>();
    for (const { label, count } of directFacetData.value.facet_counts) {
      out.set(label, count);
    }
    return out;
  });

  // convenient combined counts
  const tabCounts = computed(() => {
    const res: Record<string, { direct: number; all: number }> = {};
    for (const c of categoryOptions.value) {
      res[c.id] = {
        direct: directCountByCategory.value.get(c.id) ?? 0,
        all: allCountByCategory.value.get(c.id) ?? 0,
      };
    }
    return res;
  });

  const hasDirectAssociationsForCategory = (categoryId: string) =>
    (directCountByCategory.value.get(categoryId) ?? 0) > 0;

  const directAssociationCount = (categoryId: string) =>
    directCountByCategory.value.get(categoryId) ?? 0;

  const showAllTab = computed(() => {
    return (_categoryCountFromProp: number, categoryId: string) => {
      const allCount = allCountByCategory.value.get(categoryId) ?? 0;
      const directCount = directCountByCategory.value.get(categoryId) ?? 0;
      return allCount > directCount;
    };
  });

  // optional: example disease subject for the “All” tooltip (cached)
  const diseaseExampleByCategory = reactive<Record<string, string>>({});
  async function ensureDiseaseExample(categoryId: string) {
    if (!categoryId.includes("DiseaseToPhenotypicFeatureAssociation")) return;
    if (diseaseExampleByCategory[categoryId]) return;
    const res = await getAssociations(
      nodeId.value,
      categoryId,
      0,
      1,
      true,
      "false",
      "",
      undefined,
    );
    diseaseExampleByCategory[categoryId] = res.items?.[0]?.subject_label ?? "";
  }

  // refresh when node changes; clear example cache
  watch(
    nodeId,
    async (id) => {
      if (id) await queryDirectFacetCount();
      Object.keys(diseaseExampleByCategory).forEach(
        (k) => delete diseaseExampleByCategory[k],
      );
    },
    { immediate: true },
  );

  return {
    // state
    isLoadingDirectCount,
    isErrorDirectCount,
    tabCounts,
    diseaseExampleByCategory,
    // helpers
    hasDirectAssociationsForCategory,
    directAssociationCount,
    showAllTab,
    ensureDiseaseExample,
    queryDirectFacetCount,
  };
}
