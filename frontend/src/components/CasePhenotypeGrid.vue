<!--
  Case-Phenotype Grid component.
  Wraps the generic EntityGrid with case-phenotype-specific configuration.

  This is a backward-compatible wrapper that accepts CasePhenotypeMatrix
  and transforms it to the generic EntityGridMatrix format.
-->

<template>
  <EntityGrid
    :matrix="entityGridMatrix"
    :config="gridConfig"
    @cell-click="handleCellClick"
  />
</template>

<script setup lang="ts">
import { computed } from "vue";
import type {
  CasePhenotypeCellData,
  CasePhenotypeMatrix,
} from "@/api/case-phenotype-types";
import type { ColumnEntity, EntityGridConfig } from "@/api/entity-grid/types";
import { casePhenotypeToEntityGrid } from "@/components/EntityGrid/entity-grid-utils";
import EntityGrid from "@/components/EntityGrid/EntityGrid.vue";

interface Props {
  matrix: CasePhenotypeMatrix;
}

interface Emits {
  (
    e: "cell-click",
    caseId: string,
    phenotypeId: string,
    cellData: CasePhenotypeCellData | null,
  ): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

// Transform CasePhenotypeMatrix to EntityGridMatrix
const entityGridMatrix = computed(() =>
  casePhenotypeToEntityGrid(props.matrix),
);

// Case-phenotype-specific grid configuration
const gridConfig: EntityGridConfig = {
  columnLabel: "Case",
  columnLabelPlural: "Cases",
  rowLabel: "Phenotype",
  rowLabelPlural: "Phenotypes",
  binLabel: "System",
  cellDisplayMode: "binary",
  showNegated: true,
  columnTooltipFormatter: (column: ColumnEntity, index: number): string => {
    let html = `<strong>Case ${index + 1}</strong>`;
    if (column.label) {
      html += `<br>${column.label}`;
    }
    html += `<br><small>${column.id}</small>`;

    // Show source disease if from a descendant (not direct)
    if (!column.isDirect && column.sourceEntityLabel) {
      html += `<br><br><em>Disease: ${column.sourceEntityLabel}</em>`;
    }

    return html;
  },
};

// Handle cell click and emit with case-phenotype types
const handleCellClick = (
  columnId: string,
  rowId: string,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  cellData: any,
) => {
  // Get original cell data from the CasePhenotypeMatrix
  const originalCellData =
    props.matrix.cells.get(`${columnId}:${rowId}`) || null;
  emit("cell-click", columnId, rowId, originalCellData);
};
</script>
