<template>
  <div class="predicate-table-container">
    <!-- Loading state -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <span>Loading predicates...</span>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="error-state">
      <AppIcon icon="circle-exclamation" />
      <span>{{ error }}</span>
    </div>

    <!-- Table -->
    <div v-else-if="tableData.length > 0" class="predicate-table">
      <!-- Header -->
      <div class="table-header">
        <div class="header-cell predicate-col" @click="toggleSort('predicate')">
          <span>Predicate</span>
          <AppIcon
            v-if="sortKey === 'predicate'"
            :icon="sortDirection === 'asc' ? 'arrow-up' : 'arrow-down'"
            class="sort-icon"
          />
        </div>
        <div class="header-cell count-col" @click="toggleSort('count')">
          <span>Edge Count</span>
          <AppIcon
            v-if="sortKey === 'count'"
            :icon="sortDirection === 'asc' ? 'arrow-up' : 'arrow-down'"
            class="sort-icon"
          />
        </div>
        <div class="header-cell expand-col">Details</div>
      </div>

      <!-- Rows -->
      <div class="table-body">
        <div
          v-for="(row, index) in sortedData"
          :key="row.predicate"
          class="table-row-wrapper"
        >
          <!-- Main row -->
          <div
            :class="['table-row', { expanded: expandedRow === row.predicate }]"
            @click="toggleRow(row.predicate, row.count)"
          >
            <div class="body-cell predicate-col">
              <span class="predicate-name">{{ row.predicate }}</span>
            </div>
            <div class="body-cell count-col">
              <span class="count-value">{{ formatNumber(row.count) }}</span>
            </div>
            <div class="body-cell expand-col">
              <AppButton
                :icon="
                  expandedRow === row.predicate ? 'chevron-up' : 'chevron-down'
                "
                design="small"
                @click.stop="toggleRow(row.predicate, row.count)"
              />
            </div>
          </div>

          <!-- Expanded detail panel -->
          <transition name="expand">
            <div v-if="expandedRow === row.predicate" class="expanded-detail">
              <PredicateDetailPanel
                :selected-predicate="row.predicate"
                :predicate-count="row.count"
                :compact="true"
              />
            </div>
          </transition>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="empty-state">
      <AppIcon icon="face-meh" />
      <span>No predicates found</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import AppButton from "@/components/AppButton.vue";
import AppIcon from "@/components/AppIcon.vue";
import { useSqlQuery } from "@/composables/use-sql-query";
import PredicateDetailPanel from "./PredicateDetailPanel.vue";

export interface Props {
  title?: string;
  dataSource: string;
  sql: string;
}

interface Emits {
  (e: "predicate-selected", predicate: string, count: number): void;
  (e: "data-changed", data: any[]): void;
  (e: "error", error: string): void;
}

const props = withDefaults(defineProps<Props>(), {
  title: "Predicate Distribution",
});

const emit = defineEmits<Emits>();

// State
const expandedRow = ref<string | null>(null);
const sortKey = ref<"predicate" | "count">("count");
const sortDirection = ref<"asc" | "desc">("desc");

// Set up SQL query execution
const sqlQuery = useSqlQuery({
  sql: props.sql,
  dataSources: [props.dataSource],
  autoExecute: true,
});

const { isLoading, error, result: queryResult } = sqlQuery;

// Process data from SQL query
const tableData = computed(() => {
  if (!queryResult.value?.data || queryResult.value.data.length === 0) {
    return [];
  }

  return queryResult.value.data.map((row: any) => ({
    predicate: row.category || row.predicate || row.name || "Unknown",
    count: Number(row.count || row.value || 0),
  }));
});

// Sorted data based on current sort settings
const sortedData = computed(() => {
  const data = [...tableData.value];

  return data.sort((a, b) => {
    let comparison = 0;

    if (sortKey.value === "predicate") {
      comparison = a.predicate.localeCompare(b.predicate);
    } else {
      comparison = a.count - b.count;
    }

    return sortDirection.value === "asc" ? comparison : -comparison;
  });
});

// Toggle sort
const toggleSort = (key: "predicate" | "count") => {
  if (sortKey.value === key) {
    sortDirection.value = sortDirection.value === "asc" ? "desc" : "asc";
  } else {
    sortKey.value = key;
    sortDirection.value = key === "count" ? "desc" : "asc";
  }
};

// Toggle row expansion
const toggleRow = (predicate: string, count: number) => {
  if (expandedRow.value === predicate) {
    expandedRow.value = null;
  } else {
    expandedRow.value = predicate;
    emit("predicate-selected", predicate, count);
  }
};

// Format number with commas
const formatNumber = (num: number): string => {
  return num.toLocaleString();
};
</script>

<style lang="scss" scoped>
.predicate-table-container {
  width: 100%;
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  gap: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  font-size: 1rem;
}

.loading-state {
  color: #0369a1;

  .spinner {
    width: 24px;
    height: 24px;
    border: 3px solid #bae6fd;
    border-radius: 50%;
    border-top-color: #0369a1;
    animation: spin 0.8s linear infinite;
  }
}

.error-state {
  color: #dc2626;
}

.empty-state {
  color: #6b7280;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.predicate-table {
  overflow: hidden;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: white;
}

.table-header {
  display: grid;
  grid-template-columns: 1fr auto auto;
  border-bottom: 2px solid #e5e7eb;
  background: #f9fafb;
}

.header-cell {
  display: flex;
  align-items: center;
  padding: 1rem;
  gap: 0.5rem;
  color: #374151;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background-color 0.2s;
  user-select: none;

  &:hover {
    background: #f3f4f6;
  }

  &.expand-col {
    cursor: default;

    &:hover {
      background: #f9fafb;
    }
  }

  .sort-icon {
    color: #3b82f6;
  }
}

.predicate-col {
  min-width: 0;
}

.count-col {
  justify-content: flex-end;
  width: 150px;
}

.expand-col {
  justify-content: center;
  width: 100px;
}

.table-body {
  .table-row-wrapper {
    border-bottom: 1px solid #e5e7eb;

    &:last-child {
      border-bottom: none;
    }
  }

  .table-row {
    display: grid;
    grid-template-columns: 1fr auto auto;
    cursor: pointer;
    transition: background-color 0.2s;

    &:hover {
      background: #f9fafb;
    }

    &.expanded {
      background: #eff6ff;

      &:hover {
        background: #dbeafe;
      }
    }
  }

  .body-cell {
    display: flex;
    align-items: center;
    padding: 1rem;
  }

  .predicate-name {
    color: #1f2937;
    font-weight: 500;
    font-family: "Courier New", monospace;
  }

  .count-value {
    color: #374151;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
  }
}

.expanded-detail {
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

// Expand transition
.expand-enter-active,
.expand-leave-active {
  overflow: hidden;
  transition: all 0.3s ease;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}

.expand-enter-to,
.expand-leave-from {
  max-height: 2000px;
  opacity: 1;
}

// Responsive
@media (max-width: 768px) {
  .table-header,
  .table-row {
    grid-template-columns: 1fr auto;
  }

  .expand-col {
    grid-column: 1 / -1;
    justify-content: flex-start;
    border-top: 1px solid #e5e7eb;
  }

  .count-col {
    width: auto;
  }
}
</style>
