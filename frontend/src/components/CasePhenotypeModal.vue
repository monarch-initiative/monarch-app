<!--
  Modal displaying details for a case-phenotype cell in the grid
-->

<template>
  <AppModal v-model="modelValue" label="Phenotype Details">
    <div class="content">
      <div class="field">
        <span class="label">Case:</span>
        <AppNodeBadge :node="{ id: caseId, label: caseLabel }" />
      </div>

      <div class="field">
        <span class="label">Phenotype:</span>
        <AppNodeBadge :node="{ id: phenotypeId, label: phenotypeLabel }" />
      </div>

      <template v-if="cellData">
        <div class="field">
          <span class="label">Status:</span>
          <span :class="statusClass">{{ statusText }}</span>
        </div>

        <div v-if="cellData.onset" class="field">
          <span class="label">Onset:</span>
          <AppNodeBadge
            v-if="cellData.onsetId"
            :node="{ id: cellData.onsetId, label: cellData.onset }"
          />
          <span v-else>{{ cellData.onset }}</span>
        </div>

        <div v-if="cellData.frequency" class="field">
          <span class="label">Frequency:</span>
          <span>{{ cellData.frequency }}</span>
        </div>

        <div v-if="cellData.source" class="field">
          <span class="label">Source:</span>
          <span>{{ cellData.source }}</span>
        </div>

        <div
          v-if="cellData.publicationLinks && cellData.publicationLinks.length"
          class="field"
        >
          <span class="label">Publications:</span>
          <ul class="publications">
            <li
              v-for="pub in cellData.publicationLinks"
              :key="pub.id"
              class="publication"
            >
              <a v-if="pub.url" :href="pub.url" target="_blank" rel="noopener">
                {{ pub.id }}
              </a>
              <span v-else>{{ pub.id }}</span>
            </li>
          </ul>
        </div>
      </template>

      <div v-else class="no-data">
        No data for this case-phenotype combination
      </div>
    </div>
  </AppModal>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { CasePhenotypeCellData } from "@/api/case-phenotype-types";
import AppModal from "@/components/AppModal.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";

interface Props {
  modelValue: boolean;
  caseId: string;
  caseLabel?: string;
  phenotypeId: string;
  phenotypeLabel?: string;
  cellData: CasePhenotypeCellData | null;
}

const props = defineProps<Props>();

interface Emits {
  (e: "update:modelValue", value: boolean): void;
}

const emit = defineEmits<Emits>();

const modelValue = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit("update:modelValue", value),
});

const statusText = computed(() => {
  if (!props.cellData) return "";
  return props.cellData.negated ? "Excluded/Negated" : "Present";
});

const statusClass = computed(() => {
  if (!props.cellData) return "";
  return props.cellData.negated ? "status-negated" : "status-present";
});
</script>

<style lang="scss" scoped>
.content {
  display: flex;
  flex-direction: column;
  width: 100%;
  min-width: 300px;
  gap: 12px;
}

.field {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 8px;
}

.label {
  min-width: 100px;
  font-weight: 600;
}

.status-present {
  color: #2e7d32;
  font-weight: 500;
}

.status-negated {
  color: #c62828;
  font-weight: 500;
}

.publications {
  margin: 0;
  padding-left: 20px;
  list-style-type: disc;
}

.publication {
  margin: 4px 0;
}

.no-data {
  color: #666;
  font-style: italic;
}
</style>
