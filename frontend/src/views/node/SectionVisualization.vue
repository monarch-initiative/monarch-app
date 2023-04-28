<template>
  <!-- <AppSection v-if="node.category === 'disease'"> -->
  <AppSection>
    <AppHeading icon="chart-bar">HistoPheno</AppHeading>
    <HistoPheno :node="node" />
  </AppSection>
</template>

<script setup lang="ts">
import { Node } from "@/api/model";
import HistoPheno from "./HistoPheno.vue";

interface Props {
  /** current node */
  node: Node;
}

defineProps<Props>();
</script>
