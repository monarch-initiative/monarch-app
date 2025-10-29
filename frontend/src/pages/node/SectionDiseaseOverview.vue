<!-- SectionDiseaseOverview.vue -->
<template>
  <AppDetails gap="20px">
    <!-- Clinical resources ( heritability/causal genes/frequency) -->
    <SectionClinicalReources :frequency-label="frequencyLabel" :node="node" />

    <!-- Equivalent concepts (disease) -->
    <AppDetail
      v-if="otherMappings && otherMappings.length"
      title="Equivalent disease concepts in other terminologies"
      :full="true"
    >
      <AppFlex align-h="left" gap="small">
        <AppLink
          v-for="(mapping, index) in otherMappings"
          :key="index"
          :to="mapping.url || ''"
        >
          {{ mapping.id }}
        </AppLink>
      </AppFlex>
    </AppDetail>

    <!-- External references -->
    <AppDetail
      v-if="externalRefs?.length"
      title="External References"
      :full="true"
    >
      <AppFlex align-h="left" gap="small">
        <AppLink
          v-for="(link, index) of node.external_links"
          :key="index"
          :to="link.url || ''"
          >{{ link.id }}</AppLink
        >
      </AppFlex>
    </AppDetail>

    <!-- URI -->
    <AppDetail v-if="node.uri" title="URI">
      <AppLink :to="node.uri || ''">{{ node.id }}</AppLink>
    </AppDetail>

    <!-- Ingest docs -->
    <AppDetail v-if="node.provided_by_link" title="Ingest Documentation">
      <AppLink :to="node.provided_by_link?.url || ''">
        {{ node.provided_by_link?.id || node.provided_by }}
      </AppLink>
    </AppDetail>
  </AppDetails>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { Node } from "@/api/model";
import AppDetail from "@/components/AppDetail.vue";
import AppDetails from "@/components/AppDetails.vue";
import AppFlex from "@/components/AppFlex.vue";
import AppLink from "@/components/AppLink.vue";
import { useClinicalResources } from "@/composables/use-clinical-resources";
import SectionClinicalReources from "./SectionClinicalReources.vue";

const props = defineProps<{ node: Node }>();

// pull mappings/refs specific to this node
const { otherMappings, externalRefs } = useClinicalResources(props.node);

// frequency label lives with the blue block
const frequencyLabel = computed<"Rare" | "Common">(() =>
  props.node.subsets?.includes("rare") ? "Rare" : "Common",
);
</script>
