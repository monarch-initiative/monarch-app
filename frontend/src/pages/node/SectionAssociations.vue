<!--
  node page associations section
-->

<template>
  <!-- show an AppSection for each category in categoryOptions  -->
  <div v-for="category in categoryOptions" :key="category.id">
    <!-- Association table -->
    <AppSection alignment="left" width="full" class="inset">
      <AppHeading :level="3">{{ category.label }}</AppHeading>
      <span v-if="!categoryOptions.length"
        >No associations with &nbsp;<AppNodeBadge :node="node" />
      </span>
      <p v-if="isLoadingDirectCount">Loading direct association data...</p>
      <p v-else-if="isErrorDirectCount" class="error">
        Failed to load direct data.
      </p>

      <!--tabs omly if its disease node-->
      <template v-if="isDiseaseNode">
        <div class="association-tabs">
          <div class="tab-item">
            <AppButton
              :info="true"
              :info-tooltip="directTooltip(category.id)"
              v-if="hasDirectAssociationsForCategory(category.id)"
              :class="[
                'tab-button',
                {
                  active:
                    (selectedTabs[category.id] ?? defaultTab(category.id)) ===
                    'direct',
                },
              ]"
              :disabled="
                isLoadingDirectCount ||
                !hasDirectAssociationsForCategory(category.id)
              "
              :text="`Directly associated ${typeMapping[category.id] ?? 'phenotypes'}`"
              color="none"
              @click="setDirect(category.id, 'true')"
            />
          </div>
          <div class="tab-item">
            <AppButton
              :info="true"
              :info-tooltip="inferredTooltip(category.id)"
              v-if="showAllTab(category.count ?? 0, category.id)"
              :class="[
                'tab-button',
                {
                  active:
                    (selectedTabs[category.id] ?? defaultTab(category.id)) ===
                    'all',
                },
              ]"
              :text="`Inferred associated ${typeMapping[category.id] ?? 'phenotypes'}`"
              color="none"
              @click="setDirect(category.id, 'false')"
            />
          </div>
        </div>
      </template>

      <div class="actions-row">
        <AppButton
          v-if="
            (selectedTabs[category.id] === 'direct' &&
              node.category === 'biolink:Disease' &&
              category?.id.startsWith('biolink:DiseaseToPheno') &&
              (node.has_phenotype_count ?? 0) > 0) ||
            (node.category === 'biolink:Gene' &&
              category?.id.startsWith('biolink:GeneToPheno') &&
              (node.has_phenotype_count ?? 0) > 0)
          "
          v-tooltip="
            'Send these phenotypes to Phenotype Explorer for comparison'
          "
          to="/search-phenotypes"
          :state="{ search: node.id }"
          text="Phenotype Explorer"
          icon="search"
        />

        <div class="search-wrapper">
          <AppTextbox
            v-model="searchValues[category.id]"
            placeholder="Search table data..."
            class="search-box"
            @debounce="(value) => (debouncedSearchValues[category.id] = value)"
            @change="(value) => (debouncedSearchValues[category.id] = value)"
          />
        </div>
      </div>

      <template v-if="category">
        <!-- table view of associations -->
        <AssociationsTable
          :node="node"
          :category="category"
          :direct="getDirectProps(category.id)"
          :search="debouncedSearchValues[category.id]"
          @update:diseaseSubjectLabel="onDiseaseSubjectLabel"
          @totals="(p) => onTotals({ categoryId: String(category.id), ...p })"
        />
      </template>
    </AppSection>
    <!-- details viewer of association -->
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, watchEffect } from "vue";
import { startCase } from "lodash";
import { getDirectAssociationFacetCounts } from "@/api/associations";
import type { Node } from "@/api/model";
import AppButton from "@/components/AppButton.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import type { Options } from "@/components/AppSelectSingle.vue";
import AppTextbox from "@/components/AppTextbox.vue";
import { useQuery } from "@/composables/use-query";
import AssociationsTable from "@/pages/node/AssociationsTable.vue";

type Props = {
  /** current node */
  node: Node;
};

const props = defineProps<Props>();

type Totals = { direct: number; all: number };
type TotalsMap = Record<string, Totals>;
const totalsByCategory = ref<TotalsMap>({});

const { category: nodeCategory } = props.node;
const diseaseSubject = ref("");

const selectedTabs = ref<Record<string, "all" | "direct">>({});
const searchValues = ref<Record<string, string>>({});
const debouncedSearchValues = ref<Record<string, string>>({});

const typeMapping: { [key: string]: string } = {
  "biolink:DiseaseToPhenotypicFeatureAssociation": "phenotypes",
  "biolink:GeneToPhenotypicFeatureAssociation": "Gene To Phenotypes",
  "biolink:CausalGeneToDiseaseAssociation": "Causal Genes",
  "biolink:CorrelatedGeneToDiseaseAssociation": "Correlated Genes",
  "biolink:GenotypeToDiseaseAssociation": " Genotype to Disease",
};
// parent <script setup>
const onTotals = ({
  categoryId,
  direct,
  all,
}: {
  categoryId: string;
  direct: number;
  all: number;
}) => {
  totalsByCategory.value[categoryId] = { direct, all };
};

const isDiseaseNode = computed(() => nodeCategory === "biolink:Disease");
const onDiseaseSubjectLabel = (label: string) => {
  diseaseSubject.value = label;
};

const directFor = (id: string) => totalsByCategory.value[id]?.direct ?? 0;
const allFor = (id: string) => totalsByCategory.value[id]?.all ?? 0;

const diffFor = (id: string) => {
  const diff = allFor(id) - directFor(id);
  return Number.isFinite(diff) ? Math.max(0, diff) : 0;
};
/** list of options for dropdown */
const categoryOptions = computed<Options>(() => {
  const options =
    props.node.association_counts?.map((association_count) => ({
      id: association_count.category || "",
      label: startCase(association_count.label),
      count: association_count.count,
    })) || [];

  // clone so we don’t mutate the original
  const ordered = [...options];

  // hack: ensure CausalGene sits immediately before Gene→to-Phenotype
  const idxCausal = ordered.findIndex(
    (item) => item.id === "biolink:CausalGeneToDiseaseAssociation",
  );
  const idxGenePhen = ordered.findIndex(
    (item) => item.id === "biolink:GeneToPhenotypicFeatureAssociation",
  );

  if (idxCausal > -1 && idxGenePhen > -1 && idxCausal > idxGenePhen) {
    // remove and re-insert at the target position
    const [causalEntry] = ordered.splice(idxCausal, 1);
    ordered.splice(idxGenePhen, 0, causalEntry);
  }

  return ordered;
});

const setDirect = (categoryId: string, directId: "true" | "false") => {
  selectedTabs.value[categoryId] = directId === "true" ? "direct" : "all";
};

// Tooltip builders
const directTooltip = (categoryId: string): string | undefined => {
  const n = totalsByCategory.value[categoryId]?.direct;
  if (typeof n === "number" && Number.isFinite(n) && n > 0) {
    return `${n.toLocaleString()} phenotypes directly associated with ${props.node.name}`;
  }
  return undefined;
};

const inferredTooltip = (categoryId: string): string | undefined => {
  const all = totalsByCategory.value[categoryId]?.all;
  console.log("inferredTooltip", all);
  if (typeof all === "number" && Number.isFinite(all) && all > 0) {
    const subclassNote = diseaseSubject.value
      ? `  subclasses such as ${diseaseSubject.value}`
      : " subclasses";
    return `${all.toLocaleString()} phenotypes direcly associated with ${props.node.name} as well as ${diffFor(categoryId)} ${subclassNote}`;
  }
  return undefined;
};

// Initialize a query for fetching direct association facet counts per category for a node.
const {
  query: queryDirectFacetCount,
  data: directFacetData,
  isLoading: isLoadingDirectCount,
  isError: isErrorDirectCount,
} = useQuery<
  {
    facet_field: string;
    facet_counts: { label: string; count: number }[];
  },
  []
>(
  // Fetch facet counts grouped by association category, specific to this node
  async function () {
    return await getDirectAssociationFacetCounts(props.node.id);
  },
  { facet_field: "category", facet_counts: [] },
);

// Helper function to check if a specific category has any direct associations
const hasDirectAssociationsForCategory = (categoryId: string): boolean => {
  return directFacetData.value.facet_counts.some(
    (item) => item.label === categoryId && item.count > 0,
  );
};

const directAssociationCount = (categoryId: string): number => {
  const item = directFacetData.value.facet_counts.find(
    (item) => item.label === categoryId,
  );
  return item?.count ?? 0;
};

const showAllTab = computed(() => {
  return (categoryCount: number, categoryId: string): boolean => {
    return categoryCount > directAssociationCount(categoryId);
  };
});

/*
 * For disease nodes, defaults to:
 *  - "all" if there are zero direct associations
 *  - "direct" otherwise
 * Non-disease nodes always default to "all".
 */

function defaultTab(categoryId: string): "direct" | "all" {
  const directCount = directAssociationCount(categoryId);
  const isDisease = isDiseaseNode.value;

  if (!isDisease) {
    return "all";
  }

  // disease node: no direct → all, else → direct
  return directCount > 0 ? "direct" : "all";
}

/**
 * - For non-disease pages(temperory, will change once we get the new layout):
 * - 1. defaultTab(categoryId) → "all" when isDiseaseNode is false
 * - 2. If hasDirectAssociationsForCategory(...) is false, omit the “Direct” tab
 */

const getDirectProps = (categoryId: string) => {
  // pick the tab (direct vs all) based on user click or our default rule
  const selected = selectedTabs.value[categoryId] ?? defaultTab(categoryId);

  const isDirect = selected === "direct";
  return {
    id: isDirect ? "true" : "false",
    label: isDirect ? "directly" : "including sub-classes",
  };
};

watch(
  () => props.node.id,
  async (nodeId) => {
    if (nodeId) {
      await queryDirectFacetCount();
    }
  },
  { immediate: true },
);
</script>

<style lang="scss" scoped>
.arrow {
  color: $gray;
}
/** make room for the table of contents **/
.section {
  margin: 10px 20px 10px $toc-width + 20px;
  @media (max-width: 1240px) {
    margin: 10px 20px 10px 20px;
  }
}
.topRow {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  width: 100%;
  gap: 16px;
}
.leftColumn {
  flex: 1;
  min-width: 300px;
}
.rightColumn {
  min-width: 20em;
}
.association-tabs {
  display: flex;
  gap: 0.25em;

  .tab-button {
    z-index: 0;
    position: relative;
    min-width: 22em;
    padding: 0.8rem 1.5rem;
    border: none;
    border-radius: 8px 8px 0 0;
    background-color: $light-gray;
    &.active {
      z-index: 1;
      background-color: $theme;
      box-shadow: 0 3px 0 0 $theme;
      color: white;
    }
  }
  :deep(.tab-button) {
    border: none;
    outline: none;
    box-shadow: none;

    &:focus {
      outline: none;
      box-shadow: none;
    }
    &:hover {
      outline: none;
      box-shadow: none;
    }
  }
}

.actions-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  width: 100%;
  margin: 1rem 0;
  gap: 1rem;
}

.search-wrapper {
  flex: 1 1 auto;
  max-width: 500px;
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.tab-count {
  max-width: 26em;
  color: #888; /* muted grey */
  font-size: 0.875rem;
  white-space: normal;
  word-break: break-word;
}
</style>
