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

    <!-- Center controls -->
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
          :disabled="start + perPage > total"
          icon="angle-right"
          design="small"
          @click="clickNext"
        />
        <AppButton
          v-tooltip="'Go to last page'"
          :disabled="start + perPage > total"
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
import { computed, type VNode } from "vue";
import type { Options } from "./AppSelectMulti.vue";
import AppSelectSingle from "./AppSelectSingle.vue";
import AppTextbox from "./AppTextbox.vue";

/** possible keys on datum (remove number and symbol from default object type) */
type Keys = Extract<keyof Datum, string>;

type Cols<Key extends string = string> = {
  /**
   * name of slot to use for rendering. use "divider" to create vertical divider
   * to separate cols.
   */
  slot?: string;
  /**
   * what item in row object to access as raw cell value, and which key to use
   * for sorting and filtering
   */
  key?: Key;
  /** header display text */
  heading?: string;
  /** how to align column contents (both header and body) horizontally */
  align?: "left" | "center" | "right";
  /** CSS width (effectively a min width, but wont exceed `max-content`) */
  width?: string;
  /** whether to allow sorting of column */
  sortable?: boolean;
}[];
/** sort prop */
type Sort<Key extends string = string> = {
  key: Key;
  direction: "up" | "down";
} | null;

type Props = {
  /** unique id for table */
  id: string;
  /** info for each column of table */
  cols: Cols<Keys>;
  /** list of table rows, i.e. the table data */
  rows: Datum[];
  /** sort key and direction */
  sort?: Sort;
  /** filters */
  filterOptions?: { [key: string]: Options };
  selectedFilters?: { [key: string]: Options };
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
  /** height of table according to per-page */
  dynamicMinHeight?: number;
};

const props = withDefaults(defineProps<Props>(), {
  sort: undefined,
  filterOptions: undefined,
  selectedFilters: undefined,
  perPage: 5,
  start: 0,
  total: 0,
  showControls: true,
});

type Emits = {
  /** when sort changes (two-way bound) */
  "update:sort": [Props["sort"]];
  /** when selected filters change (two-way bound) */
  "update:selectedFilters": [Props["selectedFilters"]];
  /** when per page changes (two-way bound) */
  "update:perPage": [Props["perPage"]];
  /** when start row changes (two-way bound) */
  "update:start": [Props["start"]];

  /** when user requests download */
  download: [];
};

const emit = defineEmits<Emits>();

type SlotNames = string;

type SlotProps = {
  col: Cols<Keys>[number];
  row: Datum;
  cell: Datum[Keys] | null;
};

defineSlots<{
  [slot in SlotNames]: (props: SlotProps) => VNode;
}>();

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
  emit("update:start", 0);
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
