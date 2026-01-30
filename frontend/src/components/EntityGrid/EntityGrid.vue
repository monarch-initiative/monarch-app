<!--
  Generic Entity Grid component for displaying entity × grouped-class matrices.
  Renders a table with:
  - Sticky first column for row labels
  - Collapsible bin rows showing aggregate counts
  - Expandable entity rows under each bin
  - Color-coded cells (present=teal, negated=red)
  - Hover tooltips with configurable content
-->

<template>
  <div class="entity-grid-container">
    <div class="scrollable-container">
      <table class="entity-grid">
        <!-- Header row -->
        <thead>
          <tr
            :class="{
              'labeled-header': config.columnDisplayMode === 'labeled',
            }"
          >
            <th class="sticky-col header-cell">
              {{ config.rowLabel }} / {{ config.binLabel }}
            </th>
            <th
              v-for="(column, index) in matrix.columns"
              :key="column.id"
              v-tooltip="getColumnTooltip(column, index)"
              class="header-cell column-header"
              :class="{
                'column-group-boundary': isColumnGroupBoundary(index),
              }"
            >
              <template v-if="config.columnDisplayMode === 'labeled'">
                <div class="diagonal-header">
                  <span class="diagonal-text">
                    <span class="entity-name">{{
                      column.label || column.id
                    }}</span>
                    <span
                      v-if="column.taxonLabel || column.taxonId"
                      class="taxon-info"
                    >
                      {{ column.taxonLabel || column.taxonId }}
                    </span>
                  </span>
                </div>
              </template>
              <template v-else>
                {{ index + 1 }}
              </template>
            </th>
          </tr>
        </thead>

        <!-- Body rows -->
        <tbody>
          <template v-for="bin in matrix.bins" :key="bin.id">
            <!-- Bin row (clickable to expand/collapse) -->
            <tr
              class="bin-row"
              :class="{ expanded: expandedBin === bin.id }"
              @click="toggleBin(bin.id)"
            >
              <td class="sticky-col bin-cell">
                <span class="expand-icon">{{
                  expandedBin === bin.id ? "▼" : "▶"
                }}</span>
                <span class="bin-label">{{ bin.label }}</span>
                <span class="bin-count">({{ bin.count }})</span>
              </td>
              <td
                v-for="(column, colIndex) in matrix.columns"
                :key="`${bin.id}:${column.id}`"
                v-tooltip="getBinCellTooltip(bin, column)"
                class="data-cell bin-data-cell"
                :class="{
                  'column-group-boundary': isColumnGroupBoundary(colIndex),
                }"
              >
                <div
                  v-if="getBinSummary(bin.id, column.id).presentCount > 0"
                  class="cell-square present"
                ></div>
                <div
                  v-else-if="
                    config.showNegated &&
                    getBinSummary(bin.id, column.id).negatedCount > 0
                  "
                  class="cell-square negated"
                ></div>
              </td>
            </tr>

            <!-- Expanded row entity rows (shown when bin is expanded) -->
            <tr
              v-for="rowId in expandedBin === bin.id ? bin.rowEntityIds : []"
              :key="rowId"
              class="row-entity-row"
            >
              <td class="sticky-col row-entity-cell">
                <span class="row-entity-label">
                  {{ getRowLabel(rowId) }}
                </span>
              </td>
              <td
                v-for="(column, colIndex) in matrix.columns"
                :key="`${column.id}:${rowId}`"
                v-tooltip="getCellTooltip(column, rowId)"
                class="data-cell row-entity-data-cell"
                :class="{
                  clickable: getCellData(column.id, rowId) !== null,
                  'column-group-boundary': isColumnGroupBoundary(colIndex),
                }"
                @click="handleCellClick(column.id, rowId)"
              >
                <div
                  v-if="isCellPresent(column.id, rowId)"
                  class="cell-square present"
                ></div>
                <div
                  v-else-if="
                    config.showNegated && isCellNegated(column.id, rowId)
                  "
                  class="cell-square negated"
                ></div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import type {
  CellData,
  ColumnEntity,
  EntityGridConfig,
  EntityGridMatrix,
  RowBin,
  RowEntity,
} from "@/api/entity-grid/types";
import { getBinCellSummary, getCellKey } from "./entity-grid-utils";

interface Props {
  matrix: EntityGridMatrix;
  config: EntityGridConfig;
}

interface Emits {
  (
    e: "cell-click",
    columnId: string,
    rowId: string,
    cellData: CellData | null,
  ): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

// State
const expandedBin = ref<string | null>(null);

// Check if a column is at a group boundary (different category than previous column)
const isColumnGroupBoundary = (index: number): boolean => {
  if (!props.config.showColumnGroupSeparators) return false;
  if (index === 0) return false;

  const currentColumn = props.matrix.columns[index];
  const prevColumn = props.matrix.columns[index - 1];

  // Compare source association categories
  return (
    currentColumn.sourceAssociationCategory !==
    prevColumn.sourceAssociationCategory
  );
};

// Get tooltip for column header
const getColumnTooltip = (column: ColumnEntity, index: number): string => {
  // Use custom formatter if provided
  if (props.config.columnTooltipFormatter) {
    return props.config.columnTooltipFormatter(column, index);
  }

  // Default tooltip
  let html = `<strong>${props.config.columnLabel} ${index + 1}</strong>`;
  if (column.label) {
    html += `<br>${column.label}`;
  }
  if (column.taxonLabel) {
    html += `<br>Species: ${column.taxonLabel}`;
  }
  html += `<br><small>${column.id}</small>`;

  // Show source entity if from a descendant (not direct)
  if (!column.isDirect && column.sourceEntityLabel) {
    html += `<br><br><em>Source: ${column.sourceEntityLabel}</em>`;
  }

  return html;
};

// Get tooltip for bin summary cell
const getBinCellTooltip = (bin: RowBin, column: ColumnEntity): string => {
  const summary = getBinSummary(bin.id, column.id);
  const columnLabel = column.label || column.id;

  if (summary.total === 0) {
    return `<strong>${bin.label}</strong><br>${props.config.columnLabel}: ${columnLabel}<br><em>No ${props.config.rowLabelPlural.toLowerCase()} recorded</em>`;
  }

  let html = `<strong>${bin.label}</strong><br>${props.config.columnLabel}: ${columnLabel}`;
  if (summary.presentCount > 0) {
    html += `<br><span style="display: inline-flex; align-items: center; gap: 4px;"><span style="display: inline-block; width: 10px; height: 10px; background: hsla(185, 100%, 30%, 0.85); border-radius: 2px;"></span> ${summary.presentCount} present</span>`;
  }
  if (props.config.showNegated && summary.negatedCount > 0) {
    html += `<br><span style="display: inline-flex; align-items: center; gap: 4px;"><span style="display: inline-block; width: 10px; height: 10px; background: hsla(0, 70%, 50%, 0.7); border-radius: 2px;"></span> ${summary.negatedCount} excluded</span>`;
  }
  return html;
};

// Toggle bin expansion
const toggleBin = (binId: string) => {
  if (expandedBin.value === binId) {
    expandedBin.value = null;
  } else {
    expandedBin.value = binId;
  }
};

// Get bin cell summary using utility function
const getBinSummary = (binId: string, columnId: string) => {
  return getBinCellSummary(props.matrix, binId, columnId);
};

// Get row label from matrix
const getRowLabel = (rowId: string): string => {
  const row = props.matrix.rows.find((r: RowEntity) => r.id === rowId);
  return row?.label || rowId;
};

// Get cell data from matrix
const getCellData = (columnId: string, rowId: string): CellData | null => {
  const key = getCellKey(columnId, rowId);
  return props.matrix.cells.get(key) || null;
};

// Check if cell is present (not negated)
const isCellPresent = (columnId: string, rowId: string): boolean => {
  const cellData = getCellData(columnId, rowId);
  if (!cellData) return false;
  // Check hasData for generic cells, or present for case-phenotype cells
  const hasPresence =
    "present" in cellData
      ? (cellData as { present: boolean }).present
      : cellData.hasData;
  return Boolean(hasPresence) && !cellData.negated;
};

// Check if cell is negated
const isCellNegated = (columnId: string, rowId: string): boolean => {
  const cellData = getCellData(columnId, rowId);
  return cellData?.negated === true;
};

// Get tooltip text for a row entity cell
const getCellTooltip = (column: ColumnEntity, rowId: string): string => {
  // Use custom formatter if provided
  if (props.config.cellTooltipFormatter) {
    const row = props.matrix.rows.find((r: RowEntity) => r.id === rowId);
    const cellData = getCellData(column.id, rowId);
    return props.config.cellTooltipFormatter(
      column,
      row || { id: rowId, binId: "" },
      cellData,
    );
  }

  // Default tooltip
  const cellData = getCellData(column.id, rowId);
  const rowLabel = getRowLabel(rowId);
  const columnLabel = column.label || column.id;

  if (!cellData) {
    return `<strong>${rowLabel}</strong><br>${props.config.columnLabel}: ${columnLabel}<br><em>No data</em>`;
  }

  const statusBg = cellData.negated
    ? "hsla(0, 70%, 50%, 0.7)"
    : "hsla(185, 100%, 30%, 0.85)";
  const statusText = cellData.negated ? "Excluded" : "Present";
  const statusSquare = `<span style="display: inline-block; width: 10px; height: 10px; background: ${statusBg}; border-radius: 2px; vertical-align: middle;"></span>`;

  let html = `<strong>${rowLabel}</strong>`;
  html += `<br>${props.config.columnLabel}: ${columnLabel}`;
  html += `<br>${statusSquare} ${statusText}`;

  // Show qualifiers if present
  if (cellData.qualifiers) {
    for (const q of cellData.qualifiers) {
      html += `<br>${q.type}: ${q.label}`;
    }
  }

  html += `<br><small>Click for details</small>`;

  return html;
};

// Handle cell click
const handleCellClick = (columnId: string, rowId: string) => {
  const cellData = getCellData(columnId, rowId);
  emit("cell-click", columnId, rowId, cellData);
};
</script>

<style lang="scss" scoped>
.entity-grid-container {
  width: 100%;
  // When using labeled headers, labels extend above the table
  // The parent component should provide padding if needed
  overflow: visible;
}

.scrollable-container {
  overflow-x: auto;
  overflow-y: visible;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: white;
}

.entity-grid {
  width: max-content;
  border-collapse: collapse;
  font-size: 0.9rem;
  table-layout: fixed;
}

// Sticky first column
.sticky-col {
  z-index: 2;
  position: sticky;
  left: 0;
  border-right: 2px solid #e5e7eb;
  background: white;
}

// Header styles
thead {
  .header-cell {
    padding: 0.4rem 0.5rem;
    border-bottom: 2px solid #e5e7eb;
    background: #f9fafb;
    font-weight: 600;
    font-size: 0.8rem;
    text-align: center;
    white-space: nowrap;

    &.sticky-col {
      min-width: 180px;
      background: #f9fafb;
      text-align: left;
    }
  }

  .column-header {
    min-width: 28px;
    padding: 0.4rem 0.25rem;
    cursor: help;

    &.column-group-boundary {
      border-left: 2px solid #9ca3af;
    }
  }

  // Labeled header row with diagonal text
  .labeled-header {
    background: transparent;

    .header-cell.sticky-col {
      z-index: 3;
      vertical-align: bottom;
    }

    .column-header {
      position: relative;
      width: 28px;
      min-width: 28px !important;
      max-width: 28px;
      height: 160px;
      padding: 0;
      vertical-align: bottom;
      background: transparent;
      cursor: default;

      // Remove column group border from header (doesn't work with diagonal labels)
      &.column-group-boundary {
        border-left: none;
      }

      // Remove hover highlighting
      &:hover {
        background: transparent;
      }
    }
  }

  .diagonal-header {
    position: absolute;
    bottom: 5px;
    left: 14px; // Center of 28px column
    width: 0;
    height: 0;
  }

  .diagonal-text {
    position: absolute;
    bottom: 0;
    left: 0;
    display: block;
    max-width: 200px;
    overflow: hidden;
    transform: rotate(-45deg);
    transform-origin: 0% 100%;
    font-size: 0.8rem;
    text-overflow: ellipsis;
    white-space: nowrap;

    .entity-name {
      font-weight: 500;
    }

    .taxon-info {
      margin-left: 4px;
      color: #666;
      font-weight: 400;
      font-size: 0.65rem;
    }
  }
}

// Body styles
tbody {
  // Bin row styles
  .bin-row {
    cursor: pointer;
    transition: background-color 0.2s;

    &:hover {
      background: #f3f4f6;
    }

    &.expanded {
      background: #eff6ff;

      .sticky-col {
        background: #eff6ff;
      }

      &:hover {
        background: #dbeafe;

        .sticky-col {
          background: #dbeafe;
        }
      }
    }
  }

  .bin-cell {
    display: flex;
    align-items: center;
    padding: 0.35rem 0.5rem;
    gap: 0.35rem;
    font-weight: 500;
    font-size: 0.8rem;

    .expand-icon {
      width: 0.8rem;
      color: #6b7280;
      font-size: 0.65rem;
    }

    .bin-label {
      color: #1f2937;
    }

    .bin-count {
      color: #6b7280;
      font-weight: 400;
      font-size: 0.75rem;
    }
  }

  // Row entity row styles
  .row-entity-row {
    background: #fafafa;

    .sticky-col {
      background: #fafafa;
    }

    &:hover {
      background: #f3f4f6;

      .sticky-col {
        background: #f3f4f6;
      }
    }
  }

  .row-entity-cell {
    padding: 0.25rem 0.5rem 0.25rem 1.5rem;

    .row-entity-label {
      color: #374151;
      font-size: 0.75rem;
    }
  }

  // Data cell styles
  .data-cell {
    padding: 2px;
    border-bottom: 1px solid #f3f4f6;
    text-align: center;
    vertical-align: middle;

    &.clickable {
      cursor: pointer;

      &:hover {
        background: #e5e7eb;
      }
    }

    &.column-group-boundary {
      border-left: 2px solid #9ca3af;
    }
  }

  .bin-data-cell {
    border-bottom: 1px solid #e5e7eb;
  }
}

// Cell square styles (phenogrid-like)
.cell-square {
  width: 18px;
  height: 18px;
  margin: auto;
  border-radius: 2px;

  &.present {
    background-color: hsla(185, 100%, 30%, 0.85);
  }

  &.negated {
    background-color: hsla(0, 70%, 50%, 0.7);
  }
}

// Responsive
@media (max-width: 768px) {
  .sticky-col {
    min-width: 120px;
  }

  .header-cell,
  .bin-cell,
  .row-entity-cell {
    padding: 0.25rem;
  }
}
</style>
