<!--
  explore landing page
-->

<template>
  <AppSection>
    <AppHeading>Explore</AppHeading>

    <AppTabs v-model="tab" name="Explore Mode" :tabs="tabs" />
  </AppSection>

  <NodeSearch v-if="tab === 'node-search'" />

  <TextAnnotator v-if="tab === 'text-annotator'" />

  <PhenotypeExplorer v-if="tab === 'phenotype-explorer'" />
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { useRoute } from "vue-router";
import { startCase } from "lodash";
import AppTabs from "@/components/AppTabs.vue";
import { appTitle } from "@/global/meta";
import NodeSearch from "./NodeSearch.vue";
import PhenotypeExplorer from "./PhenotypeExplorer.vue";
import tabs from "./tabs.json";
import TextAnnotator from "./TextAnnotator.vue";

/** route info */
const route = useRoute();

/** selected tab */
const tab = ref(tabs[0].id);

/** update document title */
watch(
  () => route.fullPath,
  () => {
    if (route.hash) appTitle.value = [startCase(route.hash)];
  },
  { immediate: true, flush: "post" }
);
</script>
