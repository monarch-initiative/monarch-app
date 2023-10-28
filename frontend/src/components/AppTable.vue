<!--
  raw/controlled table component. takes pre-sorted/filtered/paginated/etc data
  from parent and simply displays it, with minimal logic

  references:
  https://adamlynch.com/flexible-data-tables-with-css-grid/
-->

<template>
  <!-- table data -->
  <AppFlex direction="col" :class="['container', { expanded }]">
    <div ref="scroll" class="scroll force-scrollbar">
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
              :class="[
                'th',
                col.align || 'left',
                { divider: col.slot === 'divider' },
              ]"
              :aria-sort="ariaSort"
            >
              <span>
                {{ col.heading }}
              </span>
              <AppButton
                v-if="col.sortable"
                v-tooltip="'Sort by ' + col.heading"
                :icon="
                  'arrow-' + (sort?.key === col.key ? sort?.direction : 'down')
                "
                design="small"
                :color="sort?.key === col.key ? 'primary' : 'secondary'"
                :style="{ opacity: sort?.key === col.key ? 1 : 0.35 }"
                @click.stop="emitSort(col)"
              />
              <AppSelectMulti
                v-if="
                  col.key &&
                  selectedFilters?.[col.key] &&
                  filterOptions?.[col.key]?.length
                "
                v-tooltip="'Filter by ' + col.heading"
                :name="'Filter by ' + col.heading"
                :options="filterOptions[col.key]"
                :model-value="selectedFilters[col.key]"
                design="small"
                @change="(value) => emitFilter(col.key, value)"
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
              :class="[
                'td',
                col.align || 'left',
                { divider: col.slot === 'divider' },
              ]"
              :aria-rowindex="rowIndex + 1"
              :aria-colindex="colIndex + 1"
            >
              <!-- if col has slot name, use to custom format/template cell -->
              <slot
                v-if="col.slot && $slots[col.slot]"
                :name="col.slot"
                :row="row"
                :col="col"
                :cell="col.key ? row[col.key] : null"
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

      <!-- right side controls -->
      <div>
        <AppTextbox
          v-if="showControls"
          v-tooltip="'Search table data'"
          class="search"
          icon="magnifying-glass"
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
          v-tooltip="expanded ? 'Collapse table' : 'Expand table to full width'"
          :icon="expanded ? 'minimize' : 'maximize'"
          design="small"
          @click="expanded = !expanded"
        />
      </div>
    </div>
  </AppFlex>
</template>

<script lang="ts">
/** table column */
export type Cols<Key extends string> = {
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
  /**
   * width to apply to heading cell, in any valid css grid col width (px, fr,
   * auto, minmax, etc)
   */
  width?: number;
  /** whether to allow sorting of column */
  sortable?: boolean;
}[];

/** sort prop */
export type Sort<Key extends string = string> = {
  key: Key;
  direction: "up" | "down";
} | null;
</script>

<script setup lang="ts" generic="Datum extends object">
import { computed, watch, type VNode } from "vue";
import { useLocalStorage } from "@vueuse/core";
import { useScrollable } from "@/util/composables";
import type { Options } from "./AppSelectMulti.vue";
import AppSelectMulti from "./AppSelectMulti.vue";
import AppSelectSingle from "./AppSelectSingle.vue";
import AppTextbox from "./AppTextbox.vue";
import { closeToc } from "./TheTableOfContents.vue";

/** possible keys on datum (remove number and symbol from default object type) */
type Keys = Extract<keyof Datum, string>;

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
  /** text being searched (two-way bound) */
  search?: string;
  /**
   * whether to show certain controls (temp solution, needed b/c this is a
   * controlled component and cannot paginate/search/etc on its own where needed
   * yet)
   */
  showControls?: boolean;
};

const props = withDefaults(defineProps<Props>(), {
  sort: undefined,
  filterOptions: undefined,
  selectedFilters: undefined,
  perPage: 5,
  start: 0,
  total: 0,
  search: "",
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
  /** when search changes (two-way bound) */
  "update:search": [Props["search"]];
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

/** whether table is expanded to be full width */
const expanded = useLocalStorage(`${props.id}-table-expanded`, false);

/** style scroll states */
const { ref: scroll, updateScroll } = useScrollable();
watch(expanded, updateScroll);

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

/** when user clicks a sort button */
function emitSort(col: Cols<Keys>[number]) {
  let newSort: Sort<Keys>;

  if (!col.key) return;

  /** toggle sort direction */
  if (props.sort?.key === col.key) {
    if (props.sort?.direction === "down")
      newSort = { key: col.key, direction: "up" };
    else if (props.sort?.direction === "up") {
      newSort = null;
    } else {
      newSort = { key: col.key, direction: "down" };
    }
  } else {
    newSort = { key: col.key, direction: "down" };
  }

  emit("update:sort", newSort);
}

/** when user changes a filter */
function emitFilter(colKey: Cols<Keys>[number]["key"], value: Options) {
  if (colKey)
    emit("update:selectedFilters", {
      ...props.selectedFilters,
      [colKey]: value,
    });
}

/** when user changes rows per page */
function emitPerPage(value: string) {
  emit("update:perPage", Number(value));
  emit("update:start", 0);
}

/** when user types in search */
function emitSearch(value: string) {
  emit("update:search", value);
  emit("update:start", 0);
}

/** when user clicks download */
function emitDownload() {
  emit("download");
}

/** ending item index */
const end = computed((): number => props.start + props.rows.length);

/** grid column template widths */
const widths = computed((): string =>
  props.cols
    .map((col) =>
      col.slot === "divider"
        ? "20px"
        : expanded.value
        ? `minmax(max-content, 99999px)`
        : `${col.width || 1}fr`,
    )
    .join(" "),
);

/** aria sort direction attribute */
const ariaSort = computed(() => {
  if (props.sort?.direction === "up") return "ascending";
  if (props.sort?.direction === "down") return "descending";
  return "none";
});

/** close table of contents when expanding or starting expanded */
watch(
  expanded,
  () => {
    if (expanded.value) closeToc();
  },
  { immediate: true },
);
</script>

<style lang="scss" scoped>
.container {
  &.expanded {
    left: 0;
    width: calc(100vw - 100px);
    transform: translateX(0);

    .td,
    .th {
      width: 100%;
      max-width: unset;
    }
  }
}

.scroll {
  width: 100%;
  overflow-x: auto;
}

.table {
  display: grid;
  min-width: $section;
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
  max-width: 300px;
  padding: 5px 10px;
  gap: 10px;

  &.left {
    justify-content: flex-start;
    text-align: left;
  }

  &.center {
    justify-content: center;
    text-align: center;
  }

  &.right {
    justify-content: flex-end;
    text-align: right;

    button {
      order: -1;
    }
  }

  &.divider {
    width: 2px !important;
    margin: 0 auto;
    padding: 0;
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

  .search {
    max-width: 150px;
  }
}
</style>
