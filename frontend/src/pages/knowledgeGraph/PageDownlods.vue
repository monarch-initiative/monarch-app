<template>
  <AppBreadcrumb />

  <PageTitle title="Downloads" id="downloads-page" />
  <AppSection width="big" design="bare">
    <p>
      Here you can find all the available downloads for the knowledge graph. The
      data is available in TSV format, and you can also download the knowledge
      graph in various formats.
    </p>
    <section>
      <h2>Knowledge Graph</h2>
      <DownloadTable :items="knowledgeGraphDownloads" />
    </section>

    <section>
      <h2>Associations</h2>
      <DownloadTable :items="associations" />
    </section>

    <section>
      <h2>Derived Artifacts</h2>
      <DownloadTable :items="derivedArtifacts" />
    </section>
  </AppSection>
</template>

<script setup lang="ts">
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import DownloadTable from "@/components/AppDownloadTable.vue";
import AppSection from "@/components/AppSection.vue";
import PageTitle from "@/components/PageTitle.vue";
import {
  associations,
  derivedArtifacts,
  knowledgeGraphDownloads,
} from "@/data/downloads";
</script>

<style lang="scss" scoped>
section {
  width: 100%;
}

h2 {
  margin-bottom: 1rem;
  font-size: 1.4rem;
}
p {
  text-align: left;
}
</style>
