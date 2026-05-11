<template>
  <div class="source-dashboard">
    <AppBreadcrumb />
    <PageTitle id="source-dashboard" :title="sourceName" />

    <AppSection width="big">
      <!-- Source header info -->
      <div class="source-header">
        <p class="source-line">
          <span>
            <strong>Infores:</strong>
            <a
              :href="`https://w3id.org/information-resource-registry/${inforesId.replace('infores:', '')}`"
              target="_blank"
              rel="noopener"
              >{{ inforesId }}</a
            >
          </span>
          <span v-if="version">
            <strong>Version:</strong>
            {{ version.version || "unknown" }}
          </span>
          <span v-if="version?.version_method">
            <strong>Version method:</strong>
            {{ version.version_method }}
          </span>
          <span v-if="version?.retrieved_at">
            <strong>Retrieved:</strong>
            {{ version.retrieved_at }}
          </span>
          <button
            v-if="version?.urls.length"
            type="button"
            class="source-urls-toggle"
            :aria-expanded="urlsExpanded"
            @click="urlsExpanded = !urlsExpanded"
          >
            <strong>Source URLs:</strong>
            {{ version.urls.length }}
            <span class="caret" :class="{ open: urlsExpanded }">▾</span>
          </button>
        </p>
      </div>

      <div v-if="version?.urls.length && urlsExpanded" class="url-panel">
        <a
          v-for="url in version.urls"
          :key="url"
          class="url-chip"
          :href="url"
          target="_blank"
          rel="noopener"
        >
          {{ url }}
        </a>
      </div>

      <!-- Dashboard charts section (DuckDB-WASM powered) -->
      <KGDashboard :show-data-source-info="false">
        <DataSource
          name="edge_report"
          url="qc/edge_report.parquet"
          description="Edge/association statistics from KG quality control"
        />

        <SourceCharts
          :infores-id="inforesId"
          :source-name="sourceName"
          @filter-predicate="onFilterPredicate"
          @filter-category="onFilterCategory"
        />
      </KGDashboard>
    </AppSection>

    <!-- Association browser section (Solr API powered) — full width -->
    <AppSection width="full" alignment="left">
      <div class="browser-section">
        <h3>Association Browser</h3>
        <p class="section-description">
          Browse associations from this source with faceted filtering. Click on
          chart elements above to filter associations.
        </p>

        <SourceAssociationBrowser
          :infores-id="inforesId"
          :filters="filters"
          :filter-queries="filterQueries"
          :offset="offset"
          :limit="limit"
          :has-active-filters="hasActiveFilters"
          :set-filter="setFilter"
          :clear-filters="clearFilters"
          @update:offset="offset = $event"
          @update:limit="limit = $event"
        />
      </div>
    </AppSection>
  </div>
</template>

<script setup lang="ts">
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import AppSection from "@/components/AppSection.vue";
import DataSource from "@/components/dashboard/DataSource.vue";
import KGDashboard from "@/components/dashboard/KGDashboard.vue";
import SourceAssociationBrowser from "@/components/dashboard/SourceAssociationBrowser.vue";
import SourceCharts from "@/components/dashboard/SourceCharts.vue";
import PageTitle from "@/components/ThePageTitle.vue";
import { computed, ref } from "vue";
import { useSourceDashboard } from "@/composables/use-source-dashboard";
import { useSourceVersions } from "@/composables/use-source-versions";

const {
  inforesId,
  sourceName,
  filters,
  filterQueries,
  offset,
  limit,
  setFilter,
  clearFilters,
  hasActiveFilters,
} = useSourceDashboard();

const { versionForInfores } = useSourceVersions();
const version = computed(() => versionForInfores(inforesId.value));
const urlsExpanded = ref(false);

/** Handle chart click events to filter the association browser */
const onFilterPredicate = (predicate: string) => {
  setFilter("predicate", predicate);
};

const onFilterCategory = (
  category: string,
  type: "subjectCategory" | "objectCategory",
) => {
  setFilter(type, category);
};
</script>

<style lang="scss" scoped>
.source-dashboard {
  min-height: 100vh;
}

.source-header {
  display: flex;
  align-self: stretch;
  flex-direction: column;
  margin-bottom: 0.5rem;
  gap: 0.75rem;
  text-align: left;

  a {
    color: $theme;

    &:hover {
      text-decoration: underline;
    }
  }
}

.source-line {
  display: flex;
  flex: 1 1 auto;
  flex-wrap: wrap;
  align-items: center;
  margin: 0;
  gap: 0.5rem 1.5rem;
  color: $off-black;
  font-size: 0.95rem;
}

.source-urls-toggle {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.7rem;
  border: 1px solid $light-gray;
  border-radius: $rounded;
  background: $white;
  color: $dark-gray;
  font: inherit;
  gap: 0.4rem;
  cursor: pointer;

  &:hover {
    border-color: $gray;
    color: $off-black;
  }

  strong {
    color: $off-black;
  }

  .caret {
    color: $gray;
    font-size: 0.85em;
    transition: transform 0.15s ease;

    &.open {
      transform: rotate(180deg);
    }
  }
}

.url-panel {
  display: flex;
  flex-wrap: wrap;
  align-self: stretch;
  margin: 0 0 1rem;
  padding: 0.5rem 0.75rem;
  border: 1px solid $light-gray;
  border-radius: $rounded;
  background: $off-white;
  gap: 0.4rem 0.6rem;
}

.url-chip {
  padding: 0.25rem 0.6rem;
  border: 1px solid $light-gray;
  border-radius: 999px;
  background: $white;
  color: $theme;
  font-size: 0.85rem;
  text-decoration: none;
  word-break: break-all;

  &:hover {
    border-color: $theme;
    text-decoration: underline;
  }
}

.browser-section {
  width: 100%;
  margin-top: 3rem;
  padding: 0 40px;

  h3 {
    margin: 0 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid $light-gray;
    color: $off-black;
    font-weight: 600;
    font-size: 1.25rem;
  }

  .section-description {
    margin: 0 0 1.5rem 0;
    color: $dark-gray;
    font-size: 0.95rem;
  }
}
</style>
