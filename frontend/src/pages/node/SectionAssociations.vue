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
      <div class="association-tabs">
        <AppButton
          :class="[
            'app-button',
            { active: (selectedTabs[category.id] || 'all') === 'all' },
          ]"
          @click="setDirect(category.id, 'false')"
          text=" All Associations"
          color="none"
        >
        </AppButton>
        <AppButton
          :class="[
            'app-button',
            { active: selectedTabs[category.id] === 'direct' },
          ]"
          @click="setDirect(category.id, 'true')"
          :disabled="
            isLoadingDirectCount ||
            !hasDirectAssociationsForCategory(category.id)
          "
          text="Direct Associations"
          color="none"
        >
        </AppButton>
      </div>

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
          :direct="{
            id: selectedTabs[category.id] === 'direct' ? 'true' : 'false',
            label:
              selectedTabs[category.id] === 'direct'
                ? 'directly'
                : 'including sub-classes',
          }"
          :search="debouncedSearchValues[category.id]"
        />
      </template>
    </AppSection>
    <!-- details viewer of association -->
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
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

const selectedTabs = ref<Record<string, "all" | "direct">>({});
const searchValues = ref<Record<string, string>>({});
const debouncedSearchValues = ref<Record<string, string>>({});

/** list of options for dropdown */
const categoryOptions = computed(
  (): Options =>
    props.node.association_counts?.map((association_count) => ({
      id: association_count.category || "",
      label: startCase(association_count.label),
      count: association_count.count,
    })) || [],
);

function setDirect(categoryId: string, directId: "true" | "false") {
  selectedTabs.value[categoryId] = directId === "true" ? "direct" : "all";
}
// // Initialize a query for fetching direct association facet counts per category for a node.
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
function hasDirectAssociationsForCategory(categoryId: string): boolean {
  return directFacetData.value.facet_counts.some(
    (item) => item.label === categoryId && item.count > 0,
  );
}

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

  .app-button {
    z-index: 0;
    position: relative;
    margin-right: 0.25rem;
    padding: 0.8rem 1.5rem;
    border: none;
    border-radius: 8px 8px 0 0;
    background-color: $light-gray;

    &.active {
      z-index: 1;
      background-color: $theme;
      box-shadow: 0 3px 0 0 $theme; // gives the illusion of continuing the border
      color: white;
    }
  }
  :deep(.app-button) {
    &:hover {
      outline: none !important;
      box-shadow: none !important;
    }
    &:focus {
      outline: none !important;
      box-shadow: none !important;
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
</style>
