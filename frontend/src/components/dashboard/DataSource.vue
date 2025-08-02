<template>
  <!-- DataSource is a declarative component - it doesn't render anything -->
  <div style="display: none"></div>
</template>

<script setup lang="ts">
import { inject, onMounted, onUnmounted } from "vue";
import type { DataSourceConfig } from "@/composables/use-kg-data";

interface Props {
  name: string;
  url: string;
  description?: string;
  baseUrl?: string;
}

const props = defineProps<Props>();

// Inject the dashboard context
const dashboardContext = inject<{
  registerDataSource: (config: DataSourceConfig) => void;
  unregisterDataSource: (name: string) => void;
} | null>("dashboard-context", null);

if (!dashboardContext) {
  console.warn(
    `DataSource "${props.name}" is being used outside of a KGDashboard context. ` +
      "Make sure to wrap your DataSource components in a KGDashboard component.",
  );
}

// Register the data source immediately when component is created
if (dashboardContext) {
  dashboardContext.registerDataSource({
    name: props.name,
    url: props.url,
    description: props.description,
    baseUrl: props.baseUrl,
  });
}

// Unregister when component unmounts
onUnmounted(() => {
  if (dashboardContext) {
    dashboardContext.unregisterDataSource(props.name);
  }
});
</script>

<style scoped>
/* No visual styling needed - this is a declarative component */
</style>
