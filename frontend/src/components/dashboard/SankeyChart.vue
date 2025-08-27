<template>
  <BaseChart
    ref="baseChartRef"
    :title="title"
    :is-loading="isLoading"
    :error="error"
    :data="queryResult?.data"
    :sql="sql"
    :show-controls="showControls"
    :allow-export="allowExport"
    :show-data-preview="showDataPreview"
    :height="height"
    @retry="handleRetry"
    @export="handleExport"
  >
    <!-- The actual Sankey chart will be rendered by ECharts in the BaseChart canvas -->

    <!-- Export Menu Overlay -->
    <!-- eslint-disable-next-line vuejs-accessibility/no-static-element-interactions -->
    <div
      v-if="showExportMenu"
      class="export-overlay"
      role="dialog"
      aria-modal="true"
      aria-label="Export chart dialog"
      tabindex="0"
      @click.self="showExportMenu = false"
      @keydown.escape="showExportMenu = false"
      @keydown.enter="showExportMenu = false"
      @keydown.space="showExportMenu = false"
    >
      <div class="export-menu">
        <div class="export-header">
          <h3>Export Chart</h3>
          <button class="close-button" @click="showExportMenu = false">
            ×
          </button>
        </div>
        <div class="export-options">
          <button class="export-option" @click="exportAsPNG">
            <AppIcon icon="download" class="export-icon" />
            <div class="export-details">
              <div class="export-title">PNG Image</div>
              <div class="export-desc">Standard resolution for web use</div>
            </div>
          </button>
          <button class="export-option" @click="exportAsHighResPNG">
            <AppIcon icon="download" class="export-icon" />
            <div class="export-details">
              <div class="export-title">High-Res PNG</div>
              <div class="export-desc">4x resolution for print quality</div>
            </div>
          </button>
          <button class="export-option" @click="exportAsSVG">
            <AppIcon icon="code" class="export-icon" />
            <div class="export-details">
              <div class="export-title">SVG Vector</div>
              <div class="export-desc">Scalable vector format</div>
            </div>
          </button>
          <button class="export-option" @click="exportAsJSON">
            <AppIcon icon="file-lines" class="export-icon" />
            <div class="export-details">
              <div class="export-title">JSON Data</div>
              <div class="export-desc">Raw data and SQL query</div>
            </div>
          </button>
        </div>
      </div>
    </div>
  </BaseChart>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import * as echarts from "echarts";
import type { EChartsOption } from "echarts";
import { useSqlQuery } from "@/composables/use-sql-query";
import AppIcon from "@/components/AppIcon.vue";
import BaseChart from "./BaseChart.vue";

export interface Props {
  title: string;
  dataSource: string;
  sql: string;
  showControls?: boolean;
  allowExport?: boolean;
  showDataPreview?: boolean;
  autoExecute?: boolean;
  pollInterval?: number;
  height?: string;
}

interface Emits {
  (e: "data-changed", data: any[]): void;
  (e: "error", error: string): void;
}

const props = withDefaults(defineProps<Props>(), {
  showControls: true,
  allowExport: true,
  showDataPreview: false,
  autoExecute: true,
  pollInterval: undefined,
  height: "500px",
});

const emit = defineEmits<Emits>();
const baseChartRef = ref<InstanceType<typeof BaseChart>>();
const showExportMenu = ref(false);

// Set up SQL query execution
const sqlQuery = useSqlQuery({
  sql: props.sql,
  dataSources: [props.dataSource],
  autoExecute: props.autoExecute,
  pollInterval: props.pollInterval,
});

const {
  isLoading,
  error,
  result: queryResult,
  executeQuery,
  retry,
  cleanup,
} = sqlQuery;

/** Process raw SQL data into Sankey chart format */
const sankeyData = computed(() => {
  if (!queryResult.value?.data || queryResult.value.data.length === 0) {
    return { nodes: [], links: [] };
  }

  const nodes = new Set<string>();
  const links: Array<{ source: string; target: string; value: number }> = [];

  // Process each row: subject_category → predicate → object_category
  queryResult.value.data.forEach((row: any) => {
    const subjectCategory = row.subject_category || "Unknown Subject";
    const predicate = row.predicate || "Unknown Predicate";
    const objectCategory = row.object_category || "Unknown Object";
    const count = Number(row.count) || 0;

    // Add nodes
    nodes.add(subjectCategory);
    nodes.add(predicate);
    nodes.add(objectCategory);

    // Add links: subject_category → predicate
    links.push({
      source: subjectCategory,
      target: predicate,
      value: count,
    });

    // Add links: predicate → object_category
    links.push({
      source: predicate,
      target: objectCategory,
      value: count,
    });
  });

  return {
    nodes: Array.from(nodes).map((name) => ({ name })),
    links,
  };
});

/** Generate ECharts Sankey configuration */
const chartOptions = computed((): EChartsOption => {
  const { nodes, links } = sankeyData.value;

  return {
    tooltip: {
      trigger: "item",
      triggerOn: "mousemove",
      formatter: function (params: any) {
        if (params.dataType === "edge") {
          return `${params.data.source} → ${params.data.target}<br/>Count: ${params.data.value.toLocaleString()}`;
        } else {
          return `${params.data.name}<br/>Node`;
        }
      },
    },
    series: [
      {
        type: "sankey",
        data: nodes,
        links: links,
        emphasis: {
          focus: "adjacency",
        },
        levels: [
          {
            depth: 0,
            itemStyle: {
              color: "#3b82f6", // Blue for subject categories
            },
          },
          {
            depth: 1,
            itemStyle: {
              color: "#10b981", // Green for predicates
            },
          },
          {
            depth: 2,
            itemStyle: {
              color: "#f59e0b", // Orange for object categories
            },
          },
        ],
        lineStyle: {
          color: "gradient",
          curveness: 0.5,
        },
        label: {
          fontSize: 12,
          fontWeight: "normal",
        },
        left: "5%",
        top: "10%",
        right: "15%",
        bottom: "10%",
      },
    ],
  };
});

/** Update chart when data changes */
const updateChart = () => {
  if (baseChartRef.value?.chart && sankeyData.value.nodes.length > 0) {
    baseChartRef.value.updateChart(chartOptions.value);
  }
};

/** Handle retry action */
const handleRetry = async (): Promise<void> => {
  try {
    await retry();
  } catch (err) {
    emit("error", err instanceof Error ? err.message : "Retry failed");
  }
};

/** Handle export action */
const handleExport = (): void => {
  if (!baseChartRef.value?.chart) return;
  showExportMenu.value = true;
};

/** Export functions */
const generateFilename = (): string => {
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
  return `${props.title.replace(/\s+/g, "_").toLowerCase()}_${timestamp}`;
};

const exportAsPNG = (): void => {
  if (!baseChartRef.value?.chart) return;
  const url = baseChartRef.value.chart.getDataURL({
    type: "png",
    pixelRatio: 2,
    backgroundColor: "#fff",
  });
  downloadFile(url, `${generateFilename()}.png`);
  showExportMenu.value = false;
};

const exportAsSVG = (): void => {
  if (!baseChartRef.value?.chart) return;

  // Use an extremely wide container to ensure labels don't get cut off
  const tempContainer = document.createElement("div");
  tempContainer.style.width = "2400px"; // Even wider!
  tempContainer.style.height = "900px";
  tempContainer.style.position = "absolute";
  tempContainer.style.left = "-9999px";
  tempContainer.style.backgroundColor = "#ffffff";
  document.body.appendChild(tempContainer);


  try {
    // Initialize chart with SVG renderer and explicit size
    const svgChart = echarts.init(tempContainer, null, {
      renderer: "svg",
      width: 2400,
      height: 900,
    });

    // Get current chart options
    const currentOptions = baseChartRef.value.chart.getOption();

    // Create completely new options optimized for export
    const exportOptions = {
      title: currentOptions.title,
      tooltip: currentOptions.tooltip,
      series: [
        {
          type: "sankey",
          data: sankeyData.value.nodes,
          links: sankeyData.value.links,
          // Use pixel positioning for precise control - with HUGE right margin
          left: 80,
          top: 80,
          right: 800, // 800px margin for labels!
          bottom: 80,
          emphasis: {
            focus: "adjacency",
          },
          levels: [
            {
              depth: 0,
              itemStyle: { color: "#3b82f6" },
            },
            {
              depth: 1,
              itemStyle: { color: "#10b981" },
            },
            {
              depth: 2,
              itemStyle: { color: "#f59e0b" },
            },
          ],
          lineStyle: {
            color: "gradient",
            curveness: 0.5,
          },
          label: {
            show: true,
            position: "right",
            fontSize: 12,
            fontWeight: "normal",
            color: "#1f2937",
          },
        },
      ],
    };

    svgChart.setOption(exportOptions);

    // Give the chart time to render and then export
    setTimeout(() => {
      try {
        let svgString = svgChart.renderToSVGString();

        // Remove viewBox constraint so SVG doesn't scale content to fit
        svgString = svgString.replace(/viewBox="[^"]*"/, "");

        // Also ensure the SVG has proper dimensions without scaling
        svgString = svgString.replace(
          /<svg[^>]*>/,
          '<svg width="2400" height="900" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" baseProfile="full">',
        );


        const blob = new Blob([svgString], { type: "image/svg+xml" });
        const url = URL.createObjectURL(blob);
        downloadFile(url, `${generateFilename()}.svg`);
        URL.revokeObjectURL(url);
      } catch (err) {
        console.error("SVG string generation failed:", err);
      } finally {
        svgChart.dispose();
        document.body.removeChild(tempContainer);
        showExportMenu.value = false;
      }
    }, 300);
  } catch (error) {
    console.error("SVG export failed:", error);
    document.body.removeChild(tempContainer);
    showExportMenu.value = false;
  }
};

const exportAsHighResPNG = (): void => {
  if (!baseChartRef.value?.chart) return;
  const url = baseChartRef.value.chart.getDataURL({
    type: "png",
    pixelRatio: 4,
    backgroundColor: "#fff",
  });
  downloadFile(url, `${generateFilename()}_hires.png`);
  showExportMenu.value = false;
};

const exportAsJSON = (): void => {
  const exportData = {
    title: props.title,
    sql: props.sql,
    data: queryResult.value?.data || [],
    sankeyData: sankeyData.value,
    timestamp: new Date().toISOString(),
  };
  const dataStr = JSON.stringify(exportData, null, 2);
  const blob = new Blob([dataStr], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  downloadFile(url, `${generateFilename()}.json`);
  URL.revokeObjectURL(url);
  showExportMenu.value = false;
};

/** Helper function to download files */
const downloadFile = (url: string, filename: string): void => {
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// Watch for data changes and update chart
watch(
  () => queryResult.value,
  () => {
    updateChart();
    if (queryResult.value?.data) {
      emit("data-changed", queryResult.value.data);
    }
  },
  { deep: true },
);

// Watch for errors and emit events
watch(error, (newError) => {
  if (newError) {
    emit("error", newError);
  }
});

// Execute query on mount if auto-execute is disabled
onMounted(async () => {
  if (!props.autoExecute) {
    try {
      await executeQuery();
    } catch (err) {
      // Error is already handled by the composable
    }
  }
});

onUnmounted(() => {
  cleanup();
});
</script>

<style lang="scss" scoped>
.export-overlay {
  display: flex;
  z-index: 1000;
  position: fixed;
  top: 0;
  left: 0;
  align-items: center;
  justify-content: center;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
}

.export-menu {
  min-width: 400px;
  max-width: 500px;
  padding: 0;
  border-radius: 12px;
  background: white;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.export-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 16px;
  border-bottom: 1px solid #e5e7eb;

  h3 {
    margin: 0;
    color: #1f2937;
    font-weight: 600;
    font-size: 1.25rem;
  }
}

.close-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #6b7280;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background-color: #f3f4f6;
    color: #374151;
  }
}

.export-options {
  padding: 16px;
}

.export-option {
  display: flex;
  align-items: center;
  width: 100%;
  margin-bottom: 8px;
  padding: 16px;
  gap: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;

  &:last-child {
    margin-bottom: 0;
  }

  &:hover {
    transform: translateY(-1px);
    border-color: #3b82f6;
    background-color: #f8faff;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
  }

  &:active {
    transform: translateY(0);
  }
}

.export-icon {
  flex-shrink: 0;
  font-size: 24px;
  line-height: 1;
}

.export-details {
  flex: 1;
  text-align: left;
}

.export-title {
  margin-bottom: 2px;
  color: #1f2937;
  font-weight: 600;
  font-size: 0.95rem;
}

.export-desc {
  color: #6b7280;
  font-size: 0.85rem;
  line-height: 1.3;
}

@media (max-width: 480px) {
  .export-menu {
    min-width: auto;
    margin: 20px;
  }

  .export-option {
    padding: 12px;
    gap: 12px;
  }

  .export-icon {
    font-size: 20px;
  }

  .export-title {
    font-size: 0.9rem;
  }

  .export-desc {
    font-size: 0.8rem;
  }
}
</style>
