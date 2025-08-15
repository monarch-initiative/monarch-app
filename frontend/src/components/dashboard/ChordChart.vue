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
    <!-- The actual Chord chart will be rendered by ECharts in the BaseChart canvas -->
    
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

/** Process raw SQL data into Chord chart format */
const chordData = computed(() => {
  if (!queryResult.value?.data || queryResult.value.data.length === 0) {
    return { categories: [], matrix: [] };
  }

  // Collect all unique categories (nodes)
  const categorySet = new Set<string>();
  const connections = new Map<string, number>();

  queryResult.value.data.forEach((row: any) => {
    const subjectCategory = row.subject_category || 'Unknown Subject';
    const objectCategory = row.object_category || 'Unknown Object';
    const count = Number(row.count) || 0;

    categorySet.add(subjectCategory);
    categorySet.add(objectCategory);

    // Create bidirectional connection key
    const key1 = `${subjectCategory}→${objectCategory}`;
    const key2 = `${objectCategory}→${subjectCategory}`;
    
    connections.set(key1, (connections.get(key1) || 0) + count);
    connections.set(key2, (connections.get(key2) || 0) + count);
  });

  const categories = Array.from(categorySet);
  const matrix: number[][] = [];

  // Build adjacency matrix
  for (let i = 0; i < categories.length; i++) {
    matrix[i] = [];
    for (let j = 0; j < categories.length; j++) {
      if (i === j) {
        matrix[i][j] = 0;
      } else {
        const key = `${categories[i]}→${categories[j]}`;
        matrix[i][j] = connections.get(key) || 0;
      }
    }
  }

  return { categories, matrix };
});

/** Generate ECharts Chord configuration */
const chartOptions = computed((): any => {
  const { categories, matrix } = chordData.value;

  if (categories.length === 0) {
    return {};
  }

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
      trigger: 'item',
      position: function(point: number[], params: any, dom: any, rect: any, size: any) {
        console.log('Tooltip position called:', { point, params, size });
        
        // Safety checks for required parameters
        if (!point || !size || !size.contentSize) {
          console.log('Missing required parameters, using fallback');
          return [point[0] + 15, point[1] - 15]; // Fallback position
        }
        
        // For nodes, position tooltip outside the circle based on node position
        // Check if this is a node (not an edge/link)
        console.log('Checking params for node:', { dataType: params.dataType, seriesType: params.seriesType, data: params.data });
        
        if (params.dataType === 'node') {
          console.log('Processing node tooltip positioning');
          const chartWidth = size.contentSize[0];
          const chartHeight = size.contentSize[1];
          // Estimate tooltip size since tooltipSize isn't available yet
          const tooltipWidth = 300; // Approximate width based on our SVG
          const tooltipHeight = 200; // Approximate height
          
          // Use the actual circle center from our node positioning (300, 300 in our coordinate system)
          const centerX = 300; // This matches our circle center in the data positioning
          const centerY = 300; // This matches our circle center in the data positioning
          
          // Use the actual node position instead of mouse position for more accurate angle calculation
          const nodeX = params.data.x;
          const nodeY = params.data.y;
          
          console.log('Node actual position:', { nodeX, nodeY, centerX, centerY });
          
          // Calculate angle from center to actual node position
          const dx = nodeX - centerX;
          const dy = nodeY - centerY;
          const angle = Math.atan2(dy, dx);
          
          console.log('Tooltip positioning:', {
            point, centerX, centerY, dx, dy, angle: angle * 180 / Math.PI,
            isLeft: Math.cos(angle) < 0, isTop: Math.sin(angle) < 0
          });
          
          // Use mouse position as base, but adjust based on node's side of circle
          let x = point[0];
          let y = point[1];
          
          // Adjust tooltip position based on which side of circle the node is on
          if (Math.cos(angle) < 0) {
            // Left side - position tooltip to the left of mouse
            x = point[0] - tooltipWidth - 20;
          } else {
            // Right side - position tooltip to the right of mouse
            x = point[0] + 20;
          }
          
          if (Math.sin(angle) < 0) {
            // Top side - position tooltip above mouse
            y = point[1] - tooltipHeight - 20;
          } else {
            // Bottom side - position tooltip below mouse
            y = point[1] + 20;
          }
          
          console.log('Before clamping:', { x, y, point, chartWidth, chartHeight, tooltipWidth, tooltipHeight });
          
          // Allow tooltip to extend beyond chart bounds if needed
          const originalX = x;
          
          // Only clamp to prevent going off the viewport/page, not the chart container
          // Use much more generous bounds (assume viewport is at least 1200px wide)
          const viewportWidth = Math.max(1200, chartWidth * 3);
          const viewportHeight = Math.max(800, chartHeight * 3);
          
          if (Math.cos(angle) < 0) {
            // For left nodes, ensure tooltip doesn't go off left edge of viewport
            x = Math.max(10, x);
          } else {
            // For right nodes, ensure tooltip doesn't go off right edge of viewport
            x = Math.min(x, viewportWidth - tooltipWidth - 10);
          }
          
          // Clamp Y to reasonable viewport bounds
          y = Math.max(10, Math.min(y, viewportHeight - tooltipHeight - 10));
          
          console.log('After clamping:', { originalX, x, viewportWidth, isLeft: Math.cos(angle) < 0 });
          
          console.log('Final tooltip position:', { x, y, tooltipWidth, tooltipHeight });
          
          return [x, y];
        } else {
          // For edges/links, use default positioning
          return [point[0] + 15, point[1] - 15];
        }
      },
      formatter: function(params: any) {
        if (params.dataType === 'edge') {
          return `${categories[params.data.source]} ↔ ${categories[params.data.target]}<br/>Connections: ${params.data.value.toLocaleString()}`;
        } else if (params.dataType === 'node') {
          const nodeIndex = params.dataIndex;
          const nodeName = params.data.name;
          const totalConnections = params.data.value;
          
          // Get all connections for this node
          const connections = [];
          for (let i = 0; i < matrix[nodeIndex].length; i++) {
            if (i !== nodeIndex && matrix[nodeIndex][i] > 0) {
              connections.push({
                target: categories[i].replace('biolink:', ''),
                count: matrix[nodeIndex][i]
              });
            }
          }
          
          // Sort connections by count (descending)
          connections.sort((a, b) => b.count - a.count);
          
          let tooltip = `<strong>${nodeName}</strong><br/>`;
          tooltip += `Total Connections: ${totalConnections.toLocaleString()}<br/><br/>`;
          
          if (connections.length > 0) {
            tooltip += '<strong>Connections to:</strong><br/>';
            const connectionsToShow = connections; // Show all connections
            
            // Color palette matching our chart
            const colors = [
              '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
              '#06b6d4', '#84cc16', '#f97316', '#ec4899', '#6366f1'
            ];
            
            // Find max count for scaling bars, but use a more reasonable scale
            const maxCount = connectionsToShow[0].count;
            const minCount = connectionsToShow[connectionsToShow.length - 1].count;
            const maxBarWidth = 80;   // Max bar width in pixels
            const minBarWidth = 15;   // Min bar width in pixels
            const barHeight = 14;     // Bar height in pixels
            const labelWidth = 120;   // Space reserved for labels
            const barStartX = labelWidth + 10; // Where bars start
            
            // Create SVG bar chart with wider layout
            const svgHeight = connectionsToShow.length * 22 + 10;
            const svgWidth = labelWidth + maxBarWidth + 80; // Label + bar + count space
            let svgChart = `<svg width="${svgWidth}" height="${svgHeight}" style="margin: 5px 0;">`;
            
            connectionsToShow.forEach((conn, index) => {
              // Calculate bar width with better scaling
              const ratio = maxCount > minCount ? 
                (conn.count - minCount) / (maxCount - minCount) : 1;
              const barWidth = minBarWidth + (ratio * (maxBarWidth - minBarWidth));
              
              const y = index * 22 + 5;
              const color = colors[index % colors.length];
              
              // Keep full category name (don't truncate since we have space)
              const categoryName = conn.target;
              
              // Add category label (left side)
              svgChart += `<text x="5" y="${y + 10}" font-size="11" font-family="Arial, sans-serif" fill="#374151" font-weight="500">${categoryName}</text>`;
              
              // Add bar rectangle (middle)
              svgChart += `<rect x="${barStartX}" y="${y}" width="${barWidth}" height="${barHeight}" fill="${color}" opacity="0.8" rx="2"/>`;
              
              // Add count text (right side)
              svgChart += `<text x="${barStartX + barWidth + 8}" y="${y + 10}" font-size="11" font-family="Arial, sans-serif" fill="#374151">${conn.count.toLocaleString()}</text>`;
            });
            
            svgChart += '</svg>';
            tooltip += svgChart;
          } else {
            tooltip += '<em>No connections</em>';
          }
          
          return tooltip;
        }
        return `${params.data?.name || 'Unknown'}<br/>Category`;
      }
    },
    graphic: [{
      type: 'circle',
      shape: {
        cx: 300, // Center x in pixels
        cy: 300, // Center y in pixels  
        r: 220   // Radius in pixels
      },
      style: {
        fill: 'transparent',
        stroke: '#d1d5db',
        lineWidth: 2
      },
      silent: true,
      z: -1
    }],
    series: [{
      type: 'graph' as const,
      layout: 'none',
      data: categories.map((name, index) => {
        const angle = (2 * Math.PI * index) / categories.length;
        const radius = 220;
        const colors = [
          '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
          '#06b6d4', '#84cc16', '#f97316', '#ec4899', '#6366f1'
        ];
        return {
          name: name.replace('biolink:', ''),
          value: matrix[index].reduce((sum, val) => sum + val, 0),
          x: Math.cos(angle) * radius + 300,
          y: Math.sin(angle) * radius + 300,
          symbolSize: Math.max(15, Math.min(40, matrix[index].reduce((sum, val) => sum + val, 0) / 2000)),
          category: index,
          itemStyle: {
            color: colors[index % colors.length],
            borderWidth: 2,
            borderColor: '#fff'
          }
        };
      }),
      links: matrix.flatMap((row, i) =>
        row.map((value, j) => {
          const colors = [
            '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
            '#06b6d4', '#84cc16', '#f97316', '#ec4899', '#6366f1'
          ];
          return {
            source: i,
            target: j,
            value: value,
            lineStyle: {
              width: Math.max(2, Math.min(12, value / 3000)),
              curveness: 0.4,
              opacity: 0.7,
              color: colors[i % colors.length] // Use source node color
            }
          };
        }).filter(link => link.value > 0 && link.source !== link.target)
      ),
      categories: categories.map((name, index) => ({
        name: name.replace('biolink:', '')
      })),
      emphasis: {
        focus: 'adjacency',
        itemStyle: {
          borderWidth: 3,
          borderColor: '#333'
        },
        lineStyle: {
          width: 8,
          opacity: 0.9
        }
      },
      itemStyle: {
        borderWidth: 2,
        borderColor: '#fff'
      },
      lineStyle: {
        curveness: 0.4,
        opacity: 0.6
      },
      label: {
        show: true,
        position: 'outside',
        fontSize: 10,
        fontWeight: 'normal',
        color: '#374151',
        formatter: function(params: any) {
          const name = params.name;
          return name.length > 12 ? name.substring(0, 9) + '...' : name;
        }
      },
      roam: false,
      focusNodeAdjacency: true,
      animationDuration: 1500,
      animationEasingUpdate: 'quinticInOut'
    }]
  };
});

/** Update chart when data changes */
const updateChart = () => {
  if (baseChartRef.value?.chart && chordData.value.categories.length > 0) {
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
  
  // Create temporary SVG chart for export
  const tempContainer = document.createElement('div');
  tempContainer.style.width = '1200px';
  tempContainer.style.height = '800px';
  tempContainer.style.position = 'absolute';
  tempContainer.style.left = '-9999px';
  document.body.appendChild(tempContainer);
  
  try {
    const svgChart = echarts.init(tempContainer, null, { 
      renderer: 'svg',
      width: 1200,
      height: 800
    });
    
    svgChart.setOption(chartOptions.value);
    
    setTimeout(() => {
      try {
        let svgString = svgChart.renderToSVGString();
        svgString = svgString.replace(/viewBox="[^"]*"/, '');
        svgString = svgString.replace(
          /<svg[^>]*>/,
          '<svg width="1200" height="800" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" baseProfile="full">'
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
    chordData: chordData.value,
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