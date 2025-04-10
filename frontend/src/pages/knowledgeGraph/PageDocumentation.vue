<template>
  <AppBreadcrumb />
  <PageTitle id="kg-about" title="Documentation" />
  <AppSection width="big" design="bare">
    <p>
      The Monarch Initiative Documentation page provides resources on data
      ingestion processes and application usage. It includes guides on
      configuring data ingests and utilizing Monarch's knowledge graph tools.
    </p>
    <ul>
      <li>
        <AppLink
          to="https://monarch-initiative.github.io/monarch-ingest/"
          noIcon="true"
        >
          Monarch Ingest Documentation
        </AppLink>
        : This documentation details the data ingestion process into the Monarch
        Knowledge Graph, including information on data sources, ingestion
        pipelines, and transformation processes
      </li>
      <li>
        <AppLink to="https://monarch-app.monarchinitiative.org/" noIcon="true">
          Monarch Application Guide
        </AppLink>
        : This guide offers instructions on using the Monarch Knowledge Graph
        tools, including installation procedures, usage examples, and
        command-line interface (CLI) commands.
      </li>
    </ul>
  </AppSection>

  <AppSection width="big" design="bare">
    <p>
      For further assistance, check out our
      <AppLink to="/knowledge-graph/help">How to & Help</AppLink>
    </p>
  </AppSection>
</template>
<script setup lang="ts">
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import AppSection from "@/components/AppSection.vue";
import PageTitle from "@/components/PageTitle.vue";
</script>
<style lang="scss" scoped>
.section.center[data-v-d078f057] {
  gap: 1.8em;
}
ul {
  padding-left: 1.2em;
  list-style-type: disc;
}

li {
  margin-bottom: 1em;
}
</style>
