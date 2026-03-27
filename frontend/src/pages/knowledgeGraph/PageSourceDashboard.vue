<template>
  <div class="source-dashboard">
    <AppBreadcrumb />
    <PageTitle id="source-dashboard" :title="sourceName" />

    <AppSection width="big">
      <!-- Source header info -->
      <div class="source-header">
        <p class="source-id">
          <strong>Infores ID:</strong>
          <a
            :href="`https://w3id.org/information-resource-registry/${inforesId.replace('infores:', '')}`"
            target="_blank"
            rel="noopener"
          >
            {{ inforesId }}
          </a>
        </p>
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
import { useSourceDashboard } from "@/composables/use-source-dashboard";

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
  margin-bottom: 2rem;
  padding: 1rem 1.5rem;
  border-left: 4px solid $theme;
  border-radius: 0 $rounded $rounded 0;
  background: $theme-light;

  .source-id {
    margin: 0;
    color: $off-black;
    font-size: 0.95rem;

    a {
      color: $theme;

      &:hover {
        text-decoration: underline;
      }
    }
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
