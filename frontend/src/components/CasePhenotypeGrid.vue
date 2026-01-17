<template>
  <div class="case-phenotype-grid-container">
    <div class="scrollable-container">
      <table class="phenotype-grid">
        <!-- Header row -->
        <thead>
          <tr>
            <th class="sticky-col header-cell">Phenotype / System</th>
            <th
              v-for="(caseEntity, index) in matrix.cases"
              :key="caseEntity.id"
              v-tooltip="getCaseTooltip(caseEntity, index)"
              class="header-cell case-header"
            >
              {{ index + 1 }}
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
                v-for="caseEntity in matrix.cases"
                :key="`${bin.id}:${caseEntity.id}`"
                v-tooltip="getBinCellTooltip(bin, caseEntity)"
                class="data-cell bin-data-cell"
              >
                <span
                  v-if="getBinSummary(bin.id, caseEntity.id).presentCount > 0"
                  class="cell-icon present"
                  >●</span
                >
                <span
                  v-else-if="
                    getBinSummary(bin.id, caseEntity.id).negatedCount > 0
                  "
                  class="cell-icon negated"
                  >○</span
                >
              </td>
            </tr>

            <!-- Expanded phenotype rows (shown when bin is expanded) -->
            <tr
              v-for="phenotypeId in expandedBin === bin.id
                ? bin.phenotypeIds
                : []"
              :key="phenotypeId"
              class="phenotype-row"
            >
              <td class="sticky-col phenotype-cell">
                <span class="phenotype-label">
                  {{ getPhenotypeLabel(phenotypeId) }}
                </span>
              </td>
              <td
                v-for="caseEntity in matrix.cases"
                :key="`${caseEntity.id}:${phenotypeId}`"
                v-tooltip="getCellTooltip(caseEntity, phenotypeId)"
                class="data-cell phenotype-data-cell"
                :class="{
                  clickable: getCellData(caseEntity.id, phenotypeId) !== null,
                }"
                @click="handleCellClick(caseEntity.id, phenotypeId)"
              >
                <span
                  v-if="
                    getCellData(caseEntity.id, phenotypeId)?.present &&
                    !getCellData(caseEntity.id, phenotypeId)?.negated
                  "
                  class="cell-icon present"
                  >●</span
                >
                <span
                  v-else-if="getCellData(caseEntity.id, phenotypeId)?.negated"
                  class="cell-icon negated"
                  >○</span
                >
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
  CasePhenotypeCellData,
  CasePhenotypeMatrix,
} from "@/api/case-phenotype-types";
import { getBinCellSummary } from "@/util/case-phenotype-matrix";

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

// State
const expandedBin = ref<string | null>(null);

// Get tooltip for case header
const getCaseTooltip = (
  caseEntity: { id: string; label?: string; fullId?: string },
  index: number,
): string => {
  let html = `<strong>Case ${index + 1}</strong>`;
  if (caseEntity.label) {
    html += `<br>${caseEntity.label}`;
  }
  html += `<br><small>${caseEntity.id}</small>`;
  return html;
};

// Get tooltip for bin summary cell
const getBinCellTooltip = (
  bin: { id: string; label: string },
  caseEntity: { id: string; label?: string },
): string => {
  const summary = getBinSummary(bin.id, caseEntity.id);
  const caseLabel = caseEntity.label || caseEntity.id;

  if (summary.total === 0) {
    return `<strong>${bin.label}</strong><br>Case: ${caseLabel}<br><em>No phenotypes recorded</em>`;
  }

  let html = `<strong>${bin.label}</strong><br>Case: ${caseLabel}`;
  if (summary.presentCount > 0) {
    html += `<br><span style="color: #16a34a">● ${summary.presentCount} present</span>`;
  }
  if (summary.negatedCount > 0) {
    html += `<br><span style="color: #dc2626">○ ${summary.negatedCount} excluded</span>`;
  }
  return html;
};

// Toggle bin expansion
const toggleBin = (binId: string) => {
  console.log("toggleBin clicked:", binId);
  if (expandedBin.value === binId) {
    expandedBin.value = null;
  } else {
    expandedBin.value = binId;
  }
};

// Get bin cell summary using utility function
const getBinSummary = (binId: string, caseId: string) => {
  return getBinCellSummary(props.matrix, binId, caseId);
};

// Get phenotype label from matrix
const getPhenotypeLabel = (phenotypeId: string): string => {
  const phenotype = props.matrix.phenotypes.find((p) => p.id === phenotypeId);
  return phenotype?.label || phenotypeId;
};

// Get cell data from matrix
const getCellData = (
  caseId: string,
  phenotypeId: string,
): CasePhenotypeCellData | null => {
  const cellKey = `${caseId}:${phenotypeId}`;
  return props.matrix.cells.get(cellKey) || null;
};

// Get tooltip text for a phenotype cell
const getCellTooltip = (
  caseEntity: { id: string; label?: string },
  phenotypeId: string,
): string => {
  const cellData = getCellData(caseEntity.id, phenotypeId);
  const phenotypeLabel = getPhenotypeLabel(phenotypeId);
  const caseLabel = caseEntity.label || caseEntity.id;

  if (!cellData) {
    return `<strong>${phenotypeLabel}</strong><br>Case: ${caseLabel}<br><em>No data</em>`;
  }

  const statusColor = cellData.negated ? "#dc2626" : "#16a34a";
  const statusText = cellData.negated ? "○ Excluded" : "● Present";

  let html = `<strong>${phenotypeLabel}</strong>`;
  html += `<br>Case: ${caseLabel}`;
  html += `<br><span style="color: ${statusColor}">${statusText}</span>`;

  if (cellData.onset) {
    html += `<br>Onset: ${cellData.onset}`;
  }
  if (cellData.frequency) {
    html += `<br>Frequency: ${cellData.frequency}`;
  }

  html += `<br><small>Click for details</small>`;

  return html;
};

// Handle cell click
const handleCellClick = (caseId: string, phenotypeId: string) => {
  console.log("handleCellClick:", caseId, phenotypeId);
  const cellData = getCellData(caseId, phenotypeId);
  console.log("cellData:", cellData);
  emit("cell-click", caseId, phenotypeId, cellData);
};
</script>

<style lang="scss" scoped>
.case-phenotype-grid-container {
  width: 100%;
}

.scrollable-container {
  overflow-x: auto;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: white;
}

.phenotype-grid {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

// Sticky first column
.sticky-col {
  z-index: 1;
  position: sticky;
  left: 0;
  border-right: 2px solid #e5e7eb;
  background: white;
}

// Header styles
thead {
  .header-cell {
    padding: 0.75rem 1rem;
    border-bottom: 2px solid #e5e7eb;
    background: #f9fafb;
    font-weight: 600;
    text-align: center;
    white-space: nowrap;

    &.sticky-col {
      min-width: 200px;
      background: #f9fafb;
      text-align: left;
    }
  }

  .case-header {
    min-width: 40px;
    cursor: help;
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
    padding: 0.75rem 1rem;
    gap: 0.5rem;
    font-weight: 500;

    .expand-icon {
      width: 1rem;
      color: #6b7280;
      font-size: 0.75rem;
    }

    .bin-label {
      color: #1f2937;
    }

    .bin-count {
      color: #6b7280;
      font-weight: 400;
      font-size: 0.85rem;
    }
  }

  // Phenotype row styles
  .phenotype-row {
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

  .phenotype-cell {
    padding: 0.5rem 1rem 0.5rem 2.5rem;

    .phenotype-label {
      color: #374151;
      font-size: 0.85rem;
    }
  }

  // Data cell styles
  .data-cell {
    padding: 0.5rem;
    border-bottom: 1px solid #f3f4f6;
    text-align: center;

    &.clickable {
      cursor: pointer;

      &:hover {
        background: #e5e7eb;
      }
    }
  }

  .bin-data-cell {
    border-bottom: 1px solid #e5e7eb;
  }
}

// Cell icon styles
.cell-icon {
  font-size: 1rem;
  line-height: 1;

  &.present {
    color: #16a34a;
  }

  &.negated {
    color: #dc2626;
  }
}

// Responsive
@media (max-width: 768px) {
  .sticky-col {
    min-width: 150px;
  }

  .header-cell,
  .bin-cell,
  .phenotype-cell {
    padding: 0.5rem;
  }
}
</style>
