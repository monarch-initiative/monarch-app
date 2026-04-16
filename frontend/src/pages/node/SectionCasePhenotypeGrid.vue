<!--
  Section wrapper for Case-Phenotype Grid visualization on disease pages.
  Shows cases (from phenopackets) with their phenotypes grouped by body system.

  Only shown for specific diseases, not grouping classes (determined by Mondo subsets).
  Silently hidden for diseases with 0 cases or > 100 cases (uses association_counts
  from the node to avoid expensive API calls for high-level disease terms).
-->

<template>
  <!--
    Only render for diseases that:
    - Are biolink:Disease category
    - Are not grouping classes (based on Mondo subsets)
    - Have 1-100 cases (from association_counts - no expensive API needed to check)
  -->
  <AppSection
    v-if="
      node.category === 'biolink:Disease' &&
      !isGroupingClass &&
      caseCountFromAssociations > 0 &&
      caseCountFromAssociations <= MAX_CASES_LIMIT
    "
    width="full"
    class="inset"
    alignment="left"
  >
    <AppHeading icon="table">Case Phenotypes</AppHeading>

    <!-- Tabs for Direct/All -->
    <AppAssociationTabs
      v-if="!isLoading && !isError && (directCount > 0 || allCount > 0)"
      :has-direct-associations="directCount > 0"
      :show-all-tab="allCount > directCount"
      :direct-active="selectedTab === 'direct'"
      :all-active="selectedTab === 'all'"
      :direct-label="directTabLabel"
      :inferred-label="allTabLabel"
      :direct-tooltip="directTooltip"
      :inferred-tooltip="allTooltip"
      @select="handleTabSelect"
    />

    <!-- Loading state -->
    <AppStatus v-if="isLoading" code="loading">
      Loading case phenotype data
    </AppStatus>

    <!-- Error state -->
    <AppStatus v-else-if="isError" code="error">
      {{ errorMessage || "Error loading case phenotype data" }}
    </AppStatus>

    <!-- Grid content -->
    <template v-else-if="matrix">
      <p class="description">
        Phenotypes observed in {{ matrix.totalColumns }} case{{
          matrix.totalColumns !== 1 ? "s" : ""
        }}
        {{ selectedTab === "direct" ? "directly" : "" }} associated with
        {{ node.name
        }}{{ selectedTab === "all" ? " (including sub-diseases)" : "" }},
        grouped by body system.
      </p>

      <EntityGrid
        :matrix="matrix"
        :config="gridConfig"
        @cell-click="handleCellClick"
      />

      <!-- Detail modal -->
      <EntityGridModal
        v-model="showModal"
        :column-id="selectedColumn?.id || ''"
        :column-label="selectedColumn?.label"
        :row-id="selectedRow?.id || ''"
        :row-label="selectedRow?.label"
        :cell-data="selectedCellData"
        :config="gridConfig"
      />
    </template>
  </AppSection>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { getEntityGrid } from "@/api/entity-grid";
import type {
  CellData,
  ColumnEntity,
  EntityGridConfig,
  EntityGridMatrix,
  RowEntity,
} from "@/api/entity-grid/types";
import type { Node } from "@/api/model";
import AppAssociationTabs from "@/components/AppAssociationTabs.vue";
import EntityGrid from "@/components/EntityGrid/EntityGrid.vue";
import EntityGridModal from "@/components/EntityGrid/EntityGridModal.vue";
import { checkIsGroupingClass } from "@/util/groupingClassUtils";

const route = useRoute();

type Props = {
  /** current node */
  node: Node;
};

const props = defineProps<Props>();

/**
 * Maximum number of cases to display in the grid. We use association_counts
 * (already loaded with the node) to gate whether to show this section at all,
 * avoiding expensive API calls for high-level disease terms with many cases.
 */
const MAX_CASES_LIMIT = 100;

/**
 * Get case count from node's association_counts. This is already loaded with
 * the node data, so no additional API call needed. Returns 0 if not found.
 */
const caseCountFromAssociations = computed(() => {
  const caseAssoc = props.node.association_counts?.find(
    (a) => a.category === "biolink:CaseToDiseaseAssociation",
  );
  return caseAssoc?.count ?? 0;
});

/**
 * Check if this disease is a grouping class based on Mondo subsets. Grouping
 * classes are organizational categories (like "Ehlers-Danlos syndrome") rather
 * than specific diagnosable diseases (like "Ehlers-Danlos syndrome,
 * hypermobility type").
 */
const isGroupingClass = computed(() =>
  checkIsGroupingClass(props.node.subsets ?? []),
);

/** Grid config for case-phenotype display */
const gridConfig: EntityGridConfig = {
  columnLabel: "Case",
  columnLabelPlural: "Cases",
  rowLabel: "Phenotype",
  rowLabelPlural: "Phenotypes",
  binLabel: "System",
  cellDisplayMode: "binary",
  showNegated: true,
  columnTooltipFormatter: (column: ColumnEntity, index: number): string => {
    let html = `<strong>Case ${index + 1}</strong>`;
    if (column.label) {
      html += `<br>${column.label}`;
    }
    html += `<br><small>${column.id}</small>`;

    // Show source disease if from a descendant (not direct)
    if (!column.isDirect && column.sourceEntityLabel) {
      html += `<br><br><em>Disease: ${column.sourceEntityLabel}</em>`;
    }

    return html;
  },
};

/** Tab state */
const selectedTab = ref<"direct" | "all">("direct");

/**
 * Direct count is derived from the matrix after fetching. We count columns
 * where isDirect is true.
 */
const directCount = computed(() => {
  if (!matrix.value) return 0;
  return matrix.value.columns.filter((c) => c.isDirect).length;
});

/** All count comes from association_counts (includes descendants). */
const allCount = computed(() => caseCountFromAssociations.value);

/** Loading and error state */
const isLoading = ref(false);
const isError = ref(false);
const errorMessage = ref<string | null>(null);

/** Matrix data */
const matrix = ref<EntityGridMatrix | null>(null);

/** Tab labels */
const directTabLabel = computed(() => `Direct (${directCount.value})`);
const allTabLabel = computed(() => `All (${allCount.value})`);

/** Tab tooltips */
const directTooltip = computed(
  () =>
    `${directCount.value} cases directly associated with ${props.node.name}`,
);
const allTooltip = computed(() => {
  const inferredCount = allCount.value - directCount.value;
  return `${allCount.value} total cases including ${inferredCount} from sub-diseases`;
});

/** Handle tab selection - user clicked a tab */
function handleTabSelect(which: "direct" | "all") {
  selectedTab.value = which;
  fetchMatrix();
}

/** Modal state */
const showModal = ref(false);
const selectedColumn = ref<ColumnEntity | null>(null);
const selectedRow = ref<RowEntity | null>(null);
const selectedCellData = ref<CellData | null>(null);

/** Fetch matrix data from the backend API */
async function fetchMatrix() {
  isLoading.value = true;
  isError.value = false;
  errorMessage.value = null;
  matrix.value = null;

  try {
    const isDirect = selectedTab.value === "direct";
    const result = await getEntityGrid(props.node.id || "", {
      columnAssociationCategory: ["biolink:CaseToDiseaseAssociation"],
      rowAssociationCategory: ["biolink:CaseToPhenotypicFeatureAssociation"],
      direct: isDirect,
      limit: MAX_CASES_LIMIT,
    });

    // If direct tab has no columns but there are descendant cases, switch to all
    // and fetch again immediately. New API returns {totalColumns: 0} instead of null.
    if (isDirect && result.totalColumns === 0) {
      if (caseCountFromAssociations.value > 0) {
        selectedTab.value = "all";
        // Fetch again with all cases
        matrix.value = await getEntityGrid(props.node.id || "", {
          columnAssociationCategory: ["biolink:CaseToDiseaseAssociation"],
          rowAssociationCategory: [
            "biolink:CaseToPhenotypicFeatureAssociation",
          ],
          direct: false,
          limit: MAX_CASES_LIMIT,
        });
        return; // Exit early, finally block will run
      }
    }

    matrix.value = result.totalColumns > 0 ? result : null;
  } catch (e) {
    isError.value = true;
    errorMessage.value = e instanceof Error ? e.message : "Failed to load data";
  } finally {
    isLoading.value = false;
  }
}

/** Handle cell click to open modal */
function handleCellClick(
  columnId: string,
  rowId: string,
  cellData: CellData | null,
) {
  if (!matrix.value) return;

  // Find column and row info
  selectedColumn.value =
    matrix.value.columns.find((c) => c.id === columnId) || null;
  selectedRow.value = matrix.value.rows.find((r) => r.id === rowId) || null;
  selectedCellData.value = cellData;

  showModal.value = true;
}

/**
 * Fetch matrix on mount. The section is only rendered if
 * caseCountFromAssociations is in [1, MAX_CASES_LIMIT], so we know it's safe to
 * fetch when mounted.
 */
onMounted(() => {
  fetchMatrix();
});

/** Refetch when navigating to a different disease */
watch([() => route.path, () => props.node.id], () => {
  fetchMatrix();
});
</script>

<style lang="scss" scoped>
.description {
  margin-bottom: 1rem;
  color: var(--dark-gray);
}
</style>
