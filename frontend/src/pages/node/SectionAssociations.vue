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
          <!-- Non-disease pages: show “All” first, then “Direct” -->

          <div class="tab-item">
            <AppButton
              :class="[
                'tab-button',
                {
                  active:
                    (selectedTabs[category.id] ?? defaultTab(category.id)) ===
                    'direct',
                },
              ]"
              @click="setDirect(category.id, 'true')"
              v-if="hasDirectAssociationsForCategory(category.id)"
              :disabled="
                isLoadingDirectCount ||
                !hasDirectAssociationsForCategory(category.id)
              "
              :text="`Direct Associations`"
              v-tooltip="'Exclude subclass associations'"
              color="none"
            />

            <span
              class="tab-count"
              v-if="
                category.id.includes('DiseaseToPhenotypicFeatureAssociation')
              "
            >
              <template v-if="showAllTab(category.count ?? 0, category.id)">
                {{ directAssociationCount(category.id).toLocaleString() }}
                unique direct phenotypes across sources
              </template>
              <template v-else> No subclasses exist </template>
            </span>
          </div>
          <div class="tab-item">
            <AppButton
              v-if="showAllTab(category.count ?? 0, category.id)"
              :class="[
                'tab-button',
                {
                  active:
                    (selectedTabs[category.id] ?? defaultTab(category.id)) ===
                    'all',
                },
              ]"
              @click="setDirect(category.id, 'false')"
              v-tooltip="'Include subclass associations'"
              text="All Associations"
              color="none"
            />
            <span
              class="tab-count"
              v-if="
                showAllTab(category.count ?? 0, category.id) &&
                category.id.includes('DiseaseToPhenotypicFeatureAssociation')
              "
            >
              {{ (category.count ?? 0).toLocaleString() }} phenotypes
            </span>
          </div>

          <!-- Disease pages: show “Direct” first, then “All” -->
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
        />
      </template>
    </AppSection>
    <!-- details viewer of association -->
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
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

const { category: nodeCategory } = props.node;

const selectedTabs = ref<Record<string, "all" | "direct">>({});
const searchValues = ref<Record<string, string>>({});
const debouncedSearchValues = ref<Record<string, string>>({});

const isDiseaseNode = computed(() => nodeCategory === "biolink:Disease");

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
  color: #888; /* muted grey */
  font-size: 0.875rem;
  white-space: nowrap;
}
</style>
