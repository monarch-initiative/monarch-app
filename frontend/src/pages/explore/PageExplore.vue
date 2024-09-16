<!--
  explore landing page
-->

<template>
  <AppSection>
    <AppHeading>Explore</AppHeading>
    <AppTabs v-model="tab" name="Explore Mode" :tabs="tabs" />
  </AppSection>
  <TabSearch v-if="tab === 'search'" />
  <TabTextAnnotator v-if="tab === 'text-annotator'" />
  <TabPhenotypeExplorer v-if="tab === 'phenotype-explorer'" />
  <TabMetadata v-if="tab === 'resources'" />
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { useRoute } from "vue-router";
import { startCase } from "lodash";
import AppTabs from "@/components/AppTabs.vue";
import { appTitle } from "@/global/meta";
import TabMetadata from "./TabMetadata.vue";
import TabPhenotypeExplorer from "./TabPhenotypeExplorer.vue";
import tabs from "./tabs.json";
import TabSearch from "./TabSearch.vue";
import TabTextAnnotator from "./TabTextAnnotator.vue";

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
  { immediate: true, flush: "post" },
);
</script>
