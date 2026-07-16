<!--
  search results page

  Nothing but page chrome around TabSearch, which owns the search box, facet
  filters, results and pagination. This page used to be a near-verbatim fork of
  that component; the two drifted, and fixes kept landing in whichever copy the
  author found first.
-->

<template>
  <AppBreadcrumb />
  <PageTitle
    id="page-results"
    title="Search Results Across Genes, Diseases & Phenotypes"
  />
  <TabSearch />
</template>

<script setup lang="ts">
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import TabSearch from "@/components/TabSearch.vue";
import PageTitle from "@/components/ThePageTitle.vue";
</script>
