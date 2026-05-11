<template>
  <AppBreadcrumb />
  <PageTitle id="kg-sources" title="Monarch Knowledge Graph Sources" />
  <AppSection>
    <AppStatus v-if="isLoading" code="loading">Loading sources...</AppStatus>
    <AppStatus v-else-if="isError" code="error"
      >Error loading sources</AppStatus
    >

    <div v-else class="tab-container">
      <p v-if="versionsRelease" class="receipt-subtitle">
        Versions as of monarch-kg release
        <strong>{{ versionsRelease }}</strong>
      </p>

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
            <th>Version</th>
            <th>Associations</th>
            <th v-if="activeTab === 'primary'">Dashboard</th>
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
            <td class="version-cell">
              <template v-if="versionsById[source.id]">
                <span v-if="versionsById[source.id].version">{{
                  versionsById[source.id].version
                }}</span>
                <span v-else class="muted">unknown</span>
              </template>
              <span v-else class="muted">—</span>
            </td>
            <td>{{ source.count.toLocaleString() }}</td>
            <td v-if="activeTab === 'primary'">
              <router-link
                :to="`/kg/sources/${source.id.replace('infores:', '')}`"
                class="explore-link"
              >
                Explore in KG
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </AppSection>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import type { SourceVersion } from "@/api/source-versions";
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import AppSection from "@/components/AppSection.vue";
import PageTitle from "@/components/ThePageTitle.vue";
import { useKnowledgeSources } from "@/composables/use-knowledge-sources";
import { useSourceVersions } from "@/composables/use-source-versions";
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

const { data: versionsData, versionForInfores } = useSourceVersions();

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

/**
 * Resolve every visible source to a version once per render, keyed by id, so
 * the template can reference values without calling the lookup repeatedly.
 */
const versionsById = computed<Record<string, SourceVersion>>(() => {
  const out: Record<string, SourceVersion> = {};
  for (const list of [primarySources.value, aggregatorSources.value]) {
    for (const source of list) {
      const v = versionForInfores(source.id);
      if (v) out[source.id] = v;
    }
  }
  return out;
});

const versionsRelease = computed(() => versionsData.value?.release ?? "");
</script>

<style lang="scss" scoped>
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
  border: 1px solid $light-gray;
  text-align: left;
  word-wrap: break-word;
}

.sources-table th {
  background-color: $off-white;
  font-weight: bold;
}

.muted {
  color: $gray;
}

.receipt-subtitle {
  width: 100%;
  margin: 0 0 0.75rem;
  color: $gray;
  font-size: 0.95em;
}

.explore-link {
  color: $theme;
  font-weight: 600;
  text-decoration: none;
}

.explore-link:hover {
  text-decoration: underline;
}

.tabs {
  display: flex;
  width: 100%;
  margin-bottom: 1rem;
  background-color: $white;
}

.tab-item {
  display: flex;
  flex: 1;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.tab-item.active {
  border: 1px solid $gray;
  border-bottom: 3px solid $theme;
  background-color: $theme;
  color: $white;
}

.tab-item.active .tab-description {
  color: $white;
}

.tab-item.active :deep(.button) {
  color: $white !important;
}

.tab-item:not(.active) {
  border: 1px solid transparent;
  border-bottom: 3px solid $theme;
  background-color: $off-white;
}

.tab-item:not(.active) .tab-description {
  color: $dark-gray;
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
