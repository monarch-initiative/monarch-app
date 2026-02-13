<template>
  <div class="controls">
    <div>
      <template v-if="showControls">
        <span>Per page</span>
        <AppSelectSingle
          name="Rows per page"
          :options="[
            { id: '5' },
            { id: '10' },
            { id: '20' },
            { id: '50' },
            { id: '100' },
            { id: '500' },
          ]"
          :model-value="{ id: String(perPage || 5) }"
          @update:model-value="(value) => emitPerPage(value.id)"
        />
      </template>
    </div>

    <div>
      <template v-if="showControls">
        <AppButton
          v-tooltip="'Go to first page'"
          :disabled="start <= 0"
          icon="angles-left"
          design="small"
          @click="clickFirst"
        />
        <AppButton
          v-tooltip="'Go to previous page'"
          :disabled="start - perPage < 0"
          icon="angle-left"
          design="small"
          @click="clickPrev"
        />
      </template>
      <template v-if="total > 0">
        <span v-if="showControls"
          >{{ start + 1 }} &mdash; {{ end }} of {{ total }}</span
        >
        <span v-else>{{ total }} row(s)</span>
      </template>
      <span v-else>no data</span>
      <template v-if="showControls">
        <AppButton
          v-tooltip="'Go to next page'"
          :disabled="start + perPage >= total"
          icon="angle-right"
          design="small"
          @click="clickNext"
        />
        <AppButton
          v-tooltip="'Go to last page'"
          :disabled="start + perPage >= total"
          icon="angles-right"
          design="small"
          @click="clickLast"
        />
      </template>
    </div>

    <div>
      <AppButton
        v-tooltip="'Download table data'"
        icon="download"
        design="small"
        @click="emitDownload"
      />
    </div>
  </div>
</template>

<script setup lang="ts" generic="Datum extends object">
import { computed } from "vue";
import AppSelectSingle from "./AppSelectSingle.vue";

type Props = {
  /** list of table rows, i.e. the table data */
  rows: Datum[];
  /** items per page (two-way bound) */
  perPage?: number;
  /** starting item index (two-way bound) */
  start?: number;
  /** total number of items */
  total?: number;
  /**
   * whether to show certain controls (temp solution, needed b/c this is a
   * controlled component and cannot paginate/search/etc on its own where needed
   * yet)
   */
  showControls?: boolean;
};

const props = withDefaults(defineProps<Props>(), {
  perPage: 5,
  start: 0,
  total: 0,
  showControls: true,
});

type Emits = {
  /** when per page changes (two-way bound) */
  "update:perPage": [Props["perPage"]];
  /** when start row changes (two-way bound) */
  "update:start": [Props["start"]];
  /** when user requests download */
  download: [];
};

const emit = defineEmits<Emits>();

function updateStart(newStart: number) {
  emit("update:start", newStart);
}

/** when user clicks to first page */
function clickFirst() {
  emit("update:start", 0);
}

/** when user clicks to previous page */
function clickPrev() {
  emit("update:start", props.start - props.perPage);
}

/** when user clicks to next page */
function clickNext() {
  emit("update:start", props.start + props.perPage);
}

/** when user clicks to last page */
function clickLast() {
  emit("update:start", Math.floor(props.total / props.perPage) * props.perPage);
}

/** when user changes rows per page */
function emitPerPage(value: string) {
  emit("update:perPage", Number(value));
  updateStart(0);
}

/** when user clicks download */
function emitDownload() {
  emit("download");
}

/** ending item index */
const end = computed((): number => props.start + props.rows.length);
</script>

<style scoped>
.controls {
  display: flex;
  justify-content: space-between;
  gap: 20px 40px;
}

.controls {
  display: flex;
  justify-content: space-between;
  gap: 20px 40px;

  & > * {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
  }

  @media (max-width: 850px) {
    flex-direction: column;
  }
}
</style>
