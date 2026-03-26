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
import { computed, reactive, ref } from "vue";
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import AppSection from "@/components/AppSection.vue";
import SourceAssociationBrowser from "@/components/dashboard/SourceAssociationBrowser.vue";
import PageTitle from "@/components/ThePageTitle.vue";
import {
  emptyFilters,
  type SourceFilters,
} from "@/composables/use-source-dashboard";

/** shared filter state */
const filters = reactive<SourceFilters>(emptyFilters());

/** pagination state */
const offset = ref(0);
const limit = ref(20);

/** build Solr filter_queries array from active filters */
const filterQueries = computed(() => {
  const fqs: string[] = [];
  if (filters.subjectCategory)
    fqs.push(`subject_category:"${filters.subjectCategory}"`);
  if (filters.objectCategory)
    fqs.push(`object_category:"${filters.objectCategory}"`);
  if (filters.predicate) fqs.push(`predicate:"${filters.predicate}"`);
  if (filters.subjectTaxonLabel)
    fqs.push(`subject_taxon_label:"${filters.subjectTaxonLabel}"`);
  if (filters.objectTaxonLabel)
    fqs.push(`object_taxon_label:"${filters.objectTaxonLabel}"`);
  if (filters.knowledgeLevel)
    fqs.push(`knowledge_level:"${filters.knowledgeLevel}"`);
  if (filters.agentType) fqs.push(`agent_type:"${filters.agentType}"`);
  if (filters.providedBy) fqs.push(`provided_by:"${filters.providedBy}"`);
  if (filters.negated) fqs.push(`negated:${filters.negated}`);
  if (filters.primaryKnowledgeSource)
    fqs.push(`primary_knowledge_source:"${filters.primaryKnowledgeSource}"`);
  return fqs;
});

/** set a single filter value and reset pagination */
const setFilter = (key: keyof SourceFilters, value: string) => {
  filters[key] = value;
  offset.value = 0;
};

/** clear all filters and reset pagination */
const clearFilters = () => {
  Object.assign(filters, emptyFilters());
  offset.value = 0;
};

/** check if any filter is active */
const hasActiveFilters = computed(() =>
  Object.values(filters).some((v) => v !== ""),
);
</script>

<style lang="scss" scoped>
.browser-section {
  width: 100%;
  padding: 0 40px;

  .section-description {
    margin: 0 0 1.5rem 0;
    color: #6b7280;
    font-size: 0.95rem;
  }
}
</style>
