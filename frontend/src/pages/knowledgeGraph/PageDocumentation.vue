<template>
  <AppBreadcrumb />
  <PageTitle id="kg-about" title="Documentation" />
  <AppSection width="big">
    <p>
      The Monarch Initiative Documentation provides comprehensive resources on
      the Monarch Knowledge Graph, including data sources, the KG build
      pipeline, query tools, and application usage.
    </p>
    <ul>
      <li>
        <AppLink
          to="https://monarch-app.monarchinitiative.org/"
          :no-icon="true"
        >
          Monarch KG Documentation
        </AppLink>
        : The central documentation site covering KG data sources, the build
        process, monarch-py, the API, Neo4j access, and more.
      </li>
      <li>
        <AppLink
          to="https://monarch-app.monarchinitiative.org/docs/Sources/"
          :no-icon="true"
        >
          KG Data Sources
        </AppLink>
        : Detailed documentation of each data source ingested into the Monarch
        Knowledge Graph.
      </li>
      <li>
        <AppLink
          to="https://monarch-app.monarchinitiative.org/docs/KG-Build-Process/kg-build-process/"
          :no-icon="true"
        >
          KG Build Process
        </AppLink>
        : How the knowledge graph is assembled from download through transform,
        merge, and load.
      </li>
      <li>
        <AppLink
          to="https://neo4j.monarchinitiative.org/browser/"
          :no-icon="true"
        >
          Neo4j Browser
        </AppLink>
        : Query the Monarch KG directly using Cypher via the Neo4j browser
        interface.
      </li>
    </ul>
  </AppSection>

  <AppSection width="big">
    <p>
      For further assistance, check out our
      <AppLink to="/kg/help">How to & Help</AppLink>
    </p>
  </AppSection>
</template>
<script setup lang="ts">
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import AppSection from "@/components/AppSection.vue";
import PageTitle from "@/components/ThePageTitle.vue";
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
