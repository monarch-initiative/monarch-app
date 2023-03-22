<template>
  <AppSection v-if="node.category === 'disease'">
    <AppHeading icon="chart-bar">Histo-Pheno</AppHeading>
    <HistoPheno :node="node" />
  </AppSection>
</template>

<script setup lang="ts">
import { Node } from "@/api/node-lookup";
import HistoPheno from "./HistoPheno.vue";

// import HistoPheno from "./HistoPheno_NEW.vue";

interface Props {
  /** current node */
  node: Node;
}

defineProps<Props>();
</script>
