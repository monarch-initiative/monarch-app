<!-- 
  list of sections for special visualizations.
-->

<template>
  <AppSection v-if="node.category === 'biolink:Disease'">
    <AppHeading icon="chart-bar">HistoPheno</AppHeading>
    <HistoPheno :node="node" />
  </AppSection>
</template>

<script setup lang="ts">
import type { Node } from "@/api/model";
import HistoPheno from "./HistoPheno.vue";

type Props = {
  /** current node */
  node: Node;
};

defineProps<Props>();
</script>
