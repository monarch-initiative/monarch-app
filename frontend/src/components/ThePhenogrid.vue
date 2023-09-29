<template>
  <div class="wrapper">
    <table class="table">
      <thead>
        <tr>
          <th></th>
          <tooltip
            v-for="(col, colIndex) in cols"
            :key="colIndex"
            :interactive="true"
            follow-cursor="initial"
            :append-to="appendToBody"
            tag="th"
            class="col-head truncate"
          >
            {{ col.label }}
            <template #content>
              <div class="mini-table">
                <span>ID</span>
                <span>{{ col.id }}</span>
                <span>Name</span>
                <span>{{ col.label }}</span>
              </div>
            </template>
          </tooltip>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, rowIndex) in rows" :key="rowIndex">
          <tooltip
            :interactive="true"
            :append-to="appendToBody"
            tag="td"
            class="row-head truncate"
          >
            {{ row.label }}
            <template #content>
              <div class="mini-table">
                <span>ID</span>
                <span>{{ row.id }}</span>
                <span>Name</span>
                <span>{{ row.label }}</span>
              </div>
            </template>
          </tooltip>
          <td v-for="(col, colIndex) in cols" :key="colIndex">
            <tooltip
              :interactive="true"
              tag="button"
              :class="['cell', { selected: isSelected(colIndex, rowIndex) }]"
              :style="{ '--score': getCell(colIndex, rowIndex).score }"
              @click="selectCell(colIndex, rowIndex)"
            >
              <template #content>
                <div class="mini-table">
                  <span>Score</span>
                  <span>{{ getCell(colIndex, rowIndex).score }}</span>
                  <span>Lorem</span>
                  <span>{{ getCell(colIndex, rowIndex).lorem }}</span>
                </div>
              </template>
            </tooltip>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <div class="legend">
    <div class="gradient" />
    <span>Less similar</span>
    <span>More similar</span>
  </div>

  <AppFlex v-if="selected" direction="col">
    <strong>Selected match</strong>
    <div class="mini-table">
      <span>Score</span>
      <span>{{ getCell(selected.col, selected.row).score }}</span>
      <span>Lorem</span>
      <span>{{ getCell(selected.col, selected.row).lorem }}</span>
    </div>
  </AppFlex>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { round } from "lodash";
import type { TermSetPairwiseSimilarity } from "@/api/model";
import { appendToBody } from "@/global/tooltip";

type Props = {
  data: TermSetPairwiseSimilarity;
};

const props = defineProps<Props>();

const selected = ref<{ col: number; row: number }>();

/** details for each column */
const cols = computed(() =>
  Object.values(props.data.object_termset || {}).map(({ id, label }) => ({
    id,
    label,
  })),
);

/** details for each row */
const rows = computed(() =>
  Object.values(props.data.subject_termset || {}).map(({ id, label }) => ({
    id,
    label,
  })),
);

/** details for each cell */
const cells = computed(() =>
  cols.value.map(() =>
    rows.value.map(() => ({
      score: round(Math.random(), 3),
      lorem: "ipsum",
    })),
  ),
);

/** get cell from col/row indices */
function getCell(colIndex: number, rowIndex: number) {
  return cells.value[colIndex][rowIndex];
}

/** check if cell is selected */
function isSelected(colIndex: number, rowIndex: number) {
  return colIndex === selected.value?.col && rowIndex === selected.value?.row;
}

/** set selected cell */
function selectCell(colIndex: number, rowIndex: number) {
  if (isSelected(colIndex, rowIndex)) selected.value = undefined;
  else selected.value = { col: colIndex, row: rowIndex };
}
</script>

<style scoped lang="scss">
.wrapper {
  width: 100%;
  overflow-x: auto;
}

.table {
  margin: auto;
  margin-top: -50px;
  border-collapse: collapse;
  text-align: left;
}

th {
  font-weight: inherit;
}

.col-head {
  max-height: 200px;
  transform: translate(-5px, -10px) rotate(-135deg) translateY(100%);
  transform-origin: bottom center;
  writing-mode: vertical-lr;
}

.row-head {
  max-width: 200px !important;
  padding-right: 10px;
  text-align: right;
}

.cell {
  width: 20px;
  height: 20px;
  margin: auto;
  padding: 0;
  border-radius: 3px;
  background: color-mix(in srgb, $white, $theme calc(var(--score) * 100%));
}

.cell.selected,
.cell:hover {
  outline: solid 2px $black;
}

th,
td {
  padding: 2px;
}

.legend {
  display: grid;
  grid-template-rows: 10px 1fr;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.gradient {
  grid-column: span 2;
  background: linear-gradient(to right, $white, $theme);
}
</style>
