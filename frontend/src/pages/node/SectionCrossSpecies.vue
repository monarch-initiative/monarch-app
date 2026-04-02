<!--
  Cross-species term clique visualization section.
  Shows the cross-species parent term and its species-specific children
  with their associations (subclass_of, same_as, homologous_to).
  Only rendered when the node has a clique with 1+ species-specific entities.
-->

<template>
  <AppSection v-if="showSection" width="full" class="inset" alignment="left">
    <AppHeading icon="sitemap">Cross-Species Equivalents</AppHeading>
    <TheCrossSpeciesGraph
      :clique="node.cross_species_term_clique!"
      :current-id="node.id"
    />
  </AppSection>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { Node } from "@/api/model";
import TheCrossSpeciesGraph from "@/components/TheCrossSpeciesGraph.vue";

type Props = {
  node: Node;
};

const props = defineProps<Props>();

const showSection = computed(() => {
  const clique = props.node.cross_species_term_clique;
  return clique && clique.clique_entities.length >= 1;
});
</script>
