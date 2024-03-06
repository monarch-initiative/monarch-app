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
import { every, isEmpty } from "lodash";
import { useEventListener } from "@vueuse/core";
import { compareSetToSets } from "@/api/phenotype-explorer";
import ThePhenogrid from "@/components/ThePhenogrid.vue";
import TheSnackbar from "@/components/TheSnackbar.vue";
import { useQuery } from "@/util/composables";

/** route info */
const route = useRoute();

const aPhenotypes = ref<string[]>([]);
// const bPhenotypes = ref<Group>("Human Diseases");
const bPhenotypes = ref<string[][]>([]);
const bLabels = ref<string[]>([]);

/** comparison analysis */
const {
  query: runAnalysis,
  data: comparison,
  isLoading,
  isError,
} = useQuery(
  async function () {
    return await compareSetToSets(
      aPhenotypes.value,
      bPhenotypes.value,
      bLabels.value,
    );
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
    const { source = "", target = "", target_label = "" } = route.query;
    if (source && typeof source === "string")
      aPhenotypes.value = source.split(",");
    if (target && typeof target === "string")
      bPhenotypes.value = [target.split(",")];
    else if (
      Array.isArray(target) &&
      every(target, (t) => typeof t === "string")
    ) {
      bPhenotypes.value = target.map((t) => t?.split(",")) as string[][];
    }
    // read labels as target_label[] from url params
    if (target_label && typeof target_label === "string") {
      bLabels.value = target_label.split(",");
    } else if (
      Array.isArray(target_label) &&
      every(target_label, (t) => typeof t === "string")
    ) {
      bLabels.value = target_label as string[];
    }

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
