<template>
  <div class="chart-container" :class="{ loading: isLoading, error: hasError }">
    <div v-if="title" class="chart-header">
      <h3 class="chart-title">{{ title }}</h3>
      <div v-if="showControls" class="chart-controls">
        <AppButton
          v-if="sql"
          :text="showSQL ? 'Hide SQL' : 'Show SQL'"
          design="small"
          color="secondary"
          @click="toggleSQL"
        />
        <AppButton
          v-if="allowExport"
          text="Export"
          design="small"
          color="secondary"
          @click="exportChart"
        />
      </div>
    </div>

    <!-- Render slot content from parent components like KGMetricCard -->
    <slot />

    <div
      ref="chartRef"
      class="chart-content"
      :style="{ height: chartHeight }"
    ></div>

    <div v-if="isLoading" class="chart-loading">
      <AppIcon icon="loading" />
      <span>{{ loadingText }}</span>
    </div>

    <div v-if="hasError" class="chart-error">
      <AppIcon icon="alert-triangle" />
      <span>{{ errorMessage }}</span>
      <AppButton v-if="allowRetry" text="Retry" design="small" @click="retry" />
    </div>

    <div v-if="showSQL && sql" class="chart-sql">
      <h4>SQL Query:</h4>
      <pre><code>{{ sql }}</code></pre>

      <div
        v-if="processedData && processedData.length > 0"
        class="query-results"
      >
        <h4>Query Results ({{ processedData.length }} rows):</h4>
        <pre><code>{{ JSON.stringify(processedData, null, 2) }}</code></pre>
      </div>

      <div
        v-else-if="processedData && processedData.length === 0"
        class="query-results"
      >
        <h4>Query Results:</h4>
        <p><em>Query executed successfully but returned no rows.</em></p>
      </div>

      <div v-else class="query-results">
        <h4>Query Results:</h4>
        <p>
          <em
            >No data available - query may not have executed yet or failed.</em
          >
        </p>
      </div>
    </div>

    <div
      v-if="showDataPreview && processedData && processedData.length > 0"
      class="chart-data-preview"
    >
      <h4>
        Data Preview (first {{ Math.min(5, processedData.length) }} rows):
      </h4>
      <table class="data-table">
        <thead>
          <tr>
            <th v-for="column in dataColumns" :key="column">{{ column }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in processedData.slice(0, 5)" :key="index">
            <td v-for="column in dataColumns" :key="column">
              {{ row[column] }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue";
import * as echarts from "echarts";
import type { ECharts, EChartsOption } from "echarts";
import AppButton from "@/components/AppButton.vue";
import AppIcon from "@/components/AppIcon.vue";

interface Props {
  title?: string;
  height?: string;
  isLoading?: boolean;
  error?: string | null;
  data?: Record<string, any>[];
  sql?: string;
  showControls?: boolean;
  allowExport?: boolean;
  allowRetry?: boolean;
  loadingText?: string;
  showDataPreview?: boolean;
}

interface Emits {
  (e: "retry"): void;
  (e: "export", chart: ECharts): void;
}

const props = withDefaults(defineProps<Props>(), {
  title: undefined,
  height: "400px",
  isLoading: false,
  error: null,
  data: () => [],
  sql: undefined,
  showControls: true,
  allowExport: true,
  allowRetry: true,
  loadingText: "Loading chart data...",
  showDataPreview: false,
});

const emit = defineEmits<Emits>();

const chartRef = ref<HTMLElement>();
const chart = ref<ECharts>();
const showSQL = ref(false);

const hasError = computed(() => !!props.error);
const chartHeight = computed(() => props.height);
const errorMessage = computed(() => props.error || "An error occurred");

/** Process data to ensure proper types (safety net for display) */
const processValue = (value: any): any => {
  // Handle DuckDB-specific data types first
  if (value instanceof Uint32Array) {
    return value[0];
  }

  if (typeof value === "bigint") {
    return Number(value);
  }

  if (
    value instanceof Int32Array ||
    value instanceof Float64Array ||
    value instanceof Float32Array
  ) {
    return value[0];
  }

  // Handle JSON-serialized strings (original logic)
  if (typeof value !== "string") return value;
  if (value === "") return value;

  let processedValue = value;
  try {
    while (
      typeof processedValue === "string" &&
      processedValue.startsWith('"') &&
      processedValue.endsWith('"')
    ) {
      processedValue = JSON.parse(processedValue);
    }
  } catch {
    /* ignore parsing errors */
  }

  if (typeof processedValue === "string" && processedValue.trim() !== "") {
    const numValue = Number(processedValue);
    if (!isNaN(numValue)) return numValue;
  }

  return processedValue;
};

const processedData = computed(() => {
  if (!props.data || props.data.length === 0) return [];

  return props.data.map((row) => {
    const processedRow: Record<string, any> = {};
    Object.entries(row).forEach(([key, value]) => {
      processedRow[key] = processValue(value);
    });
    return processedRow;
  });
});

const dataColumns = computed(() => {
  if (!processedData.value || processedData.value.length === 0) return [];
  return Object.keys(processedData.value[0]);
});

/** Initialize ECharts instance */
const initChart = async (): Promise<void> => {
  if (!chartRef.value) return;

  try {
    chart.value = echarts.init(chartRef.value);

    // Handle window resize
    window.addEventListener("resize", handleResize);
  } catch (err) {
    console.error("Failed to initialize chart:", err);
  }
};

/** Update chart with new options */
const updateChart = (options: EChartsOption): void => {
  if (!chart.value) return;

  try {
    chart.value.setOption(options, true);
  } catch (err) {
    console.error("Failed to update chart:", err);
  }
};

/** Handle window resize */
const handleResize = (): void => {
  if (chart.value) {
    chart.value.resize();
  }
};

/** Toggle SQL display */
const toggleSQL = (): void => {
  showSQL.value = !showSQL.value;
};

/** Export chart */
const exportChart = (): void => {
  if (chart.value) {
    emit("export", chart.value);
  }
};

/** Retry action */
const retry = (): void => {
  emit("retry");
};

/** Cleanup chart instance */
const cleanup = (): void => {
  if (chart.value) {
    chart.value.dispose();
    chart.value = undefined;
  }
  window.removeEventListener("resize", handleResize);
};

// Watch for data changes to trigger chart updates
watch(
  () => props.data,
  () => {
    nextTick(() => {
      if (chart.value) {
        handleResize();
      }
    });
  },
  { deep: true },
);

onMounted(async () => {
  await initChart();
});

onUnmounted(() => {
  cleanup();
});

// Expose methods for parent components
defineExpose({
  chart,
  updateChart,
  handleResize,
  cleanup,
});
</script>

<style lang="scss" scoped>
.chart-container {
  position: relative;
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: white;

  &.loading {
    opacity: 0.7;
  }

  &.error {
    border-color: #ef4444;
  }
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.chart-title {
  margin: 0;
  color: #1f2937;
  font-weight: 600;
  font-size: 1.25rem;
}

.chart-controls {
  display: flex;
  gap: 8px;
}

.chart-content {
  position: relative;
  min-height: 200px;
}

.chart-loading {
  display: flex;
  z-index: 10;
  position: absolute;
  top: 50%;
  left: 50%;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  transform: translate(-50%, -50%);
  color: #6b7280;
  font-size: 0.875rem;
}

.chart-error {
  display: flex;
  z-index: 10;
  position: absolute;
  top: 50%;
  left: 50%;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  transform: translate(-50%, -50%);
  color: #ef4444;
  text-align: center;

  span {
    font-size: 0.875rem;
  }
}

.chart-sql {
  margin-top: 16px;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background-color: #f9fafb;

  h4 {
    margin: 0 0 8px 0;
    color: #374151;
    font-weight: 600;
    font-size: 0.875rem;
  }

  pre {
    margin: 0;
    color: #1f2937;
    font-size: 0.75rem;
    line-height: 1.5;
    white-space: pre-wrap;
    word-break: break-word;
  }
}

.query-results {
  margin-top: 16px;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background-color: #ffffff;

  h4 {
    margin: 0 0 8px 0;
    color: #059669;
    font-weight: 600;
    font-size: 0.875rem;
  }

  pre {
    max-height: 300px;
    margin: 0;
    padding: 8px;
    overflow-y: auto;
    border: 1px solid #e5e7eb;
    border-radius: 4px;
    background-color: #f8fafc;
    color: #1f2937;
    font-size: 0.75rem;
    line-height: 1.4;
    white-space: pre-wrap;
    word-break: break-word;
  }

  p {
    margin: 0;
    color: #6b7280;
    font-style: italic;
    font-size: 0.875rem;
  }
}

.chart-data-preview {
  margin-top: 16px;

  h4 {
    margin: 0 0 8px 0;
    color: #374151;
    font-weight: 600;
    font-size: 0.875rem;
  }
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.75rem;

  th,
  td {
    padding: 6px 8px;
    border: 1px solid #e5e7eb;
    text-align: left;
  }

  th {
    background-color: #f9fafb;
    color: #374151;
    font-weight: 600;
  }

  td {
    color: #1f2937;
  }
}

@media (max-width: 768px) {
  .chart-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .chart-controls {
    align-self: flex-end;
  }
}
</style>
