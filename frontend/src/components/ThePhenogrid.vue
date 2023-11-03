<template>
  <AppFlex direction="col" class="flex">
    <div ref="scroll" class="scroll force-scrollbar">
      <svg
        ref="svg"
        xmlns="http://www.w3.org/2000/svg"
        class="svg"
        :viewBox="`-${labelXSize} -${labelYSize} ${width} ${height}`"
        :width="width / 3"
        :height="height / 3"
        :style="{ '--x': scrollCoords.x + 'px', '--y': scrollCoords.y + 'px' }"
      >
        <!-- clip col/row labels -->
        <clipPath id="clip-col-labels">
          <rect :x="0" :y="-labelYSize" :width="width" :height="labelYSize" />
        </clipPath>
        <clipPath id="clip-row-labels">
          <rect :x="-labelXSize" :y="0" :width="labelXSize" :height="height" />
        </clipPath>

        <!-- clip cells/grid-->
        <clipPath id="clip-grid">
          <rect x="0" y="0" :width="width" :height="height" />
        </clipPath>

        <!-- col labels -->
        <g class="col-labels">
          <tooltip
            v-for="(col, colIndex) in cols"
            :key="colIndex"
            :interactive="true"
            follow-cursor="initial"
            :append-to="appendToBody"
            :tag="null"
          >
            <text
              :class="['col-label', { hovered: hovered?.col === colIndex }]"
              :transform="`translate(${(0.5 + colIndex) * cellSize}, -${
                cellSize * 0.25
              }) rotate(-45)`"
              :style="{ 'font-size': cellSize * 0.5 + 'px' }"
              dominant-baseline="middle"
            >
              {{ truncate(col.label) }}
            </text>
            <template #content>
              <AppNodeBadge
                :node="{ id: col.id, name: col.label }"
                :absolute="true"
              />
              ({{ col.id }})
            </template>
          </tooltip>
        </g>

        <!-- row labels -->
        <g class="row-labels">
          <tooltip
            v-for="(row, rowIndex) in rows"
            :key="rowIndex"
            :interactive="true"
            follow-cursor="initial"
            :append-to="appendToBody"
            :tag="null"
          >
            <text
              :class="['row-label', { hovered: hovered?.row === rowIndex }]"
              :transform="`translate(-${cellSize * 0.25}, ${
                (0.5 + rowIndex) * cellSize
              })`"
              :style="{ 'font-size': cellSize * 0.5 + 'px' }"
              dominant-baseline="middle"
              text-anchor="end"
            >
              {{ truncate(row.label) }}
            </text>
            <template #content>
              <AppNodeBadge
                :node="{ id: row.id, name: row.label }"
                :absolute="true"
              />
              ({{ row.id }})
            </template>
          </tooltip>
        </g>

        <!-- grid -->
        <g class="grid">
          <template v-for="(col, colIndex) in cols" :key="colIndex">
            <line
              stroke="gray"
              :x1="(0.5 + colIndex) * cellSize"
              y1="0"
              :x2="(0.5 + colIndex) * cellSize"
              :y2="height - labelYSize"
            />
          </template>
          <template v-for="(row, rowIndex) in rows" :key="rowIndex">
            <line
              stroke="gray"
              :y1="(0.5 + rowIndex) * cellSize"
              x1="0"
              :y2="(0.5 + rowIndex) * cellSize"
              :x2="width - labelXSize - labelXSize * 0.75"
            />
          </template>
        </g>

        <!-- cells -->
        <g class="cells">
          <tooltip
            v-for="(cell, index) in cells"
            :key="index"
            :interactive="true"
            follow-cursor="initial"
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
              fill="hsl(185, 100%, 30%)"
              :opacity="cell.strength"
              tabindex="0"
              role="button"
              class="cell"
              @mouseenter="hoverCell(cell.col.index, cell.row.index)"
              @mouseleave="hoverCell(cell.col.index, cell.row.index, true)"
            />
            <template #content>
              <div class="mini-table">
                <AppNodeBadge
                  class="span"
                  :node="{ id: cell.col.id, name: cell.col.label }"
                  :absolute="true"
                />
                <AppNodeBadge
                  class="span"
                  :node="{ id: cell.row.id, name: cell.row.label }"
                  :absolute="true"
                />
                <span>Ancestor</span>
                <AppNodeBadge
                  :node="{
                    id: cell.ancestor_id,
                    name: cell.ancestor_label,
                  }"
                  :absolute="true"
                />
                <span>Ancestor IC</span>
                <span>{{ cell.score?.toFixed(3) }}</span>
                <span>Phenodigm</span>
                <span>
                  {{ cell.phenodigm_score?.toFixed(3) }}
                </span>
                <span>Jaccard</span>
                <span>
                  {{ cell.jaccard_similarity?.toFixed(3) }}
                </span>
              </div>
            </template>
          </tooltip>
        </g>
      </svg>
    </div>

    <AppFlex>
      <!-- <tooltip :interactive="true" :append-to="appendToBody" tag="button">
        Info&nbsp;<AppIcon icon="circle-question" />
        <template #content>
          <p>
            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
            eiusmod tempor incididunt ut labore et dolore magna aliqua.
          </p>
          <p>
            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
            eiusmod tempor incididunt ut labore et dolore magna aliqua.
          </p>
        </template>
      </tooltip> -->
      <AppButton
        v-tooltip="'Download grid as PNG'"
        design="small"
        text="Download"
        icon="download"
        @click="download"
      />
      <AppFlex flow="inline" gap="small">
        <span>Sort</span>
        <AppSelectSingle
          v-model="sortMethod"
          name="Sort"
          :options="sortMethods"
        />
      </AppFlex>
      <AppCheckbox v-model="reverse" text="Reverse" />
      <AppButton
        v-tooltip="'Copy unmatched phenotype ids to clipboard'"
        design="small"
        icon="copy"
        :text="`Unmatched (${data.unmatched.length})`"
        @click="copy"
      />
    </AppFlex>
  </AppFlex>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { sortBy } from "lodash";
import { useScroll } from "@vueuse/core";
import type { TermInfo } from "@/api/model";
import { type SetToSet } from "@/api/phenotype-explorer";
import AppCheckbox from "@/components/AppCheckbox.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppSelectSingle, {
  type Option,
  type Options,
} from "@/components/AppSelectSingle.vue";
import { appendToBody } from "@/global/tooltip";
import { screenToSvgCoords, truncateBySize } from "@/util/dom";
import { downloadSvg } from "@/util/download";
import { copyToClipboard } from "@/util/string";

type Props = {
  data: SetToSet["phenogrid"];
};

const props = defineProps<Props>();

/** size of cell squares */
const cellSize = 100;
/** space around cell squares */
const cellMargin = 10;
/** max length of labels, i.e. top and left margin */
const labelXSize = 500;
const labelYSize = 400;

const svg = ref<SVGSVGElement>();

/** track grid scroll */
const scroll = ref<HTMLDivElement>();
const scrollInfo = useScroll(scroll);
const scrollCoords = ref<{ x: number; y: number }>({ x: 0, y: 0 });

watch(
  () => scrollInfo,
  () => {
    const { x, y } = screenToSvgCoords(
      svg.value,
      scrollInfo.x.value,
      scrollInfo.y.value,
    );
    scrollCoords.value = { x: x + labelXSize, y: y + labelYSize };
  },
  { deep: true },
);

/** currently hovered col and row */
const hovered = ref<{ col: number; row: number }>();

/** total dimensions and viewbox of svg */
const width = computed(
  () => labelXSize + props.data.cols.length * cellSize + labelXSize * 0.65,
);
const height = computed(() => labelYSize + props.data.rows.length * cellSize);

/** set/unset hovered cell */
function hoverCell(col: number, row: number, unset = false) {
  if (unset) hovered.value = undefined;
  else hovered.value = { col, row };
}

/** options for sorting */
const sortMethods: Options = [
  { id: "", label: "Input Order" },
  { id: "alpha", label: "Alphabetical" },
  { id: "total", label: "Score Totals" },
];
const sortMethod = ref<Option>(sortMethods[0]);
const reverse = ref(false);

/** get sort func to sort rows/cols in particular order */
function sort(array: TermInfo[]): TermInfo[] {
  const method = sortMethod.value.id;
  array = [...array];
  if (method === "alpha") array = sortBy(array, "label");
  if (method === "total") array = sortBy(array, ["total"]).reverse();
  if (reverse.value) array.reverse();
  return array;
}

/** put rows, cols, cells in order for display */
const cols = computed(() => sort(props.data.cols));
const rows = computed(() => sort(props.data.rows));
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
      ...props.data.cells[col.id + row.id],
    }))
    .filter((cell) => cell.score),
);

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
    labelXSize * 0.9,
    cellSize * 0.5 + "px Poppins",
  );
}
</script>

<style scoped lang="scss">
.flex {
  max-width: 100%;
  max-height: 100%;
}

.scroll {
  flex-grow: 1;
  max-width: 100%;
  overflow: auto;
  border-radius: $rounded;
  box-shadow: $shadow;
}

.hovered {
  fill: $theme;
  font-weight: 600;
}

.col-labels {
  transform: translateY(var(--y));
}

.row-labels {
  transform: translateX(var(--x));
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

#clip-col-labels {
  transform: translateX(var(--x));
}

#clip-row-labels {
  transform: translateY(var(--y));
}

#clip-grid {
  transform: translate(var(--x), var(--y));
}
</style>
