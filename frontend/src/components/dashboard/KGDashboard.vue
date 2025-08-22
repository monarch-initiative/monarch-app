<template>
  <div class="kg-dashboard-wrapper">
    <!-- Dashboard initialization status -->
    <div v-if="isInitializing" class="dashboard-loading">
      <AppIcon icon="loading" />
      <span>Initializing Knowledge Graph Dashboard...</span>
    </div>

    <div v-else-if="initError" class="dashboard-error">
      <AppIcon icon="alert-triangle" />
      <div class="error-content">
        <h3>Dashboard Initialization Failed</h3>
        <p>{{ initError }}</p>
        <AppButton text="Retry" @click="retryInit" />
      </div>
    </div>

    <!-- Dashboard content -->
    <div v-else class="dashboard-content">
      <!-- Data source info panel (collapsible) -->
      <div v-if="showDataSourceInfo" class="data-source-panel">
        <div class="panel-header">
          <h4>
            <AppIcon icon="database" />
            Data Sources ({{ registeredSources.length }})
          </h4>
          <AppButton
            :text="showDataSourceDetails ? 'Hide Details' : 'Show Details'"
            design="small"
            color="secondary"
            @click="toggleDataSourceInfo"
          />
        </div>

        <div v-if="showDataSourceDetails" class="panel-content">
          <div v-if="registeredSources.length === 0" class="no-sources">
            <p>
              No data sources registered yet. Add DataSource components to
              declare your parquet files.
            </p>
          </div>

          <div v-else class="source-list">
            <div
              v-for="source in registeredSources"
              :key="source.name"
              class="source-item"
              :class="{ loaded: source.isLoaded, error: source.loadError }"
            >
              <div class="source-header">
                <strong>{{ source.name }}</strong>
                <span class="source-status">
                  <AppIcon
                    v-if="source.isLoaded"
                    icon="check-circle"
                    style="color: #10b981"
                  />
                  <AppIcon
                    v-else-if="source.loadError"
                    icon="x-circle"
                    style="color: #ef4444"
                  />
                  <AppIcon v-else icon="clock" style="color: #6b7280" />
                </span>
              </div>

              <div class="source-details">
                <p class="source-url">{{ getSourceUrl(source) }}</p>
                <p v-if="source.description" class="source-description">
                  {{ source.description }}
                </p>
                <p v-if="source.loadError" class="source-error">
                  Error: {{ source.loadError }}
                </p>
                <p v-if="source.lastLoaded" class="source-loaded">
                  Loaded: {{ formatDate(source.lastLoaded) }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Dashboard slot content - only render after initialization -->
      <div v-if="!isInitializing && !initError">
        <slot />
      </div>
    </div>

    <!-- Debug panel (development only) -->
    <div v-if="showDebugInfo && isDevelopment" class="debug-panel">
      <details>
        <summary>🔍 Debug Info</summary>
        <div class="debug-content">
          <h5>KG Version: {{ kgVersion || "Not loaded" }}</h5>
          <h5>Source URL: {{ kgSourceUrl || "Not set" }}</h5>
          <h5>Registered Sources: {{ registeredSources.length }}</h5>
          <h5>Loaded Sources: {{ loadedSources.length }}</h5>
        </div>
      </details>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, provide, ref } from "vue";
import AppButton from "@/components/AppButton.vue";
import AppIcon from "@/components/AppIcon.vue";
import { useKGData, type DataSourceConfig } from "@/composables/use-kg-data";

interface Props {
  showDataSourceInfo?: boolean;
  showDebugInfo?: boolean;
  autoInit?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  showDataSourceInfo: true,
  showDebugInfo: false,
  autoInit: true,
});

const showDataSourceDetails = ref(false);
const isInitializing = ref(false);
const initError = ref<string | null>(null);

// Initialize KG data system
const kgData = useKGData();
const {
  kgVersion,
  kgSourceUrl,
  init,
  registerDataSource,
  getAllDataSources,
  getLoadedDataSources,
} = kgData;

const registeredSources = computed(() => getAllDataSources.value);
const loadedSources = computed(() => getLoadedDataSources.value);
const isDevelopment = computed(() => import.meta.env.DEV);

/** Initialize the dashboard */
const initDashboard = async (): Promise<void> => {
  try {
    isInitializing.value = true;
    initError.value = null;
    await init();
  } catch (err) {
    initError.value =
      err instanceof Error ? err.message : "Failed to initialize dashboard";
    console.error("Dashboard initialization failed:", err);
  } finally {
    isInitializing.value = false;
  }
};

/** Retry initialization */
const retryInit = async (): Promise<void> => {
  await initDashboard();
};

/** Toggle data source info panel */
const toggleDataSourceInfo = (): void => {
  showDataSourceDetails.value = !showDataSourceDetails.value;
};

/** Get full URL for a data source */
const getSourceUrl = (source: any): string => {
  if (source.baseUrl) {
    return `${source.baseUrl}/${source.url}`;
  }
  return source.url;
};

/** Format date for display */
const formatDate = (date: Date): string => {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
};

/** Handle data source registration from child DataSource components */
const handleRegisterDataSource = (config: DataSourceConfig): void => {
  registerDataSource(config);
};

/** Handle data source unregistration (when DataSource components unmount) */
const handleUnregisterDataSource = (name: string): void => {
  // Note: The composable doesn't have an unregister method yet
  // For now, we'll just log this - in practice, data sources usually persist
  console.debug(`DataSource "${name}" component unmounted`);
};

// Provide context for child DataSource components and KGMetricCard components
provide("dashboard-context", {
  registerDataSource: handleRegisterDataSource,
  unregisterDataSource: handleUnregisterDataSource,
});

// Provide the KG data instance for child components to use
provide("kg-data", kgData);

// Auto-initialize on mount if enabled
onMounted(async () => {
  if (props.autoInit) {
    await initDashboard();
  }
});
</script>

<style lang="scss" scoped>
.kg-dashboard-wrapper {
  width: 100%;
  min-height: 200px;
}

.dashboard-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  gap: 1rem;
  color: #6b7280;

  .icon {
    font-size: 2rem;
    animation: spin 1s linear infinite;
  }
}

.dashboard-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  gap: 1rem;
  color: #ef4444;

  .icon {
    font-size: 2rem;
  }

  .error-content {
    text-align: center;

    h3 {
      margin: 0 0 0.5rem 0;
      color: #dc2626;
    }

    p {
      margin: 0 0 1rem 0;
      color: #7f1d1d;
    }
  }
}

.dashboard-content {
  width: 100%;
}

.data-source-panel {
  margin-bottom: 2rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fafafa;

  .panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem;
    border-bottom: 1px solid #e5e7eb;

    h4 {
      display: flex;
      align-items: center;
      margin: 0;
      gap: 0.5rem;
      color: #374151;
      font-size: 1rem;

      .icon {
        color: #3b82f6;
      }
    }
  }

  .panel-content {
    padding: 1rem;
  }

  .no-sources {
    color: #6b7280;
    font-style: italic;
    text-align: center;

    p {
      margin: 0;
    }
  }

  .source-list {
    display: grid;
    gap: 1rem;
  }

  .source-item {
    padding: 1rem;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    background: white;

    &.loaded {
      border-color: #10b981;
      background: #f0fdf4;
    }

    &.error {
      border-color: #ef4444;
      background: #fef2f2;
    }

    .source-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 0.5rem;

      strong {
        color: #1f2937;
        font-size: 0.875rem;
      }
    }

    .source-details {
      font-size: 0.75rem;
      line-height: 1.4;

      p {
        margin: 0.25rem 0;
      }

      .source-url {
        color: #6b7280;
        font-family: monospace;
        word-break: break-all;
      }

      .source-description {
        color: #4b5563;
      }

      .source-error {
        color: #dc2626;
        font-weight: 500;
      }

      .source-loaded {
        color: #059669;
        font-weight: 500;
      }
    }
  }
}

.debug-panel {
  margin-top: 2rem;
  padding: 1rem;
  border: 1px dashed #d1d5db;
  border-radius: 6px;
  background: #f9fafb;
  font-size: 0.75rem;

  details {
    summary {
      color: #374151;
      font-weight: 600;
      cursor: pointer;
    }

    .debug-content {
      margin-top: 0.5rem;
      padding-top: 0.5rem;
      border-top: 1px solid #e5e7eb;

      h5 {
        margin: 0.25rem 0;
        color: #6b7280;
        font-weight: 500;
      }
    }
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .panel-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .source-item {
    padding: 0.75rem;
  }
}
</style>
