<template>
  <AppFlex ref="container" direction="col" class="container">
    <tooltip
      :interactive="true"
      placement="bottom"
      :append-to="appendToBody"
      tag="span"
      tabindex="0"
    >
      Info&nbsp;<AppIcon icon="circle-question" />
      <template #content>
        <p>
          Compares one set of phenotypes to another based on ontology structure.
          Set A is on the
          {{ transpose ? "top" : "left" }}, set B is on the
          {{ transpose ? "left" : "top" }}.
        </p>
      </template>
    </tooltip>

    <div ref="scroll" class="scroll force-scrollbar">
      <svg
        ref="svg"
        xmlns="http://www.w3.org/2000/svg"
        class="svg"
        :viewBox="`-${marginLeft} -${marginTop} ${width} ${height}`"
        :width="width / 3"
        :height="height / 3"
      >
        <!-- clip col/row labels -->
        <clipPath
          id="clip-col-labels"
          class="translate"
          :style="{ '--x': scrollCoords.x + 'px' }"
        >
          <rect :x="0" :y="-marginTop" :width="width" :height="marginTop" />
        </clipPath>
        <clipPath
          id="clip-row-labels"
          class="translate"
          :style="{ '--y': scrollCoords.y + 'px' }"
        >
          <rect :x="-marginLeft" :y="0" :width="marginLeft" :height="height" />
        </clipPath>

        <!-- clip cells/grid-->
        <clipPath
          id="clip-grid"
          class="translate"
          :style="{
            '--x': scrollCoords.x + 'px',
            '--y': scrollCoords.y + 'px',
          }"
        >
          <rect x="0" y="0" :width="width" :height="height" />
        </clipPath>

        <!-- col labels -->
        <g
          class="col-labels translate"
          :style="{
            'font-size': cellSize * 0.5 + 'px',
            '--y': scrollCoords.y + 'px',
          }"
          dominant-baseline="middle"
        >
          <tooltip
            v-for="(col, colIndex) in cols"
            :key="colIndex"
            :interactive="true"
            placement="bottom"
            follow-cursor="initial"
            :append-to="appendToBody"
            :tag="null"
          >
            <text
              :data-hovered="hovered ? hovered.col === colIndex : ''"
              :transform="`translate(${(0.5 + colIndex) * cellSize}, -${
                cellSize * 0.25
              }) rotate(-45)`"
            >
              {{ truncate(col.label) }}
            </text>
            <template #content>
              <AppNodeBadge :node="col" :absolute="true" :show-id="true" />
              <div class="mini-table">
                <span>Total Score</span>
                <span>{{ col.total.toFixed(3) }}</span>
              </div>
            </template>
          </tooltip>
        </g>

        <!-- row labels -->
        <g
          class="row-labels translate"
          :style="{
            'font-size': cellSize * 0.5 + 'px',
            '--x': scrollCoords.x + 'px',
          }"
          dominant-baseline="middle"
          text-anchor="end"
        >
          <tooltip
            v-for="(row, rowIndex) in rows"
            :key="rowIndex"
            :interactive="true"
            placement="bottom"
            follow-cursor="initial"
            :append-to="appendToBody"
            :tag="null"
          >
            <text
              :data-hovered="hovered ? hovered.row === rowIndex : ''"
              :transform="`translate(-${cellSize * 0.25}, ${
                (0.5 + rowIndex) * cellSize
              })`"
            >
              {{ truncate(row.label) }}
            </text>
            <template #content>
              <AppNodeBadge :node="row" :absolute="true" :show-id="true" />
              <div class="mini-table">
                <span>Total Score</span>
                <span>{{ row.total.toFixed(3) }}</span>
              </div>
            </template>
          </tooltip>
        </g>

        <!-- grid -->
        <g class="grid" stroke="gray">
          <template v-for="(col, colIndex) in cols" :key="colIndex">
            <line
              stroke-width="0"
              :data-hovered="hovered ? hovered.col === colIndex : ''"
              :x1="(0.5 + colIndex) * cellSize"
              :y1="0"
              :x2="(0.5 + colIndex) * cellSize"
              :y2="gridHeight"
            />
          </template>
          <template v-for="(row, rowIndex) in rows" :key="rowIndex">
            <line
              stroke-width="0"
              :data-hovered="hovered ? hovered.row === rowIndex : ''"
              :x1="0"
              :y1="(0.5 + rowIndex) * cellSize"
              :x2="gridWidth"
              :y2="(0.5 + rowIndex) * cellSize"
            />
          </template>
        </g>

        <!-- cells -->
        <g class="cells">
          <tooltip
            v-for="(cell, index) in cells"
            :key="index"
            :interactive="true"
            placement="bottom"
            :append-to="appendToBody"
            :tag="null"
          >
            <rect
              :x="
                (cell.col.index + 0.5) * cellSize - cellSize * 0.5 + cellMargin
              "
              :y="
                (cell.row.index + 0.5) * cellSize - cellSize * 0.5 + cellMargin
              "
              :width="cellSize - cellMargin * 2"
              :height="cellSize - cellMargin * 2"
              :rx="cellMargin"
              :ry="cellMargin"
              :fill="getColor(cell.strength)"
              tabindex="0"
              role="button"
              @mouseenter="hoverCell(cell.col.index, cell.row.index)"
              @mouseleave="hoverCell(cell.col.index, cell.row.index, true)"
            />
            <template #content>
              <AppNodeBadge
                v-if="cell.phenotype"
                :node="{ id: cell.col.id, name: cell.col.label }"
                :absolute="true"
              />
              <div class="tooltip-heading">
                <AppNodeBadge
                  v-if="cell.phenotype"
                  :node="{ id: cell.phenotype, name: cell.phenotypeLabel }"
                  :absolute="true"
                />
                <AppNodeBadge
                  v-else
                  :node="{ id: cell.col.id, name: cell.col.label }"
                  :absolute="true"
                />
                <AppIcon icon="arrows-left-right" />
                <AppNodeBadge
                  :node="{ id: cell.row.id, name: cell.row.label }"
                  :absolute="true"
                />
              </div>
              <div class="mini-table">
                <span>Ancestor</span>
                <AppNodeBadge
                  :node="{
                    id: cell.ancestor_id,
                    name: cell.ancestor_label,
                  }"
                  :absolute="true"
                />
                <AppLink
                  to="https://incatools.github.io/ontology-access-kit/guide/similarity.html#information-content"
                >
                  Ancestor IC
                </AppLink>
                <span>
                  {{ cell.score?.toFixed(3) }}
                </span>
                <AppLink
                  to="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3649640/"
                >
                  Phenodigm
                </AppLink>
                <strong>
                  {{ cell.phenodigm_score?.toFixed(3) }}
                </strong>
                <AppLink
                  to="https://incatools.github.io/ontology-access-kit/guide/similarity.html#jaccard-similarity"
                >
                  Jaccard
                </AppLink>
                <span>{{ cell.jaccard_similarity?.toFixed(3) }}</span>
              </div>
            </template>
          </tooltip>
        </g>

        <!-- legend -->
        <g
          class="legend translate"
          dominant-baseline="middle"
          :style="{
            'font-size': cellSize * 0.5 + 'px',
            '--x': scrollCoords.x + 'px',
            '--y': scrollCoords.y + 'px',
          }"
        >
          <text :x="-marginLeft / 2" :y="-marginTop / 2" text-anchor="middle">
            Similarity
          </text>
          <text
            :x="-marginLeft / 2 - cellSize * 0.75"
            :y="-marginTop / 2 + cellSize * 0.65"
            text-anchor="end"
          >
            Less
          </text>
          <text
            :x="-marginLeft / 2 + cellSize * 0.75"
            :y="-marginTop / 2 + cellSize * 0.65"
            text-anchor="start"
          >
            More
          </text>
          <defs>
            <linearGradient id="gradient" x1="0" x2="1" y1="0" y2="0">
              <stop
                v-for="(percent, index) in [0, 0.2, 0.4, 0.6, 0.8, 1]"
                :key="index"
                :offset="`${percent * 100}%`"
                :stop-color="getColor(percent)"
              />
            </linearGradient>
          </defs>
          <rect
            fill="url(#gradient)"
            :x="-marginLeft / 2 - cellSize / 2"
            :y="-marginTop / 2 + cellSize * 0.8 - cellSize / 3"
            :width="cellSize"
            :height="cellSize / 3"
          />
        </g>
      </svg>
    </div>

    <div class="controls">
      <AppFlex
        v-tooltip="'What order to put column and row labels in'"
        flow="inline"
        gap="small"
      >
        <span>Sort</span>
        <AppSelectSingle
          v-model="sortOrder"
          name="Sort"
          :options="sortOrders"
        />
      </AppFlex>
      <AppCheckbox
        v-model="transpose"
        v-tooltip="'Swap rows and columns'"
        text="Transpose"
      />
      <AppButton
        v-tooltip="'Copy unmatched phenotype ids to clipboard'"
        design="small"
        icon="copy"
        :text="`Unmatched (${data.unmatched.length})`"
        @click="copy"
      />
      <AppButton
        v-tooltip="'Download grid as PNG'"
        design="small"
        text="Download"
        icon="download"
        @click="download"
      />
    </div>
  </AppFlex>
</template>

<script lang="ts">
export type Phenogrid = {
  cols: {
    total: number;
    id: string;
    label?: string | undefined;
  }[];
  rows: {
    total: number;
    id: string;
    label?: string | undefined;
  }[];
  cells: {
    [key: string]: {
      score: number;
      strength: number;
      phenotype?: string;
      phenotypeLabel?: string;
    } & Pick<
      TermPairwiseSimilarity,
      | "ancestor_id"
      | "ancestor_label"
      | "jaccard_similarity"
      | "phenodigm_score"
    >;
  };
  unmatched: {
    total: number;
    id: string;
    label?: string | undefined;
  }[];
};
</script>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";
import { sortBy } from "lodash";
import { useResizeObserver, useScroll } from "@vueuse/core";
import type { TermInfo, TermPairwiseSimilarity } from "@/api/model";
import AppCheckbox from "@/components/AppCheckbox.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppSelectSingle, { type Option } from "@/components/AppSelectSingle.vue";
import { appendToBody } from "@/global/tooltip";
import { frame } from "@/util/debug";
import { screenToSvgCoords, truncateBySize } from "@/util/dom";
import { downloadSvg } from "@/util/download";
import { copyToClipboard } from "@/util/string";

type Props = {
  data: Phenogrid;
};

const props = defineProps<Props>();

/** size of cell squares */
const cellSize = 100;
/** space around cell squares */
const cellMargin = 10;
/** margins around cell area */
const marginLeft = 500;
const marginRight = 325;
const marginTop = 400;
const marginBottom = 20;

/** element refs */
const container = ref<{ element: HTMLDivElement }>();
const scroll = ref<HTMLDivElement>();
const svg = ref<SVGSVGElement>();

/** dimensions of grid cells area */
const gridWidth = computed(() => cols.value.length * cellSize);
const gridHeight = computed(() => rows.value.length * cellSize);

/** total dimensions and viewbox of svg */
const width = computed(() => marginLeft + gridWidth.value + marginRight);
const height = computed(() => marginTop + gridHeight.value + marginBottom);

/** currently hovered col and row */
const hovered = ref<{ col: number; row: number }>();

/** set/unset hovered cell */
function hoverCell(col: number, row: number, unset = false) {
  if (unset) hovered.value = undefined;
  else hovered.value = { col, row };
}

/** options for sorting */
const sortOrders: Option[] = [
  { id: "input", label: "Input Order" },
  { id: "alpha", label: "Alpha. (a → z)" },
  { id: "alpha-rev", label: "Alpha. (z → a)" },
  { id: "total", label: "Score (highest)" },
  { id: "total-rev", label: "Score (lowest)" },
];
const sortOrder = ref(sortOrders[0]);

/** get sort func to sort rows/cols in particular order */
function sort(array: Phenogrid["rows"]): Phenogrid["rows"] {
  const { id } = sortOrder.value;
  array = [...array];
  if (id.startsWith("alpha"))
    array = sortBy(array, (item) => item.label?.toLowerCase());
  if (id.startsWith("total")) array = sortBy(array, ["total"]).reverse();
  if (id.endsWith("-rev")) array.reverse();
  return array;
}

/** swap cols/rows */
const transpose = ref(false);

/** put rows, cols, cells in order for display */
const cols = computed(() =>
  sort(transpose.value ? props.data.rows : props.data.cols),
);
const rows = computed(() =>
  sort(transpose.value ? props.data.cols : props.data.rows),
);
const cells = computed(() =>
  cols.value
    .map((col, colIndex) =>
      rows.value.map((row, rowIndex) => ({
        row: { ...row, index: rowIndex },
        col: { ...col, index: colIndex },
      })),
    )
    .flat()
    .map(({ col, row }) => ({
      col,
      row,
      ...getCell(col, row),
    }))
    .filter((cell) => cell.score),
);

/** get matching cell from col and row */
function getCell(col: TermInfo, row: TermInfo) {
  return transpose.value
    ? props.data.cells[row.id + col.id]
    : props.data.cells[col.id + row.id];
}

/** get color of strength */
function getColor(strength: number) {
  /** $theme */
  return `hsla(185, 100%, 30%, ${strength})`;
}

/** download svg */
function download() {
  if (svg.value) downloadSvg(svg.value, "phenogrid");
}

/** copy unmatched phenotype ids to clipboard */
function copy() {
  copyToClipboard(
    props.data.unmatched.map((phenotype) => phenotype.id).join(","),
  );
}

/** truncate labels */
function truncate(text?: string) {
  return truncateBySize(
    text || "",
    marginLeft * 0.9,
    cellSize * 0.5 + "px Poppins",
  );
}

/** track grid scroll */
const scrollInfo = useScroll(scroll);
const scrollCoords = ref({ x: 0, y: 0, w: 0, h: 0 });
function updateScroll() {
  if (!svg.value || !scroll.value) return;
  const { x, y } = screenToSvgCoords(
    svg.value,
    scrollInfo.x.value,
    scrollInfo.y.value,
  );
  const { x: w, y: h } = screenToSvgCoords(
    svg.value,
    scroll.value.clientWidth,
    scroll.value.clientHeight,
  );
  scrollCoords.value = { x: x + marginLeft, y: y + marginTop, w, h };
}
watch(() => scrollInfo, updateScroll, { deep: true });
useResizeObserver(scroll, updateScroll);

/** notify parent of events that may change dimensions */
watch([sortOrder, transpose, props.data], emitSize, {
  immediate: true,
  deep: true,
});

/** post message that size of widget has changed */
async function emitSize() {
  await nextTick();
  const element = container.value?.element;
  if (!element) return;
  element.classList.add("full-size");
  await frame();
  let width = element.clientWidth + 2;
  let height = element.clientHeight + 2;
  await frame();
  element.classList.remove("full-size");
  window.parent.postMessage({ width, height }, "*");
}
</script>

<style scoped lang="scss">
.container {
  max-width: 100%;
  max-height: 100%;
}

.full-size {
  width: max-content !important;
  max-width: unset !important;
  height: max-content !important;
  max-height: unset !important;
  margin: auto;
}

.scroll {
  flex-grow: 1;
  max-width: 100%;
  overflow: auto;
  border-radius: $rounded;
  box-shadow: $shadow;
}

.translate {
  transform: translate(var(--x, 0), var(--y, 0));
}

.col-labels,
.row-labels,
.cells {
  cursor: help;
}

.col-labels {
  clip-path: url(#clip-col-labels);
}

.row-labels {
  clip-path: url(#clip-row-labels);
}

.cells,
.grid {
  clip-path: url(#clip-grid);
}

[data-hovered] {
  transition:
    fill $fast,
    stroke $fast,
    opacity $fast;
}

.col-labels [data-hovered="true"],
.row-labels [data-hovered="true"] {
  fill: $theme;
}

.grid [data-hovered="true"] {
  stroke: $theme;
  stroke-width: 5;
}

[data-hovered="false"] {
  opacity: 0.1;
}

.tooltip-heading {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  padding-bottom: 10px;
  gap: 20px;
  border-bottom: dashed 1px $dark-gray;
}

.controls {
  display: grid;
  grid-template-columns: auto auto;
  gap: 10px 20px;
}
</style>
