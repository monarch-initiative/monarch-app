<!--
  Section wrapper for Case-Phenotype Grid visualization on disease pages.
  Shows cases (from phenopackets) with their phenotypes grouped by body system.
-->

<template>
  <!-- Render for diseases, hide after load if no cases -->
  <AppSection
    v-if="node.category === 'biolink:Disease' && !hideSection"
    width="full"
    class="inset"
    alignment="left"
  >
    <AppHeading icon="table-cells">Case Phenotypes</AppHeading>

    <!-- Loading state -->
    <AppStatus v-if="isLoading" code="loading">
      Loading case phenotype data
    </AppStatus>

    <!-- Error state -->
    <AppStatus v-else-if="isError" code="error">
      Error loading case phenotype data
    </AppStatus>

    <!-- Grid content -->
    <template v-else-if="matrix">
      <p class="description">
        Phenotypes observed in {{ matrix.totalCases }} case{{
          matrix.totalCases !== 1 ? "s" : ""
        }}
        associated with {{ node.name }}, grouped by body system.
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
} from "@/api/case-phenotype-types";
import type { Node } from "@/api/model";
import CasePhenotypeGrid from "@/components/CasePhenotypeGrid.vue";
import CasePhenotypeModal from "@/components/CasePhenotypeModal.vue";
import { useQuery } from "@/composables/use-query";

const route = useRoute();

type Props = {
  /** current node */
  node: Node;
};

const props = defineProps<Props>();

/** Modal state */
const showModal = ref(false);
const selectedCase = ref<CaseEntity | null>(null);
const selectedPhenotype = ref<CasePhenotype | null>(null);
const selectedCellData = ref<CasePhenotypeCellData | null>(null);

/** Fetch matrix data */
const {
  query: runGetMatrix,
  data: matrix,
  isLoading,
  isError,
  isSuccess,
} = useQuery(async function () {
  return await getCasePhenotypeMatrix(props.node.id || "", props.node.name);
}, null);

/** Hide section if loading finished and no data */
const hideSection = computed(() => isSuccess.value && !matrix.value);

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

/** Refetch when route or node changes */
watch([() => route.path, () => props.node.id], runGetMatrix, {
  immediate: true,
});
</script>

<style lang="scss" scoped>
.description {
  margin-bottom: 1rem;
  color: var(--dark-gray);
}

.no-data {
  color: var(--dark-gray);
  font-style: italic;
}
</style>
