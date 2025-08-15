<template>
  <AppBreadcrumb />
  <PageTitle id="kg-sources" title="Monarch Knowledge Graph Sources" />
  <AppSection>
    <AppStatus v-if="isLoading" code="loading">Loading sources...</AppStatus>
    <AppStatus v-else-if="isError" code="error"
      >Error loading sources</AppStatus
    >

    <div v-else class="tab-container">
      <div class="tabs">
        <div class="tab-item" :class="{ active: activeTab === 'primary' }">
          <AppButton
            text="Primary Sources"
            color="none"
            :class="{ active: activeTab === 'primary' }"
            @click="activeTab = 'primary'"
          />
          <p class="tab-description">List of direct data sources</p>
        </div>
        <div class="tab-item" :class="{ active: activeTab === 'aggregator' }">
          <AppButton
            text="Aggregator Sources"
            color="none"
            :class="{ active: activeTab === 'aggregator' }"
            @click="activeTab = 'aggregator'"
          />
          <p class="tab-description">Sources that aggregate data</p>
        </div>
      </div>

      <table class="sources-table">
        <thead>
          <tr>
            <th>Resource</th>
            <th>Link</th>
            <th>Associations</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="source in currentSources" :key="source.id">
            <td>{{ resourceFullName(source.label) }}</td>
            <td>
              <a :href="generateInforesLink(source.id)" target="_blank">{{
                source.id
              }}</a>
            </td>
            <td>{{ source.count }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </AppSection>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import AppSection from "@/components/AppSection.vue";
import PageTitle from "@/components/ThePageTitle.vue";
import { useKnowledgeSources } from "@/composables/use-knowledge-sources";
import { RESOURCE_NAME_MAP } from "@/config/resourceNames";

const activeTab = ref<"primary" | "aggregator">("primary");

const {
  primarySources,
  aggregatorSources,
  isLoadingPrimary,
  isLoadingAggregator,
  isErrorPrimary,
  isErrorAggregator,
  fetchAll,
} = useKnowledgeSources();

onMounted(() => fetchAll());

function generateInforesLink(id: string) {
  return `https://w3id.org/information-resource-registry/${id.replace("infores:", "")}`;
}
const resourceFullName = (label?: string) =>
  RESOURCE_NAME_MAP[(label ?? "").toUpperCase()] ?? label ?? "";
const currentSources = computed(() =>
  activeTab.value === "primary"
    ? primarySources.value
    : aggregatorSources.value,
);
const isLoading = computed(
  () => isLoadingPrimary.value || isLoadingAggregator.value,
);
const isError = computed(() => isErrorPrimary.value || isErrorAggregator.value);
</script>

<style scoped>
.tab-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  padding: 1rem;
}

.sources-table {
  width: 100%;
  margin-top: 1rem;
  border-collapse: collapse;
  table-layout: fixed;
}

.sources-table th,
.sources-table td {
  padding: 12px;
  border: 1px solid #ddd;
  text-align: left;
  word-wrap: break-word;
}

.sources-table th {
  background-color: #f5f5f5;
  font-weight: bold;
}

.tabs {
  display: flex;
  width: 100%;
  margin-bottom: 1rem;
  background-color: #fff;
}

.tab-item {
  display: flex;
  flex: 1;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.tab-item.active {
  border: 1px solid #ccc;
  border-bottom: 3px solid #008080;
  background-color: #008080;
  color: #fff;
}

.tab-item.active .tab-description {
  color: #fff;
}

.tab-item.active :deep(.button) {
  color: #fff !important;
}

.tab-item:not(.active) {
  border: 1px solid transparent;
  border-bottom: 3px solid #008080;
  background-color: #f5f5f5;
}

.tab-item:not(.active) .tab-description {
  color: #555;
}

.tab-description {
  padding-bottom: 0.2em;
  font-size: 0.8em;
}

:deep(.button) {
  width: 100%;
  border: none;
  background-color: transparent;
  font-weight: bold;
  cursor: pointer;
  &:hover,
  &:focus {
    outline: none !important;
    box-shadow: none !important;
  }
}
</style>
