<template>
  <AppBreadcrumb />

  <PageTitle title="Downloads" id="downloads-page" />
  <AppSection width="big" design="bare">
    <p class="description">
      Here you can find all the available downloads for the knowledge graph. The
      data is available in TSV format, and you can also download the knowledge
      graph in various formats.
    </p>
    <section>
      <h2>Knowledge Graph</h2>
      <DownloadTable :items="knowledgeGraphDownloads" />
    </section>

    <section>
      <h2>Derived Artifacts</h2>
      <DownloadTable :items="derivedArtifacts" />
    </section>

    <section>
      <h2>Simplified TSV Exports</h2>
      <p>
        You can browse all TSV exports directly
        <a :href="tsvIndexLink" target="_blank">here</a>.
      </p>
    </section>
  </AppSection>
</template>

<script setup lang="ts">
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import DownloadTable from "@/components/AppDownloadTable.vue";
import AppSection from "@/components/AppSection.vue";
import PageTitle from "@/components/PageTitle.vue";
import {
  derivedArtifacts,
  knowledgeGraphDownloads,
  tsvIndexLink,
} from "@/data/downloads";
</script>

<style lang="scss" scoped>
.downloads-page {
  padding: 2rem;
}

section {
  width: 100%;
}

h1 {
  margin-bottom: 1rem;
  font-size: 2rem;
}

h2 {
  margin-bottom: 1rem;
  padding-bottom: 0.3rem;
  border-bottom: 1px solid #ccc;
  font-size: 1.4rem;
}
</style>
