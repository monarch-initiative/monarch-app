<template>
  <div>
    <AppBreadcrumb />
    <PageTitle id="association-browser" title="Association Browser" />

    <AppSection width="full" alignment="left">
      <div class="browser-section">
        <p class="section-description">
          Browse and filter all associations in the Monarch Knowledge Graph.
        </p>

        <SourceAssociationBrowser
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
import SourceAssociationBrowser from "@/components/dashboard/SourceAssociationBrowser.vue";
import PageTitle from "@/components/ThePageTitle.vue";
import { useAssociationFilters } from "@/composables/use-source-dashboard";

const {
  filters,
  filterQueries,
  offset,
  limit,
  setFilter,
  clearFilters,
  hasActiveFilters,
} = useAssociationFilters();
</script>

<style lang="scss" scoped>
.browser-section {
  width: 100%;
  padding: 0 40px;

  .section-description {
    margin: 0 0 1.5rem 0;
    color: $gray;
    font-size: 0.95rem;
  }
}
</style>
