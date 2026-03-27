<!--
  Generic modal for displaying entity grid cell details.
  Provides slots for customizing the content display.
-->

<template>
  <AppModal v-model="modelValue" :label="modalLabel">
    <div class="content">
      <!-- Column entity field -->
      <div class="field">
        <span class="label">{{ config.columnLabel }}:</span>
        <AppNodeBadge :node="{ id: columnId, label: columnLabel }" />
      </div>

      <!-- Row entity field -->
      <div class="field">
        <span class="label">{{ config.rowLabel }}:</span>
        <AppNodeBadge :node="{ id: rowId, label: rowLabel }" />
      </div>

      <template v-if="cellData">
        <!-- Default cell details slot -->
        <slot name="cell-details" :cell-data="cellData">
          <!-- Default status display -->
          <div class="field">
            <span class="label">Status:</span>
            <span :class="statusClass">{{ statusText }}</span>
          </div>

          <!-- Qualifiers -->
          <template v-if="cellData.qualifiers">
            <div v-for="q in cellData.qualifiers" :key="q.type" class="field">
              <span class="label">{{ formatQualifierType(q.type) }}:</span>
              <AppNodeBadge v-if="q.id" :node="{ id: q.id, label: q.label }" />
              <span v-else>{{ q.label }}</span>
            </div>
          </template>

          <!-- Source -->
          <div v-if="cellData.source" class="field">
            <span class="label">Source:</span>
            <span>{{ cellData.source }}</span>
          </div>

          <!-- Publications -->
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
                <a
                  v-if="pub.url"
                  :href="pub.url"
                  target="_blank"
                  rel="noopener"
                >
                  {{ pub.id }}
                </a>
                <span v-else>{{ pub.id }}</span>
              </li>
            </ul>
          </div>
        </slot>

        <!-- Additional fields slot for use-case specific content -->
        <slot name="additional-fields" :cell-data="cellData"></slot>
      </template>

      <div v-else class="no-data">
        No data for this {{ config.columnLabel.toLowerCase() }}-{{
          config.rowLabel.toLowerCase()
        }}
        combination
      </div>
    </div>
  </AppModal>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { CellData, EntityGridConfig } from "@/api/entity-grid/types";
import AppModal from "@/components/AppModal.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";

interface Props {
  modelValue: boolean;
  columnId: string;
  columnLabel?: string;
  rowId: string;
  rowLabel?: string;
  cellData: CellData | null;
  config: EntityGridConfig;
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

const modalLabel = computed(() => `${props.config.rowLabel} Details`);

const statusText = computed(() => {
  if (!props.cellData) return "";
  return props.cellData.negated ? "Excluded/Negated" : "Present";
});

const statusClass = computed(() => {
  if (!props.cellData) return "";
  return props.cellData.negated ? "status-negated" : "status-present";
});

const formatQualifierType = (type: string): string => {
  // Capitalize first letter
  return type.charAt(0).toUpperCase() + type.slice(1);
};
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
