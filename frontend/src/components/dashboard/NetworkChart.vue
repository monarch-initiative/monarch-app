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
    <!-- The actual Network chart will be rendered by ECharts in the BaseChart canvas -->

    <!-- Export Menu Overlay -->
    <button
      v-if="showExportMenu"
      class="export-overlay"
      role="dialog"
      aria-modal="true"
      aria-label="Export chart dialog"
      @click.self="showExportMenu = false"
      @keydown.escape="showExportMenu = false"
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
    </button>
  </BaseChart>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import * as echarts from "echarts";
import type { EChartsOption } from "echarts";
import AppIcon from "@/components/AppIcon.vue";
import { useSqlQuery } from "@/composables/use-sql-query";
import BaseChart from "./BaseChart.vue";

export interface Props {
  title: string;
  dataSource: string;
  sql: string;
  predicate?: string;
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
  predicate: "",
  showControls: true,
  allowExport: true,
  showDataPreview: false,
  autoExecute: true,
  pollInterval: undefined,
  height: "600px",
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

/** Process raw SQL data into Network graph format */
const networkData = computed(() => {
  if (!queryResult.value?.data || queryResult.value.data.length === 0) {
    return { nodes: [], links: [], selfLoops: new Map() };
  }

  const nodeSet = new Map<
    string,
    { name: string; value: number; selfLoopCount: number }
  >();
  const links: Array<{ source: string; target: string; value: number }> = [];
  const selfLoops = new Map<string, number>();

  queryResult.value.data.forEach((row: any) => {
    const source = row.subject_category || "Unknown";
    const target = row.object_category || "Unknown";
    const count = Number(row.count) || 0;

    // Initialize nodes
    if (!nodeSet.has(source)) {
      nodeSet.set(source, { name: source, value: 0, selfLoopCount: 0 });
    }
    if (!nodeSet.has(target)) {
      nodeSet.set(target, { name: target, value: 0, selfLoopCount: 0 });
    }

    // Handle self-loops separately
    if (source === target) {
      selfLoops.set(source, count);
      nodeSet.get(source)!.selfLoopCount = count;
      nodeSet.get(source)!.value += count;
    } else {
      // Regular connections
      nodeSet.get(source)!.value += count;
      nodeSet.get(target)!.value += count;

      links.push({
        source,
        target,
        value: count,
      });
    }
  });

  const nodes = Array.from(nodeSet.values());

  return { nodes, links, selfLoops };
});

/** Generate ECharts Network graph configuration */
const chartOptions = computed((): EChartsOption => {
  const { nodes, links } = networkData.value;

  if (nodes.length === 0) {
    return {};
  }

  // Calculate node sizes based on their total connection values
  const maxNodeValue = Math.max(...nodes.map((n) => n.value), 1);
  const minNodeSize = 20;
  const maxNodeSize = 80;

  // Calculate zoom based on number of nodes to fit them in the panel
  const nodeCount = nodes.length;
  let zoom = 1.0;
  if (nodeCount > 15) {
    zoom = 0.55;
  } else if (nodeCount > 10) {
    zoom = 0.7;
  } else if (nodeCount > 7) {
    zoom = 0.85;
  }

  return {
    animation: false,
    grid: {
      left: "5%",
      right: "5%",
      top: "10%",
      bottom: "10%",
      containLabel: true,
    },
    tooltip: {
      trigger: "item",
      formatter: (params: any) => {
        if (params.dataType === "node") {
          const hasSelfLoop = params.data.selfLoopCount > 0;
          let tooltip = `<strong>${params.data.name}</strong><br/>`;
          tooltip += `Total connections: ${params.data.value.toLocaleString()}`;
          if (hasSelfLoop && props.predicate) {
            tooltip += `<br/><span style="color: #3b82f6;">↻ ${params.data.name} ${props.predicate} ${params.data.name}: ${params.data.selfLoopCount.toLocaleString()}</span>`;
          }
          return tooltip;
        } else if (params.dataType === "edge") {
          const predicate = props.predicate || "relates to";
          return `<strong>${params.data.source} → ${predicate} → ${params.data.target}</strong><br/>Count: ${params.data.value.toLocaleString()}`;
        }
        return "";
      },
    },
    series: [
      {
        type: "graph",
        layout: "force",
        data: nodes.map((node) => {
          const hasSelfLoop = node.selfLoopCount > 0;
          return {
            name: node.name,
            value: node.value,
            selfLoopCount: node.selfLoopCount,
            symbolSize:
              minNodeSize +
              (node.value / maxNodeValue) * (maxNodeSize - minNodeSize),
            label: {
              show: true,
              position: "top" as const,
              fontSize: 10,
              fontWeight: "normal",
              color: "#374151",
            },
            itemStyle: {
              color: generateColor(node.name),
              borderColor: hasSelfLoop ? "#3b82f6" : "#fff",
              borderWidth: hasSelfLoop ? 3 : 2,
              shadowColor: hasSelfLoop
                ? "rgba(59, 130, 246, 0.5)"
                : "transparent",
              shadowBlur: hasSelfLoop ? 10 : 0,
            },
          };
        }),
        links: links.map((link) => ({
          source: link.source,
          target: link.target,
          value: link.value,
          lineStyle: {
            width: Math.max(1, Math.min(10, link.value / 100000)),
            opacity: 0.6,
            curveness: 0.2,
          },
          symbol: ["none", "arrow"],
          symbolSize: [0, 12],
          symbolOffset: [0, -5],
        })),
        emphasis: {
          focus: "adjacency",
          label: {
            fontSize: 14,
          },
          lineStyle: {
            width: 2,
          },
        },
        force: {
          repulsion: 600,
          edgeLength: [120, 280],
          gravity: 0.15,
          layoutAnimation: false,
          friction: 0.6,
        },
        center: ["50%", "50%"],
        zoom: zoom,
        scaleLimit: {
          min: 0.5,
          max: 1.5,
        },
        animation: false,
        animationDuration: 0,
        animationEasing: "linear",
        lineStyle: {
          color: "source",
          curveness: 0.3,
        },
      },
    ],
  };
});

/** Generate color based on category name */
const generateColor = (name: string): string => {
  const colors = [
    "#5470c6",
    "#91cc75",
    "#fac858",
    "#ee6666",
    "#73c0de",
    "#3ba272",
    "#fc8452",
    "#9a60b4",
    "#ea7ccc",
  ];

  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return colors[Math.abs(hash) % colors.length];
};

/** Update chart when data changes */
const updateChart = () => {
  if (baseChartRef.value?.chart && networkData.value.nodes.length > 0) {
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

  const tempContainer = document.createElement("div");
  tempContainer.style.width = "1200px";
  tempContainer.style.height = "800px";
  tempContainer.style.position = "absolute";
  tempContainer.style.left = "-9999px";
  document.body.appendChild(tempContainer);

  try {
    const svgChart = echarts.init(tempContainer, null, {
      renderer: "svg",
      width: 1200,
      height: 800,
    });

    svgChart.setOption(chartOptions.value);

    setTimeout(() => {
      try {
        let svgString = svgChart.renderToSVGString();
        svgString = svgString.replace(/viewBox="[^"]*"/, "");
        svgString = svgString.replace(
          /<svg[^>]*>/,
          '<svg width="1200" height="800" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" baseProfile="full">',
        );

        const blob = new Blob([svgString], { type: "image/svg+xml" });
        const url = URL.createObjectURL(blob);
        downloadFile(url, `${generateFilename()}.svg`);
        URL.revokeObjectURL(url);
      } catch (err) {
        console.error("SVG export failed:", err);
      } finally {
        svgChart.dispose();
        document.body.removeChild(tempContainer);
        showExportMenu.value = false;
      }
    }, 200);
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
    networkData: networkData.value,
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
