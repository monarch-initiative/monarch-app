<template>
  <BaseChart
    :title="title"
    :is-loading="isLoading"
    :error="error"
    :data="queryResult?.data"
    :show-controls="false"
    :allow-export="false"
    :show-data-preview="false"
    height="auto"
    @retry="handleRetry"
  >
    <div class="metric-content">
      <div
        class="metric-value"
        :class="{ loading: isLoading, error: hasError }"
      >
        <span v-if="!isLoading && !hasError" class="value">
          {{ formattedValue }}
        </span>

        <div v-if="subtitle" class="metric-subtitle">
          {{ subtitle }}
        </div>

        <div
          v-if="showTrend && trendValue !== null"
          class="metric-trend"
          :class="trendClass"
        >
          <AppIcon :icon="trendIcon" />
          <span>{{ Math.abs(trendValue || 0) }}{{ trendSuffix }}</span>
        </div>
      </div>

      <div v-if="description" class="metric-description">
        {{ description }}
      </div>
    </div>
  </BaseChart>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, watch } from "vue";
import AppIcon from "@/components/AppIcon.vue";
import { useSqlQuery } from "@/composables/use-sql-query";
import BaseChart from "./BaseChart.vue";

export interface Props {
  title: string;
  dataSource: string;
  sql: string;
  format?: "number" | "currency" | "percentage" | "bytes" | "duration";
  subtitle?: string;
  description?: string;
  autoExecute?: boolean;
  pollInterval?: number;
  showTrend?: boolean;
  trendValue?: number | null;
  trendSuffix?: string;
}

interface Emits {
  (e: "value-changed", value: any): void;
  (e: "error", error: string): void;
}

const props = withDefaults(defineProps<Props>(), {
  format: "number",
  autoExecute: true,
  trendSuffix: "%",
});

const emit = defineEmits<Emits>();

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

const hasError = computed(() => !!error.value);
const rawValue = computed(() => sqlQuery.getSingleValue.value);

/** Format the metric value based on the specified format */
const formattedValue = computed(() => {
  const value = rawValue.value;

  if (value === null || value === undefined) {
    return "—";
  }

  const numValue = Number(value);

  if (isNaN(numValue)) {
    return String(value);
  }

  switch (props.format) {
    case "number":
      return numValue.toLocaleString();

    case "currency":
      return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
      }).format(numValue);

    case "percentage":
      return `${(numValue * 100).toFixed(1)}%`;

    case "bytes":
      return formatBytes(numValue);

    case "duration":
      return formatDuration(numValue);

    default:
      return numValue.toLocaleString();
  }
});

/** Format bytes into human readable format */
const formatBytes = (bytes: number): string => {
  if (bytes === 0) return "0 B";

  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
};

/** Format duration in milliseconds into human readable format */
const formatDuration = (ms: number): string => {
  if (ms < 1000) return `${ms.toFixed(0)}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  if (ms < 3600000) return `${(ms / 60000).toFixed(1)}m`;
  return `${(ms / 3600000).toFixed(1)}h`;
};

/** Compute trend class based on trend value */
const trendClass = computed(() => {
  if (props.trendValue === null || props.trendValue === undefined) return "";

  return {
    positive: props.trendValue > 0,
    negative: props.trendValue < 0,
    neutral: props.trendValue === 0,
  };
});

/** Compute trend icon based on trend value */
const trendIcon = computed(() => {
  if (props.trendValue === null || props.trendValue === undefined) return "";

  if (props.trendValue > 0) return "trending-up";
  if (props.trendValue < 0) return "trending-down";
  return "minus";
});

/** Handle retry action */
const handleRetry = async (): Promise<void> => {
  try {
    await retry();
  } catch (err) {
    emit("error", err instanceof Error ? err.message : "Retry failed");
  }
};


// Watch for value changes and emit events
watch(rawValue, (newValue) => {
  if (newValue !== null && newValue !== undefined) {
    emit("value-changed", newValue);
  }
});

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
.metric-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px 16px;
  text-align: center;
}

.metric-value {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 12px;
  gap: 8px;

  &.loading {
    opacity: 0.5;
  }

  &.error {
    opacity: 0.3;
  }
}

.value {
  color: #1f2937;
  font-weight: 700;
  font-size: 2.5rem;
  line-height: 1;
}

.metric-subtitle {
  color: #6b7280;
  font-weight: 500;
  font-size: 0.875rem;
}

.metric-trend {
  display: flex;
  align-items: center;
  padding: 2px 6px;
  gap: 4px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.75rem;

  &.positive {
    background-color: #d1fae5;
    color: #059669;
  }

  &.negative {
    background-color: #fee2e2;
    color: #dc2626;
  }

  &.neutral {
    background-color: #f3f4f6;
    color: #6b7280;
  }
}

.metric-description {
  max-width: 300px;
  color: #6b7280;
  font-size: 0.75rem;
  line-height: 1.4;
  text-align: center;
}

/* Override BaseChart's min-height for metric cards */
:deep(.chart-content) {
  min-height: auto;
}

@media (max-width: 768px) {
  .value {
    font-size: 2rem;
  }

  .metric-content {
    padding: 12px;
  }
}
</style>
