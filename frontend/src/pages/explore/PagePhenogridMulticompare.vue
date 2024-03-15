<!--
  phenogrid on blank page to be used as iframe widget
-->

<template>
  <TheSnackbar />
  <link :href="stylesheet" rel="stylesheet" />

  <!-- analysis status -->
  <AppStatus v-if="isLoading" code="loading">Running analysis</AppStatus>
  <AppStatus v-else-if="isError" code="error">Error running analysis</AppStatus>
  <AppStatus v-else-if="isEmpty(comparison.phenogrid.cells)" code="warning"
    >No results</AppStatus
  >

  <!-- results -->
  <template v-else>
    <ThePhenogrid :data="comparison.phenogrid" />
  </template>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { isEmpty } from "lodash";
import { useEventListener } from "@vueuse/core";
import { compareSetToSets } from "@/api/phenotype-explorer";
import ThePhenogrid from "@/components/ThePhenogrid.vue";
import TheSnackbar from "@/components/TheSnackbar.vue";
import { useQuery } from "@/composables/use-query";

/** route info */
const route = useRoute();

const aPhenotypes = ref<Parameters<typeof compareSetToSets>[0]>([]);
const bPhenotypes = ref<Parameters<typeof compareSetToSets>[1]>([]);

/** comparison analysis */
const {
  query: runAnalysis,
  data: comparison,
  isLoading,
  isError,
} = useQuery(
  async function () {
    return await compareSetToSets(aPhenotypes.value, bPhenotypes.value);
  },

  /** default value */
  { phenogrid: { cols: [], rows: [], cells: {}, unmatched: [] } },
);

/** re-rerun analysis when inputs change */
watch([aPhenotypes, bPhenotypes], runAnalysis);

/** get input phenotype sets from url params */
watch(
  () => route.query,
  () => {
    let { subjects = "", "object-sets": objectSets = "" } = route.query;
    const flatObjectSets = [objectSets].flat();

    if (subjects && typeof subjects === "string")
      aPhenotypes.value = subjects.split(",");
    if (objectSets)
      bPhenotypes.value = flatObjectSets.filter(Boolean).map((object) => ({
        phenotypes: object?.split(",") || [],
      }));

    runAnalysis();
  },
  { immediate: true, deep: true },
);

/** get input phenotype sets from parent window message */
useEventListener("message", (event: MessageEvent) => {
  if ("subjects" in event.data && "object-sets" in event.data) {
    aPhenotypes.value = event.data.subjects;
    bPhenotypes.value = event.data["object-sets"];
  }
});

/** allow consuming parent to link to css stylesheet */
const stylesheet = computed(() =>
  typeof route.query.stylesheet === "string"
    ? window.decodeURIComponent(route.query.stylesheet)
    : "",
);
</script>

<style scoped>
:global(html),
:global(body) {
  width: 100%;
  height: 100%;
}

:global(#app) {
  display: contents;
}
</style>
