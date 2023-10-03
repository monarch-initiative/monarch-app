<template>
  <AppFlex direction="col">
    <div class="wrapper">
      <table class="table">
        <thead>
          <tr>
            <th></th>
            <tooltip
              v-for="(col, colIndex) in data.cols"
              :key="colIndex"
              :interactive="true"
              follow-cursor="initial"
              :append-to="appendToBody"
              tag="th"
              :class="['col-head', { hovered: hovered?.col === colIndex }]"
            >
              <div class="truncate">
                {{ col.label }}
              </div>
              <template #content>
                <AppNodeBadge :node="{ id: col.id, name: col.label }" /> ({{
                  col.id
                }})
              </template>
            </tooltip>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, rowIndex) in data.rows" :key="rowIndex">
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
                <AppNodeBadge :node="{ id: row.id, name: row.label }" /> ({{
                  row.id
                }})
              </template>
            </tooltip>
            <td
              v-for="(cell, colIndex) in data.cols.map(
                (_, colIndex) => data.cells[colIndex][rowIndex],
              )"
              :key="colIndex"
            >
              <tooltip
                :interactive="true"
                tag="button"
                class="cell"
                :style="{ '--score': cell.strength }"
                @mouseenter="hoverCell(colIndex, rowIndex)"
                @mouseleave="hoverCell(colIndex, rowIndex, true)"
              >
                <template #content>
                  <div class="mini-table">
                    <span>Score</span>
                    <span>{{ cell.score.toFixed(2) }}</span>
                    <template
                      v-for="(value, key, index) in cell.simInfo"
                      :key="index"
                    >
                      <span>{{ startCase(key) }}</span>
                      <span>{{
                        typeof value === "number" ? value.toFixed(2) : value
                      }}</span>
                    </template>
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
  </AppFlex>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { startCase } from "lodash";
import { type SetToSet } from "@/api/phenotype-explorer";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import { appendToBody } from "@/global/tooltip";

type Props = {
  data: SetToSet["phenogrid"];
};

defineProps<Props>();

const hovered = ref<{ col: number; row: number }>();

/** set/unset hovered cell */
function hoverCell(colIndex: number, rowIndex: number, unset = false) {
  if (unset) hovered.value = undefined;
  else hovered.value = { col: colIndex, row: rowIndex };
}
</script>

<style scoped lang="scss">
.wrapper {
  max-width: 100%;
  max-height: 100%;
  overflow: auto;
}

.table {
  margin-top: -40px;
  margin-right: 140px;
  border-collapse: collapse;
  text-align: left;
}

th {
  font-weight: inherit;
}

.col-head {
  text-align: left;
  vertical-align: bottom;
}

// need extra wrapper because of safari writing-mode bug with table cells
.col-head div {
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
  vertical-align: middle;
  cursor: help;
}

td {
  text-align: center;
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

.hovered {
  font-weight: 600;
}
</style>
