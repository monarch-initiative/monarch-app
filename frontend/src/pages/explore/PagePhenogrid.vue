<!--
  phenogrid on blank page to be used as iframe widget
-->

<template>
  <div ref="container" class="container">
    <link :href="stylesheet" rel="stylesheet" />

    <!-- analysis status -->
    <AppStatus v-if="isLoading" code="loading">Running analysis</AppStatus>
    <AppStatus v-else-if="isError" code="error"
      >Error running analysis</AppStatus
    >
    <AppStatus v-else-if="!comparison.phenogrid.cells.length" code="warning"
      >No results</AppStatus
    >

    <!-- results -->
    <template v-if="comparison.phenogrid.cells.length">
      <ThePhenogrid :data="comparison.phenogrid" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { useEventListener, useResizeObserver } from "@vueuse/core";
import { compareSetToSet } from "@/api/phenotype-explorer";
import ThePhenogrid from "@/components/ThePhenogrid.vue";
import { useQuery } from "@/util/composables";

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
  { summary: [], phenogrid: { cols: [], rows: [], cells: [] } },
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
  },
  { immediate: true, deep: true },
);

/** get input phenotype sets from parent window message */
useEventListener("message", (event: MessageEvent) => {
  if ("source" in event.data) aPhenotypes.value = event.data.source;
  if ("target" in event.data) bPhenotypes.value = event.data.target;
});

/** allow consuming parent to link to css stylesheet */
const stylesheet = computed(() =>
  typeof route.query.stylesheet === "string"
    ? window.decodeURIComponent(route.query.stylesheet)
    : "",
);

const container = ref<HTMLDivElement>();

/** when size of widget changes */
function onResize() {
  const bbox = container.value?.getBoundingClientRect();
  window.parent.postMessage(bbox, "*");
}

useResizeObserver(container, onResize);
</script>

<style lang="scss" scoped>
.container {
  width: max-content;
  height: max-content;
}
</style>
