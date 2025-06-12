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

      <div class="association-tabs">
        <button
          :class="{ active: selectedTabs[category.id] === 'all' }"
          @click="selectedTabs[category.id] = 'all'"
        >
          All Associations
        </button>
        <button
          :class="{ active: selectedTabs[category.id] === 'direct' }"
          @click="selectedTabs[category.id] = 'direct'"
        >
          Direct Associations
        </button>
      </div>

      <div class="actions-row">
        <AppButton
          v-if="
            selectedTabs[category.id] === 'direct' &&
            ((node.category === 'biolink:Disease' &&
              category?.id.startsWith('biolink:DiseaseToPheno') &&
              (node.has_phenotype_count ?? 0) > 0) ||
              (node.category === 'biolink:Gene' &&
                category?.id.startsWith('biolink:GeneToPheno') &&
                (node.has_phenotype_count ?? 0) > 0))
          "
          v-tooltip="
            'Send these phenotypes to Phenotype Explorer for comparison'
          "
          to="/search-phenotypes"
          :state="{ search: node.id }"
          text="Phenotype Explorer"
          icon="arrow-right"
        />
        <div class="search-wrapper">
          <AppTextbox
            v-model="searchValues[category.id]"
            class="search-box"
            placeholder="Search table data..."
            @debounce="
              (value: string) => (debouncedSearchValues[category.id] = value)
            "
            @change="
              (value: string) => (debouncedSearchValues[category.id] = value)
            "
          />
        </div>
      </div>

      <template v-if="category && direct">
        <!-- table view of associations -->
        <AssociationsTable
          :node="node"
          :category="category"
          :include-orthologs="includeOrthologs"
          :direct="direct"
          :search="debouncedSearchValues[category.id] || ''"
          :selectedTab="selectedTabs[category.id] || 'all'"
          :directParam="directParamForCategory(category.id)"
        />
      </template>
    </AppSection>
    <!-- details viewer of association -->
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { startCase } from "lodash";
import type { Node } from "@/api/model";
import AppCheckbox from "@/components/AppCheckbox.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import type { Option, Options } from "@/components/AppSelectSingle.vue";
import AppTextbox from "@/components/AppTextbox.vue";
import AssociationsTable from "@/pages/node/AssociationsTable.vue";

/** route info */
const route = useRoute();

type Props = {
  /** current node */
  node: Node;
};

const selectedTabs = ref<Record<string, "all" | "direct">>({});

const props = defineProps<Props>();

const directParamForCategory = (categoryId: string) => {
  return selectedTabs.value[categoryId] === "direct"
    ? { id: "true", label: "Direct Associations" }
    : { id: undefined, label: "All Associations" };
};

const direct = ref<Option>();

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

const directOptions = computed(
  (): Options => [
    { id: "false", label: "including sub-classes" },
    { id: "true", label: "directly" },
  ],
);

watch(
  () => route.query,
  () => {
    if (!route.query.direct) {
      direct.value = directOptions.value.find(
        (option) => option.id === "false",
      ); // Set default value
    } else {
      direct.value = directOptions.value.find(
        (option) => option.id === route.query.direct,
      );
    }
  },
  { immediate: true },
);
watch(
  categoryOptions,
  (categories) => {
    categories.forEach((cat) => {
      if (!selectedTabs.value[cat.id]) {
        selectedTabs.value[cat.id] = "all";
      }
    });
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
  margin: 10px 20px 10px $toc-width + 20px !important;
}

.actions-row {
  display: flex;
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

.association-tabs {
  display: flex;
  border-bottom: 3px solid $theme;

  button {
    position: relative;
    padding: 0.9em 1.9em;
    border: none;
    background: none;
    color: #333;
    font-weight: 500;
    font-size: 1em;
    cursor: pointer;
    transition:
      background-color 0.3s ease,
      color 0.3s ease;

    &:hover {
      background-color: #f5f5f5;
    }

    &.active {
      border-radius: 5px 5px 0 0;
      background-color: $theme;
      color: white;
      font-weight: 600;

      &::after {
        display: none;
        content: "";
      }
    }

    &:not(.active) {
      background-color: #f0f0f0;
      color: #555;
      font-weight: 500;
    }
  }
}
</style>
