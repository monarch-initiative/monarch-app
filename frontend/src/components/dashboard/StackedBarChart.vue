<template>
  <BaseChart
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
    ref="baseChartRef"
  >
    <!-- The actual Stacked Bar chart will be rendered by ECharts in the BaseChart canvas -->
    
    <!-- Export Menu Overlay -->
    <div v-if="showExportMenu" class="export-overlay" @click.self="showExportMenu = false">
      <div class="export-menu">
        <div class="export-header">
          <h3>Export Chart</h3>
          <button @click="showExportMenu = false" class="close-button">×</button>
        </div>
        <div class="export-options">
          <button @click="exportAsPNG" class="export-option">
            <span class="export-icon">🖼️</span>
            <div class="export-details">
              <div class="export-title">PNG Image</div>
              <div class="export-desc">Standard resolution for web use</div>
            </div>
          </button>
          <button @click="exportAsHighResPNG" class="export-option">
            <span class="export-icon">📷</span>
            <div class="export-details">
              <div class="export-title">High-Res PNG</div>
              <div class="export-desc">4x resolution for print quality</div>
            </div>
          </button>
          <button @click="exportAsSVG" class="export-option">
            <span class="export-icon">📐</span>
            <div class="export-details">
              <div class="export-title">SVG Vector</div>
              <div class="export-desc">Scalable vector format</div>
            </div>
          </button>
          <button @click="exportAsJSON" class="export-option">
            <span class="export-icon">📄</span>
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
import BaseChart from "./BaseChart.vue";
import { useSqlQuery } from "@/composables/use-sql-query";

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
  orientation?: 'horizontal' | 'vertical';
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
  height: "400px",
  orientation: "vertical"
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

/** Process gene connection data into stacked bar format */
const stackedData = computed(() => {
  if (!queryResult.value?.data || queryResult.value.data.length === 0) {
    return { categories: [], series: [] };
  }

  // Process the boolean combinations into meaningful categories
  const processedData = queryResult.value.data.map((row: any) => {
    const count = Number(row.count || 0);
    const hasHumanPhenotype = row.has_phenotype_or_disease;
    const hasOrtholog = row.has_ortholog;
    const hasOrthologPhenotype = row.has_ortholog_phenotype;

    // Determine the information source category
    let category = 'No Information';
    if (hasHumanPhenotype && hasOrthologPhenotype) {
      category = 'Human + Ortholog Phenotypes';
    } else if (hasHumanPhenotype && !hasOrthologPhenotype) {
      category = 'Human Phenotypes Only';
    } else if (!hasHumanPhenotype && hasOrthologPhenotype) {
      category = 'Ortholog Phenotypes Only';
    } else {
      category = 'No Phenotype Information';
    }

    return {
      category,
      count,
      hasHumanPhenotype,
      hasOrtholog,
      hasOrthologPhenotype
    };
  });

  // Create series data for stacked bar
  const categories = ['Information Sources'];
  const seriesData = [
    {
      name: 'Human + Ortholog Phenotypes',
      type: 'bar' as const,
      stack: 'total',
      emphasis: { focus: 'series' },
      data: [processedData.find(d => d.category === 'Human + Ortholog Phenotypes')?.count || 0],
      itemStyle: { color: '#10b981' } // Green - best case
    },
    {
      name: 'Ortholog Phenotypes Only',
      type: 'bar' as const, 
      stack: 'total',
      emphasis: { focus: 'series' },
      data: [processedData.find(d => d.category === 'Ortholog Phenotypes Only')?.count || 0],
      itemStyle: { color: '#3b82f6' } // Blue - ortholog value
    },
    {
      name: 'Human Phenotypes Only',
      type: 'bar' as const,
      stack: 'total',
      emphasis: { focus: 'series' },
      data: [processedData.find(d => d.category === 'Human Phenotypes Only')?.count || 0],
      itemStyle: { color: '#f59e0b' } // Orange - human only
    },
    {
      name: 'No Phenotype Information',
      type: 'bar' as const,
      stack: 'total', 
      emphasis: { focus: 'series' },
      data: [processedData.find(d => d.category === 'No Phenotype Information')?.count || 0],
      itemStyle: { color: '#6b7280' } // Gray - no info
    }
  ];

  return { categories, series: seriesData, processedData };
});

/** Generate ECharts Stacked Bar configuration */
const chartOptions = computed((): any => {
  const { categories, series } = stackedData.value;

  if (categories.length === 0) {
    return {};
  }

  const isHorizontal = props.orientation === 'horizontal';

  return {
    title: {
      text: props.title,
      left: 'center',
      top: 20,
      textStyle: {
        fontSize: 16,
        fontWeight: 'normal'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params: any) {
        if (!Array.isArray(params) || params.length === 0) return '';
        
        const total = params.reduce((sum: number, p: any) => sum + p.value, 0);
        let tooltip = `<strong>Total Genes: ${total.toLocaleString()}</strong><br/>`;
        
        params.forEach((param: any) => {
          const percentage = total > 0 ? ((param.value / total) * 100).toFixed(1) : '0.0';
          tooltip += `${param.marker} ${param.seriesName}: ${param.value.toLocaleString()} (${percentage}%)<br/>`;
        });
        
        return tooltip;
      }
    },
    legend: {
      orient: 'horizontal',
      left: 'center',
      bottom: 10,
      textStyle: {
        fontSize: 11
      }
    },
    grid: {
      left: '10%',
      right: '10%',
      top: '20%',
      bottom: '25%',
      containLabel: true
    },
    xAxis: {
      type: isHorizontal ? 'value' : 'category',
      data: isHorizontal ? undefined : categories,
      axisLabel: {
        fontSize: 12,
        fontWeight: 'bold'
      }
    },
    yAxis: {
      type: isHorizontal ? 'category' : 'value',
      data: isHorizontal ? categories : undefined,
      axisLabel: {
        fontSize: 10,
        formatter: function(value: any) {
          if (isHorizontal) {
            return String(value);
          } else {
            const num = Number(value);
            if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
            if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
            return String(num);
          }
        }
      }
    },
    series: series.map(s => ({
      ...s,
      animationDelay: function(idx: number) {
        return idx * 100;
      }
    })),
    animationEasing: 'cubicOut',
    animationDuration: 1000
  };
});

/** Update chart when data changes */
const updateChart = () => {
  if (baseChartRef.value?.chart && stackedData.value.categories.length > 0) {
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
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  return `${props.title.replace(/\s+/g, '_').toLowerCase()}_${timestamp}`;
};

const exportAsPNG = (): void => {
  if (!baseChartRef.value?.chart) return;
  const url = baseChartRef.value.chart.getDataURL({
    type: 'png',
    pixelRatio: 2,
    backgroundColor: '#fff'
  });
  downloadFile(url, `${generateFilename()}.png`);
  showExportMenu.value = false;
};

const exportAsSVG = (): void => {
  if (!baseChartRef.value?.chart) return;
  
  const tempContainer = document.createElement('div');
  tempContainer.style.width = '800px';
  tempContainer.style.height = '600px';
  tempContainer.style.position = 'absolute';
  tempContainer.style.left = '-9999px';
  document.body.appendChild(tempContainer);
  
  try {
    const svgChart = echarts.init(tempContainer, null, { 
      renderer: 'svg',
      width: 800,
      height: 600
    });
    
    svgChart.setOption(chartOptions.value);
    
    setTimeout(() => {
      try {
        let svgString = svgChart.renderToSVGString();
        svgString = svgString.replace(/viewBox="[^"]*"/, '');
        svgString = svgString.replace(
          /<svg[^>]*>/,
          '<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" baseProfile="full">'
        );
        
        const blob = new Blob([svgString], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);
        downloadFile(url, `${generateFilename()}.svg`);
        URL.revokeObjectURL(url);
      } catch (err) {
        console.error('SVG export failed:', err);
      } finally {
        svgChart.dispose();
        document.body.removeChild(tempContainer);
        showExportMenu.value = false;
      }
    }, 200);
    
  } catch (error) {
    console.error('SVG export failed:', error);
    document.body.removeChild(tempContainer);
    showExportMenu.value = false;
  }
};

const exportAsHighResPNG = (): void => {
  if (!baseChartRef.value?.chart) return;
  const url = baseChartRef.value.chart.getDataURL({
    type: 'png',
    pixelRatio: 4,
    backgroundColor: '#fff'
  });
  downloadFile(url, `${generateFilename()}_hires.png`);
  showExportMenu.value = false;
};

const exportAsJSON = (): void => {
  const exportData = {
    title: props.title,
    sql: props.sql,
    data: queryResult.value?.data || [],
    stackedData: stackedData.value,
    timestamp: new Date().toISOString(),
  };
  const dataStr = JSON.stringify(exportData, null, 2);
  const blob = new Blob([dataStr], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  downloadFile(url, `${generateFilename()}.json`);
  URL.revokeObjectURL(url);
  showExportMenu.value = false;
};

/** Helper function to download files */
const downloadFile = (url: string, filename: string): void => {
  const link = document.createElement('a');
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
  { deep: true }
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
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000;
  display: flex;
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
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  gap: 16px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:last-child {
    margin-bottom: 0;
  }

  &:hover {
    border-color: #3b82f6;
    background-color: #f8faff;
    transform: translateY(-1px);
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
    margin: 20px;
    min-width: auto;
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