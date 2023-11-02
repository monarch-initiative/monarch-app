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
import { compareSetToSet } from "@/api/phenotype-explorer";
import ThePhenogrid from "@/components/ThePhenogrid.vue";
import TheSnackbar from "@/components/TheSnackbar.vue";
import { useQuery } from "@/util/composables";
import { sleep } from "@/util/debug";

/** route info */
const route = useRoute();

const aPhenotypes = ref<string[]>([]);
const bPhenotypes = ref<string[]>([]);

/** comparison analysis */
const {
  query: runAnalysis,
  data: comparison,
  isLoading,
  isError,
} = useQuery(
  async function () {
    return await compareSetToSet(aPhenotypes.value, bPhenotypes.value);
  },

  /** default value */
  { summary: [], phenogrid: { cols: [], rows: [], cells: {}, unmatched: [] } },
);

/** re-rerun analysis when inputs change */
watch([aPhenotypes, bPhenotypes], runAnalysis);

/** get input phenotype sets from url params */
watch(
  () => route.query,
  () => {
    const { source = "", target = "" } = route.query;

    if (source && typeof source === "string")
      aPhenotypes.value = source.split(",");
    if (target && typeof target === "string")
      bPhenotypes.value = target.split(",");

    runAnalysis();
  },
  { immediate: true, deep: true },
);

/** get input phenotype sets from parent window message */
useEventListener("message", (event: MessageEvent) => {
  if ("source" in event.data && "target" in event.data) {
    aPhenotypes.value = event.data.source;
    bPhenotypes.value = event.data.target;
  }
});

watch(
  [isLoading, isError, comparison],
  async () => {
    const container = document.body;
    await sleep(10);
    if (!container) return;
    let width = container.scrollWidth + 2;
    let height = container.scrollHeight + 2;
    window.parent.postMessage({ width, height }, "*");
  },
  { immediate: true, deep: true },
);

/** allow consuming parent to link to css stylesheet */
const stylesheet = computed(() =>
  typeof route.query.stylesheet === "string"
    ? window.decodeURIComponent(route.query.stylesheet)
    : "",
);
</script>

<style>
body {
  height: max-content;
}

#app {
  display: contents;
}
</style>
