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
import { getCasePhenotypeMatrix } from "@/api/case-phenotype";
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

/**
 * Direct count is derived from the matrix after fetching. We count cases where
 * isDirect is true.
 */
const directCount = computed(() => {
  if (!matrix.value) return 0;
  return matrix.value.cases.filter((c) => c.isDirect).length;
});

/** All count comes from association_counts (includes descendants). */
const allCount = computed(() => caseCountFromAssociations.value);

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

/** Fetch matrix data from the backend API */
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

    // If direct tab has no cases but there are descendant cases, switch to all
    if (isDirect && matrix.value && matrix.value.totalCases === 0) {
      if (caseCountFromAssociations.value > 0) {
        selectedTab.value = "all";
        // The tab watcher will trigger a refetch
      }
    }
  } catch (e) {
    isError.value = true;
    errorMessage.value = e instanceof Error ? e.message : "Failed to load data";
  } finally {
    isLoading.value = false;
  }
}

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

/**
 * Fetch matrix when route/node changes. The section is only rendered if
 * caseCountFromAssociations is in [1, MAX_CASES_LIMIT], so we know it's safe to
 * fetch when this component is mounted.
 */
watch(
  [() => route.path, () => props.node.id],
  () => {
    // Only fetch if we're within the display limit (template already gates this)
    if (
      !isGroupingClass.value &&
      caseCountFromAssociations.value > 0 &&
      caseCountFromAssociations.value <= MAX_CASES_LIMIT
    ) {
      fetchMatrix();
    }
  },
  { immediate: true },
);

/** Refetch matrix when tab changes */
watch(selectedTab, () => {
  fetchMatrix();
});
</script>

<style lang="scss" scoped>
.description {
  margin-bottom: 1rem;
  color: var(--dark-gray);
}
</style>
