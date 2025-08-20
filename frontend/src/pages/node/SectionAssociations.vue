<!--
  node page associations section
-->

<template>
  <!-- show an AppSection for each category in categoryOptions  -->
  <div v-for="category in categoryOptions" :key="category.id">
    <!-- Association table -->
    <AppSection alignment="left" width="full" class="inset">
      <AppHeading :level="3">{{
        sectionTitle(category.id, category.label)
      }}</AppHeading>
      <span v-if="!categoryOptions.length"
        >No associations with &nbsp;<AppNodeBadge :node="node" />
      </span>

      <!--tabs omly if its disease node-->
      <AppAssociationTabs
        v-if="isDiseaseNode"
        :has-direct-associations="hasDirectAssociationsForCategory(category.id)"
        :show-all-tab="showAllTab(category.count ?? 0, category.id)"
        :direct-active="
          (selectedTabs[category.id] ?? defaultTab(category.id)) === 'direct'
        "
        :all-active="
          (selectedTabs[category.id] ?? defaultTab(category.id)) === 'all'
        "
        :direct-label="tabLabel(category.id, 'direct')"
        :inferred-label="tabLabel(category.id, 'inferred')"
        :direct-tooltip="directTooltip(category.id)"
        :inferred-tooltip="inferredTooltip(category.id)"
        @select="
          (which: string) =>
            setDirect(category.id, which === 'direct' ? 'true' : 'false')
        "
      />

      <div class="actions-row">
        <AppButton
          v-if="
            (hasTotals(category.id) &&
              activeTabIsDirect(category.id) &&
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
          @totals="(p) => onTotals({ categoryId: String(category.id), ...p })"
          @inferred-label="onInferredLabel"
        />
      </template>
    </AppSection>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import type { Node } from "@/api/model";
import AppAssociationTabs from "@/components/AppAssociationTabs.vue";
import AppButton from "@/components/AppButton.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppTextbox from "@/components/AppTextbox.vue";
import { useAssociationCategories } from "@/composables/use-association-categories";
import AssociationsTable from "@/pages/node/AssociationsTable.vue";
import { sectionTitle } from "@/util/sectionTitles";
import { tabLabel } from "@/util/tabText";
import { formatDirectTooltip, formatInferredTooltip } from "@/util/tooltipText";
import { labelFor } from "@/util/typeConfig";

type Props = {
  /** current node */
  node: Node;
};

const props = defineProps<Props>();

type Totals = { direct: number; all: number };
type TotalsMap = Record<string, Totals>;
const totalsByCategory = ref<TotalsMap>({});

const { category: nodeCategory } = props.node;

const selectedTabs = ref<Record<string, "all" | "direct">>({});
const searchValues = ref<Record<string, string>>({});
const debouncedSearchValues = ref<Record<string, string>>({});
const inferredByCategory = ref<Record<string, string>>({});

const { options: categoryOptions } = useAssociationCategories(props.node);

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

const directFor = (id: string) => totalsByCategory.value[id]?.direct ?? 0;
const allFor = (id: string) => totalsByCategory.value[id]?.all ?? 0;

const diffFor = (id: string) => {
  const diff = allFor(id) - directFor(id);
  return Number.isFinite(diff) ? Math.max(0, diff) : 0;
};
const hasTotals = (id: string) => totalsByCategory.value[id] !== undefined;
const activeTabIsDirect = (id: string) =>
  (selectedTabs.value[id] ?? defaultTab(id)) === "direct";

const onInferredLabel = ({
  categoryId,
  label,
}: {
  categoryId: string;
  label: string;
}) => {
  inferredByCategory.value[categoryId] = label;
};

const setDirect = (categoryId: string, directId: "true" | "false") => {
  selectedTabs.value[categoryId] = directId === "true" ? "direct" : "all";
};
const directTooltip = (categoryId: string): string | undefined => {
  return formatDirectTooltip(categoryId, {
    node: props.node.name,
    label: labelFor(categoryId),
    n: directFor(categoryId),
  });
};

const inferredTooltip = (categoryId: string): string | undefined => {
  return formatInferredTooltip(categoryId, {
    node: props.node.name,
    label: labelFor(categoryId),
    all: allFor(categoryId),
    n: directFor(categoryId),
    diff: diffFor(categoryId),
    example: inferredByCategory.value[categoryId], // optional subclass example text
  });
};

// Helper function to check if a specific category has any direct associations
const hasDirectAssociationsForCategory = (categoryId: string): boolean => {
  return directFor(categoryId) > 0;
};

const showAllTab = computed(() => {
  return (categoryCount: number, categoryId: string): boolean => {
    return categoryCount > directFor(categoryId);
  };
});

/*
 * For disease nodes, defaults to:
 *  - "all" if there are zero direct associations
 *  - "direct" otherwise
 * Non-disease nodes always default to "all".
 */

function defaultTab(categoryId: string): "direct" | "all" {
  const directCount = directFor(categoryId);
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
