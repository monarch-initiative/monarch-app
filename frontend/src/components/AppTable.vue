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
        class="wrapper"
        :data-left="arrivedState.left"
        :data-right="arrivedState.right"
        :data-expanded="expanded"
      >
        <div class="left-scroll">
          <AppIcon icon="angle-left" />
        </div>
        <div class="right-scroll">
          <AppIcon icon="angle-right" />
        </div>

        <div ref="table" class="scroll">
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
                      'arrow-' +
                      (sort?.id === col.id ? sort?.direction : 'down')
                    "
                    design="small"
                    :color="sort?.id === col.id ? 'primary' : 'secondary'"
                    :style="{ opacity: sort?.id === col.id ? 1 : 0.35 }"
                    @click.stop="emitSort(col)"
                  />
                  <AppSelectMulti
                    v-if="
                      selectedFilters?.[col.id] &&
                      filterOptions?.[col.id]?.length
                    "
                    v-tooltip="'Filter by ' + col.heading"
                    :name="'Filter by ' + col.heading"
                    :options="filterOptions[col.id]"
                    :model-value="selectedFilters[col.id]"
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
/** table column */
export type Cols<Key extends PropertyKey = PropertyKey> = {
  /**
   * unique id name to identify/match named slots. use "divider" to create
   * vertical divider to separate cols.
   */
  id: string;
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
  width?: string;
  /** whether to allow sorting of column */
  sortable?: boolean;
}[];

/** sort prop */
export type Sort = {
  id: string;
  direction: "up" | "down";
} | null;
</script>

<script setup lang="ts" generic="Datum extends object">
import { computed, nextTick, onMounted, ref, watch, type VNode } from "vue";
import { useResizeObserver, useScroll } from "@vueuse/core";
import type { Options } from "./AppSelectMulti.vue";
import AppSelectMulti from "./AppSelectMulti.vue";
import AppSelectSingle from "./AppSelectSingle.vue";
import AppTextbox from "./AppTextbox.vue";
import { closeToc } from "./TheTableOfContents.vue";

type Props = {
  /** info for each column of table */
  cols: Cols<keyof Datum>;
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

type SlotNames = Cols<keyof Datum>[number]["id"];

type SlotProps = {
  col: Cols<keyof Datum>[number];
  row: Datum;
  cell: Datum[keyof Datum] | null;
};

defineSlots<{
  [slot in SlotNames]: (props: SlotProps) => VNode;
}>();

/** whether table is expanded to be full width */
const expanded = ref(false);
/** table reference */
const table = ref<HTMLElement>();

/** table scroll state */
const { arrivedState } = useScroll(table, { offset: { left: 10, right: 10 } });

/** force table scroll to update */
async function updateScroll() {
  await nextTick();
  table.value?.dispatchEvent(new Event("scroll"));
}
onMounted(updateScroll);
watch(expanded, updateScroll);
useResizeObserver(table, updateScroll);

/** close table of contents when expanding */
watch(expanded, () => {
  if (expanded.value) closeToc();
});

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
function emitSort(col: Cols[number]) {
  let newSort: Sort;

  /** toggle sort direction */
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

  emit("update:sort", newSort);
}

/** when user changes a filter */
function emitFilter(colId: Cols[number]["id"], value: Options) {
  emit("update:selectedFilters", { ...props.selectedFilters, [colId]: value });
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
  props.cols.map((col) => col.width || "auto").join(" "),
);

/** aria sort direction attribute */
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
  position: relative;
  width: 100%;

  .left-scroll,
  .right-scroll {
    display: flex;
    z-index: 99;
    position: absolute;
    align-items: center;
    justify-content: center;
    width: 0;
    height: 100%;
    color: $gray;
    animation: 0.5s alternate infinite ease-in-out;
    opacity: 0;
    transition: opacity $fast;

    svg {
      transform: scale(1.5);
    }

    @keyframes nudge-left {
      to {
        transform: translateX(-5px);
      }
    }

    @keyframes nudge-right {
      to {
        transform: translateX(5px);
      }
    }
  }

  .left-scroll {
    left: 0px;
    animation-name: nudge-left;
  }

  .right-scroll {
    right: 0px;
    animation-name: nudge-right;
  }

  .scroll {
    width: 100%;
    overflow-x: auto;
  }

  &[data-left="false"] .left-scroll {
    opacity: 1;
  }

  &[data-right="false"] .right-scroll {
    opacity: 1;
  }

  &[data-left="false"][data-right="true"] .scroll {
    -webkit-mask-image: linear-gradient(to left, black 75%, transparent);
    mask-image: linear-gradient(to left, black 75%, transparent);
  }

  &[data-right="false"][data-left="true"] .scroll {
    -webkit-mask-image: linear-gradient(to right, black 75%, transparent);
    mask-image: linear-gradient(to right, black 75%, transparent);
  }

  &[data-left="false"][data-right="false"] .scroll {
    -webkit-mask-image: linear-gradient(
      to left,
      transparent,
      black 25%,
      black 75%,
      transparent
    );
    mask-image: linear-gradient(
      to left,
      transparent,
      black 25%,
      black 75%,
      transparent
    );
  }

  &[data-expanded="true"] {
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
  display: inline-grid;
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
    width: 2px;
    margin: 0 5px;
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
  width: 100%;
  gap: 10px;

  & > * {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
  }

  @media (max-width: 600px) {
    flex-direction: column;
  }

  .search {
    max-width: 150px;
  }
}
</style>
