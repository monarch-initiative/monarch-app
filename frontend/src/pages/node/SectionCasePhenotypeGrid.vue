<!--
  Section wrapper for Case-Phenotype Grid visualization on disease pages.
  Shows cases (from phenopackets) with their phenotypes grouped by body system.

  Only shown for specific diseases, not grouping classes (determined by Mondo subsets).
  Also limited to diseases with <= 1000 cases to avoid performance issues.
-->

<template>
  <!-- Render for specific diseases (not grouping classes), hide after load if no cases -->
  <AppSection
    v-if="
      node.category === 'biolink:Disease' && !isGroupingClass && !hideSection
    "
    width="full"
    class="inset"
    alignment="left"
  >
    <AppHeading icon="table">Case Phenotypes</AppHeading>

    <!-- Tabs for Direct/All (hidden when limit exceeded) -->
    <AppAssociationTabs
      v-if="
        !isLoading &&
        !isError &&
        !exceedsLimit &&
        (directCount > 0 || allCount > 0)
      "
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

    <!-- Limit exceeded message -->
    <p v-else-if="exceedsLimit" class="limit-message">
      This disease has {{ allCount }} associated cases, which exceeds the
      display limit of {{ MAX_CASES_LIMIT }}. The grid visualization is only
      shown for diseases with fewer cases.
    </p>

    <!-- Grid content -->
    <template v-else-if="matrix">
      <p class="description">
        Phenotypes observed in {{ matrix.totalCases }} case{{
          matrix.totalCases !== 1 ? "s" : ""
        }}
        {{ selectedTab === "direct" ? "directly" : "" }} associated with
        {{ node.name
        }}{{ selectedTab === "all" ? " (including sub-diseases)" : "" }},
        grouped by body system.
      </p>

      <CasePhenotypeGrid :matrix="matrix" @cell-click="handleCellClick" />

      <!-- Detail modal -->
      <CasePhenotypeModal
        v-model="showModal"
        :case-id="selectedCase?.id || ''"
        :case-label="selectedCase?.label"
        :phenotype-id="selectedPhenotype?.id || ''"
        :phenotype-label="selectedPhenotype?.label"
        :cell-data="selectedCellData"
      />
    </template>
  </AppSection>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import {
  CaseLimitExceededError,
  getCaseCounts,
  getCasePhenotypeMatrix,
} from "@/api/case-phenotype";
import type {
  CaseEntity,
  CasePhenotype,
  CasePhenotypeCellData,
  CasePhenotypeMatrix,
} from "@/api/case-phenotype-types";
import type { Node } from "@/api/model";
import AppAssociationTabs from "@/components/AppAssociationTabs.vue";
import CasePhenotypeGrid from "@/components/CasePhenotypeGrid.vue";
import CasePhenotypeModal from "@/components/CasePhenotypeModal.vue";

const route = useRoute();

type Props = {
  /** current node */
  node: Node;
};

const props = defineProps<Props>();

/**
 * Maximum number of cases to display in the grid. Diseases with more cases than
 * this limit are typically high-level grouping terms where the grid becomes
 * unwieldy and expensive to render. The limit also reduces backend load by
 * skipping the expensive phenotype fetching for large case sets.
 */
const MAX_CASES_LIMIT = 1000;

/**
 * Subset markers that indicate a disease is a grouping class (not a specific
 * diagnosable entity). These are curated by Mondo/Orphanet to distinguish
 * organizational categories from actual diseases.
 */
const GROUPING_SUBSET_MARKERS = [
  "disease_grouping",
  "ordo_group_of_disorders",
  "rare_grouping",
];

/**
 * Check if this disease is a grouping class based on Mondo subsets. Grouping
 * classes are organizational categories (like "Ehlers-Danlos syndrome") rather
 * than specific diagnosable diseases (like "Ehlers-Danlos syndrome,
 * hypermobility type").
 */
const isGroupingClass = computed(() => {
  // subsets is an array, often with a single pipe-delimited string
  const subsets = props.node.subsets ?? [];
  // Parse pipe-delimited values and flatten
  const allSubsets = subsets.flatMap((s) => s.split("|"));
  return allSubsets.some((s) => GROUPING_SUBSET_MARKERS.includes(s));
});

/** Tab state */
const selectedTab = ref<"direct" | "all">("direct");
const directCount = ref(0);
const allCount = ref(0);

/** Loading and error state */
const isLoading = ref(false);
const isError = ref(false);
const errorMessage = ref<string | null>(null);

/** Matrix data */
const matrix = ref<CasePhenotypeMatrix | null>(null);

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

/** Handle tab selection */
function handleTabSelect(which: "direct" | "all") {
  selectedTab.value = which;
}

/** Modal state */
const showModal = ref(false);
const selectedCase = ref<CaseEntity | null>(null);
const selectedPhenotype = ref<CasePhenotype | null>(null);
const selectedCellData = ref<CasePhenotypeCellData | null>(null);

/** Fetch case counts for both tabs */
async function fetchCounts() {
  try {
    const counts = await getCaseCounts(props.node.id || "");
    directCount.value = counts.direct;
    allCount.value = counts.all;

    // Default to "all" tab if no direct cases but there are descendant cases
    if (counts.direct === 0 && counts.all > 0) {
      selectedTab.value = "all";
    } else {
      // Reset to direct if we have direct cases
      selectedTab.value = "direct";
    }
  } catch (e) {
    console.error("Failed to fetch case counts:", e);
    directCount.value = 0;
    allCount.value = 0;
  }
}

/** Fetch matrix data using the new single-endpoint API */
async function fetchMatrix() {
  isLoading.value = true;
  isError.value = false;
  errorMessage.value = null;
  matrix.value = null;

  try {
    const isDirect = selectedTab.value === "direct";
    matrix.value = await getCasePhenotypeMatrix(props.node.id || "", {
      direct: isDirect,
      limit: MAX_CASES_LIMIT,
    });
  } catch (e) {
    isError.value = true;
    if (e instanceof CaseLimitExceededError) {
      errorMessage.value =
        `This disease has ${e.actual} cases, which exceeds the display limit. ` +
        `Switch to "Direct" tab to see only directly-annotated cases.`;
    } else {
      errorMessage.value =
        e instanceof Error ? e.message : "Failed to load data";
    }
  } finally {
    isLoading.value = false;
  }
}

/** Check if case count exceeds our display limit */
const exceedsLimit = computed(() => allCount.value > MAX_CASES_LIMIT);

/** Hide section if loading finished and no data in either tab */
const hideSection = computed(
  () => !isLoading.value && !isError.value && allCount.value === 0,
);

/** Handle cell click to open modal */
function handleCellClick(
  caseId: string,
  phenotypeId: string,
  cellData: CasePhenotypeCellData | null,
) {
  if (!matrix.value) return;

  // Find case and phenotype info
  selectedCase.value = matrix.value.cases.find((c) => c.id === caseId) || null;
  selectedPhenotype.value =
    matrix.value.phenotypes.find((p) => p.id === phenotypeId) || null;
  selectedCellData.value = cellData;

  showModal.value = true;
}

/** Refetch when route or node changes, but skip for grouping classes */
watch(
  [() => route.path, () => props.node.id],
  async () => {
    if (!isGroupingClass.value) {
      await fetchCounts();
      // Skip expensive matrix fetch if case count exceeds limit
      if (allCount.value <= MAX_CASES_LIMIT) {
        fetchMatrix();
      }
    }
  },
  { immediate: true },
);

/** Refetch matrix when tab changes, but only if within limit */
watch(selectedTab, () => {
  if (allCount.value <= MAX_CASES_LIMIT) {
    fetchMatrix();
  }
});
</script>

<style lang="scss" scoped>
.description {
  margin-bottom: 1rem;
  color: var(--dark-gray);
}

.limit-message {
  color: var(--dark-gray);
  font-style: italic;
}

.no-data {
  color: var(--dark-gray);
  font-style: italic;
}
</style>
