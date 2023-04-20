<!--
  raw/controlled table component. takes pre-sorted/filtered/paginated/etc data
  from parent and simply displays it, with minimal logic

  references:
  https://adamlynch.com/flexible-data-tables-with-css-grid/
-->

<template>
  <div class="container">
    <!-- table data -->
    <AppFlex direction="col">
      <div
        ref="table"
        class="wrapper"
        :data-left="arrivedState.left"
        :data-right="arrivedState.right"
        :data-expanded="expanded"
      >
        <table
          class="table"
          :aria-colcount="cols.length"
          :aria-rowcount="rows.length"
          :style="{ gridTemplateColumns: widths }"
        >
          <!-- head -->
          <thead class="thead">
            <tr class="tr">
              <th
                v-for="(col, colIndex) in cols"
                :key="colIndex"
                class="th"
                :aria-sort="ariaSort"
                :data-align="col.align || 'left'"
                :data-divider="col.id === 'divider'"
              >
                <span>
                  {{ col.heading }}
                </span>
                <AppButton
                  v-if="col.sortable"
                  v-tooltip="'Sort by ' + col.heading"
                  :icon="
                    'arrow-' + (sort?.id === col.id ? sort?.direction : 'down')
                  "
                  design="small"
                  :color="sort?.id === col.id ? 'primary' : 'secondary'"
                  :style="{ opacity: sort?.id === col.id ? 1 : 0.35 }"
                  @click.stop="emitSort(col)"
                />
                <AppSelectMulti
                  v-if="
                    availableFilters &&
                    activeFilters &&
                    availableFilters[col.id] &&
                    activeFilters[col.id] &&
                    availableFilters[col.id]?.length
                  "
                  v-tooltip="'Filter by ' + col.heading"
                  :name="'Filter by ' + col.heading"
                  :options="availableFilters[col.id]"
                  :model-value="activeFilters[col.id]"
                  design="small"
                  @change="(value) => emitFilter(col.id, value)"
                />
              </th>
            </tr>
          </thead>

          <!-- body -->
          <tbody class="tbody">
            <tr v-for="(row, rowIndex) in rows" :key="rowIndex" class="tr">
              <td
                v-for="(col, colIndex) in cols"
                :key="colIndex"
                class="td"
                :aria-rowindex="rowIndex + 1"
                :aria-colindex="colIndex + 1"
                :data-align="col.align || 'left'"
                :data-divider="col.id === 'divider'"
              >
                <!-- if slot w/ name == col id, use to custom format/template cell -->
                <slot
                  v-if="$slots[col.id]"
                  :name="col.id"
                  :row="row"
                  :col="col"
                  :cell="col.key ? row[col.key] : {}"
                />
                <!-- otherwise, just display raw cell value -->
                <template v-else-if="col.key">
                  {{ row[col.key] }}
                </template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="controls">
        <!-- left side controls -->
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

        <!-- center controls -->
        <div>
          <template v-if="showControls">
            <AppButton
              v-tooltip="'Go to first page'"
              :disabled="start <= 0"
              icon="angle-double-left"
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
              icon="angle-double-right"
              design="small"
              @click="clickLast"
            />
          </template>
        </div>

        <!-- right side controls -->
        <div>
          <AppTextbox
            v-if="showControls"
            v-tooltip="'Search table data'"
            class="search"
            icon="search"
            :model-value="search"
            @debounce="emitSearch"
            @change="emitSearch"
          />
          <AppButton
            v-tooltip="'Download table data'"
            icon="download"
            design="small"
            @click="emitDownload"
          />
          <AppButton
            v-tooltip="
              expanded ? 'Collapse table' : 'Expand table to full width'
            "
            :icon="expanded ? 'minimize' : 'maximize'"
            design="small"
            @click="expanded = !expanded"
          />
        </div>
      </div>
    </AppFlex>
  </div>
</template>

<script lang="ts">
/** Table column */
export type Col = {
  /**
   * Unique id, used to identify/match for sorting, filtering, and named slots.
   * use "divider" to create vertical divider to separate cols
   */
  id: string;
  /** What item in row object to access as raw cell value */
  key?: string;
  /** Header display text */
  heading?: string;
  /** How to align column contents (both header and body) horizontally */
  align?: "left" | "center" | "end";
  /**
   * Width to apply to heading cell, in any valid css grid col width (px, fr,
   * auto, minmax, etc)
   */
  width?: string;
  /** Whether to allow sorting of column */
  sortable?: boolean;
}

/** Object with arbitrary keys */
// eslint-disable-next-line
export type Row = Record<string | number, any>;

/** Arrays of rows and cols */
export type Cols = Array<Col>;
export type Rows = Array<Row>;

/** Sort prop */
export type Sort = {
  id: string;
  direction: "up" | "down";
} | null;
</script>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from "vue";
import { useResizeObserver, useScroll } from "@vueuse/core";
import type { Filters } from "@/api/facets";
import type { Options } from "./AppSelectMulti.vue";
import AppSelectMulti from "./AppSelectMulti.vue";
import AppSelectSingle from "./AppSelectSingle.vue";
import AppTextbox from "./AppTextbox.vue";
import { closeToc } from "./TheTableOfContents.vue";

type Props = {
  /** Info for each column of table */
  cols: Cols;
  /** List of table rows, i.e. the table data */
  rows: Rows;
  /** Sort key and direction */
  sort?: Sort;
  /** Filters */
  availableFilters?: Filters;
  activeFilters?: Filters;
  /** Items per page (two-way bound) */
  perPage?: number;
  /** Starting item index (two-way bound) */
  start?: number;
  /** Total number of items */
  total?: number;
  /** Text being searched (two-way bound) */
  search?: string;
  /**
   * Whether to show certain controls (temp solution, needed b/c this is a
   * controlled component and cannot paginate/search/etc on its own where needed
   * yet)
   */
  showControls?: boolean;
};

const props = withDefaults(defineProps<Props>(), {
  sort: undefined,
  availableFilters: undefined,
  activeFilters: undefined,
  perPage: 5,
  start: 0,
  total: 0,
  search: "",
  showControls: true,
});

type Emits = {
  /** When sort changes */
  (event: "sort", sort: Sort): void;
  /** When filter changes */
  (event: "filter", colId: Col["id"], value: Options): void;
  /** When per page changes (two-way bound) */
  (event: "update:perPage", value: number): void;
  /** When start row changes (two-way bound) */
  (event: "update:start", row: number): void;
  /** When search changes (two-way bound) */
  (event: "update:search", value: string): void;
  /** When user requests download */
  (event: "download"): void;
}

const emit = defineEmits<Emits>();

/** Whether table is expanded to be full width */
const expanded = ref(false);
/** Table reference */
const table = ref<HTMLElement | null>(null);

/** Table scroll state */
const { arrivedState } = useScroll(table, { offset: { left: 10, right: 10 } });

/** Force table scroll to update */
async function updateScroll() {
  await nextTick();
  table.value?.dispatchEvent(new Event("scroll"));
}
onMounted(updateScroll);
watch(expanded, updateScroll);
useResizeObserver(table, updateScroll);

/** Close table of contents when expanding */
watch(expanded, () => {
  if (expanded.value) closeToc();
});

/** When user clicks to first page */
function clickFirst() {
  emit("update:start", 0);
}

/** When user clicks to previous page */
function clickPrev() {
  emit("update:start", props.start - props.perPage);
}

/** When user clicks to next page */
function clickNext() {
  emit("update:start", props.start + props.perPage);
}

/** When user clicks to last page */
function clickLast() {
  emit("update:start", Math.floor(props.total / props.perPage) * props.perPage);
}

/** When user clicks a sort button */
function emitSort(col: Col) {
  let newSort: Sort;

  /** Toggle sort direction */
  if (props.sort?.id === col.id) {
    if (props.sort?.direction === "down")
      newSort = { id: col.id, direction: "up" };
    else if (props.sort?.direction === "up") {
      newSort = null;
    } else {
      newSort = { id: col.id, direction: "down" };
    }
  } else {
    newSort = { id: col.id, direction: "down" };
  }

  emit("sort", newSort);
}

/** When user changes a filter */
function emitFilter(colId: Col["id"], value: Options) {
  emit("filter", colId, value);
}

/** When user changes rows per page */
function emitPerPage(value: string) {
  emit("update:perPage", Number(value));
  emit("update:start", 0);
}

/** When user types in search */
function emitSearch(value: string) {
  emit("update:search", value);
  emit("update:start", 0);
}

/** When user clicks download */
function emitDownload() {
  emit("download");
}

/** Ending item index */
const end = computed((): number => props.start + props.rows.length);

/** Grid column template widths */
const widths = computed((): string =>
  props.cols.map((col) => col.width || "auto").join(" ")
);

/** Aria sort direction attribute */
const ariaSort = computed(() => {
  if (props.sort?.direction === "up") return "ascending";
  if (props.sort?.direction === "down") return "descending";
  return "none";
});
</script>

<style lang="scss" scoped>
.container {
  width: 100%;
}

.wrapper {
  width: 100%;
  overflow-x: auto;
  transition: mask-image $fast;

  &[data-left="false"][data-right="true"] {
    --webkit-mask-image: linear-gradient(to left, black 90%, transparent);
    mask-image: linear-gradient(to left, black 90%, transparent);
  }

  &[data-right="false"][data-left="true"] {
    --webkit-mask-image: linear-gradient(to right, black 90%, transparent);
    mask-image: linear-gradient(to right, black 90%, transparent);
  }

  &[data-left="false"][data-right="false"] {
    --webkit-mask-image: linear-gradient(
      to left,
      transparent,
      black 10%,
      black 90%,
      transparent
    );
    mask-image: linear-gradient(
      to left,
      transparent,
      black 10%,
      black 90%,
      transparent
    );
  }

  &[data-expanded="true"] {
    position: relative;
    left: 0;
    width: calc(100vw - 80px);
    transform: translateX(0);

    .td,
    .th {
      max-width: unset;
    }
  }
}

.table {
  display: grid;
  border-collapse: collapse;
}

/** ignore top level semantic elements in grid layout */
.thead,
.tbody,
.tr {
  display: contents;
}

/** all cells */
.th,
.td {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 5px 10px;
  max-width: 300px;

  &[data-align="left"] {
    justify-content: flex-start;
    text-align: left;
  }

  &[data-align="center"] {
    justify-content: center;
    text-align: center;
  }

  &[data-align="right"] {
    justify-content: flex-end;
    text-align: right;

    button {
      order: -1;
    }
  }

  &[data-divider="true"] {
    padding: 0;
    width: 2px;
    margin: 0 5px;
    background: $light-gray;
  }
}

/** heading cells */
.th {
  padding-bottom: 10px;
  font-weight: 400;
  text-transform: capitalize;
}

.th > span {
  font-weight: 600;
}

/** body cells */
.td {
  border-bottom: solid 2px $light-gray;
}

.controls {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  width: 100%;

  & > * {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 10px;
  }

  @media (max-width: 600px) {
    flex-direction: column;
  }

  .search {
    --height: 30px;
    max-width: 150px;
  }
}
</style>
