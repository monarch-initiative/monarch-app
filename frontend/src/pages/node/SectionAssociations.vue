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
          :class="{ active: (selectedTabs[category.id] || 'all') === 'all' }"
          @click="setDirect(category.id, 'false')"
        >
          All Associations
        </button>
        <button
          :class="{ active: selectedTabs[category.id] === 'direct' }"
          @click="setDirect(category.id, 'true')"
        >
          Direct Associations
        </button>
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
import { computed, ref, watch } from "vue";
import { startCase } from "lodash";
import type { Node } from "@/api/model";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import type { Option, Options } from "@/components/AppSelectSingle.vue";
import AppTextbox from "@/components/AppTextbox.vue";
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
