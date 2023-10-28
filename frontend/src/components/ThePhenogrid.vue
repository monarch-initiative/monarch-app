<template>
  <AppFlex direction="col">
    <AppFlex ref="flex" direction="col">
      <div ref="scroll" class="scroll force-scrollbar">
        <table class="table">
          <thead>
            <tr>
              <!-- corner cell -->
              <th class="corner"></th>

              <!-- header cols -->
              <tooltip
                v-for="(col, colIndex) in sort(data.cols)"
                :key="colIndex"
                :interactive="true"
                follow-cursor="initial"
                :append-to="appendToBody"
                tag="th"
                :class="['col-head', { hovered: hovered?.col === colIndex }]"
                :style="{ zIndex: 999 - colIndex }"
              >
                <div>
                  {{ col.label }}
                </div>
                <template #content>
                  <AppNodeBadge
                    :node="{ id: col.id, name: col.label }"
                    :absolute="true"
                  />
                  ({{ col.id }})
                </template>
              </tooltip>
            </tr>
          </thead>

          <tbody>
            <!-- row heads -->
            <tr v-for="(row, rowIndex) in sort(data.rows)" :key="rowIndex">
              <tooltip
                :interactive="true"
                :append-to="appendToBody"
                tag="td"
                :class="[
                  'row-head',
                  'truncate',
                  {
                    hovered: hovered?.row === rowIndex,
                  },
                ]"
              >
                {{ row.label }}
                <template #content>
                  <AppNodeBadge
                    :node="{ id: row.id, name: row.label }"
                    :absolute="true"
                  />
                  ({{ row.id }})
                </template>
              </tooltip>

              <!-- cells -->
              <td
                v-for="(col, colIndex) in sort(data.cols)"
                :key="colIndex"
                class="cell"
              >
                <!-- cell score -->
                <tooltip
                  v-if="data.cells[col.id + row.id].strength"
                  :interactive="true"
                  tag="button"
                  :style="{ '--score': data.cells[col.id + row.id].strength }"
                  @mouseenter="hoverCell(colIndex, rowIndex)"
                  @mouseleave="hoverCell(colIndex, rowIndex, true)"
                >
                  <template #content>
                    <div class="mini-table">
                      <AppNodeBadge
                        class="span"
                        :node="{ id: col.id, name: col.label }"
                        :absolute="true"
                      />
                      <AppNodeBadge
                        class="span"
                        :node="{ id: row.id, name: row.label }"
                        :absolute="true"
                      />
                      <span>Ancestor</span>
                      <AppNodeBadge
                        :node="{
                          id: data.cells[col.id + row.id].ancestor_id,
                          name: data.cells[col.id + row.id].ancestor_label,
                        }"
                        :absolute="true"
                      />
                      <span>Ancestor IC</span>
                      <span>{{
                        data.cells[col.id + row.id].score.toFixed(3)
                      }}</span>
                      <span>Phenodigm</span>
                      <span>{{
                        data.cells[col.id + row.id].phenodigm_score?.toFixed(3)
                      }}</span>
                      <span>Jaccard</span>
                      <span>{{
                        data.cells[col.id + row.id].jaccard_similarity?.toFixed(
                          3,
                        )
                      }}</span>
                    </div>
                  </template>
                </tooltip>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- legend -->
      <div class="legend">
        <div class="gradient" />
        <span>Less similar</span>
        <span>More similar</span>
      </div>
    </AppFlex>

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
import { ref } from "vue";
import { sortBy, startCase } from "lodash";
import { hideAll } from "tippy.js";
import type { TermInfo } from "@/api/model";
import { type SetToSet } from "@/api/phenotype-explorer";
import AppCheckbox from "@/components/AppCheckbox.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppSelectSingle, {
  type Option,
  type Options,
} from "@/components/AppSelectSingle.vue";
import { snackbar } from "@/components/TheSnackbar.vue";
import { appendToBody } from "@/global/tooltip";
import { frame, sleep } from "@/util/debug";
import { downloadPng, getScreenshot } from "@/util/download";
import { copyToClipboard } from "@/util/string";

type Props = {
  data: SetToSet["phenogrid"];
};

const props = defineProps<Props>();

const hovered = ref<{ col: number; row: number }>();

/** set/unset hovered cell */
function hoverCell(colIndex: number, rowIndex: number, unset = false) {
  if (unset) hovered.value = undefined;
  else hovered.value = { col: colIndex, row: rowIndex };
}

const flex = ref<{ element: HTMLTableElement }>();
const scroll = ref<HTMLElement>();

/** download grid as png */
async function download() {
  if (!flex.value?.element || !scroll.value) return;

  /** make full size */
  scroll.value.classList.add("saving");
  flex.value.element.classList.add("saving");

  hideAll();

  /** wait for dom to update */
  await frame();
  await sleep(10);

  /** convert to image and download */
  try {
    const png = await getScreenshot(flex.value.element, 1);
    downloadPng(png, "phenogrid");
  } catch (error) {
    console.error(error);
    snackbar("Error saving image");
  }

  /** reset size */
  scroll.value.classList.remove("saving");
  flex.value.element.classList.remove("saving");
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
  if (method === "") array = [...array];
  if (method === "alpha") array = sortBy(array, "label");
  if (method === "total") array = sortBy(array, ["total"]).reverse();
  if (reverse.value) array.reverse();
  return array;
}

/** copy unmatched phenotype ids to clipboard */
function copy() {
  copyToClipboard(
    props.data.unmatched.map((phenotype) => phenotype.id).join(","),
  );
}
</script>

<style scoped lang="scss">
.scroll {
  max-width: 100%;
  max-height: calc(100vh - 200px);
  overflow: auto;
  background: $white;
}

.saving {
  width: max-content !important;
  max-width: unset !important;
  height: max-content !important;
  max-height: unset !important;
  overflow: visible !important;
  background: none !important;

  td,
  th {
    background: none !important;
  }
}

.table {
  margin-right: 140px;
  border-collapse: collapse;
}

.corner {
  z-index: 1000;
  position: sticky;
  top: 0;
  left: 0;
}

.col-head {
  position: sticky;
  top: 0;
  font-weight: inherit;
  text-align: left;
  vertical-align: bottom;
}

.col-head > div {
  max-height: 200px;
  overflow: hidden;
  transform: translate(-5px, -10px) rotate(-135deg) translateY(100%);
  transform-origin: bottom center;
  text-overflow: ellipsis;
  white-space: nowrap;
  writing-mode: vertical-lr;
}

.row-head {
  position: sticky;
  left: 0;
  max-width: 200px !important;
  padding-right: 10px;
  text-align: right;
}

.cell:empty {
  min-width: 20px;
  min-height: 20px;
}

.cell > * {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 3px;
  background: $light-gray;
}

.cell > div {
  opacity: 0;
}

.cell > button {
  background: color-mix(in srgb, $white, $theme calc(var(--score) * 100%));
  cursor: help;
}

th,
td {
  padding: 2px;
  background: $white;
}

.legend {
  display: grid;
  grid-template-rows: 10px 1fr;
  grid-template-columns: 1fr 1fr;
  width: max-content;
  gap: 10px;
}

.gradient {
  grid-column: span 2;
  background: linear-gradient(to right, $white, $theme);
}

.hovered {
  font-weight: 600;
}

.span {
  grid-column: span 2;
}
</style>
