<!--
  node page details section. more detailed metadata/info about node.
-->

<template>
  <AppSection>
    <AppHeading icon="clipboard-list">Details</AppHeading>

    <AppDetails>
      <!-- inheritance -->
      <AppDetail :blank="!node.inheritance" title="Heritability">
        <AppFlex align-h="left" gap="small">
          <AppLink
            v-tooltip="node.inheritance?.name"
            :to="node.inheritance?.id || ''"
            >{{ node.inheritance?.name }}</AppLink
          >
        </AppFlex>
      </AppDetail>

      <!-- taxon (gene specific)-->
      <AppDetail
        v-if="node.category === 'biolink:Gene'"
        :blank="!node.in_taxon"
        title="Taxon"
      >
        <AppLink v-tooltip="node?.in_taxon" :to="node.in_taxon || ''">{{
          node.in_taxon_label
        }}</AppLink>
      </AppDetail>

      <!-- external references -->
      <AppDetail
        :blank="!node.external_links"
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
    </AppDetails>
  </AppSection>
</template>

<script setup lang="ts">
import type { Node } from "@/api/model";
import AppDetail from "@/components/AppDetail.vue";
import AppDetails from "@/components/AppDetails.vue";

type Props = {
  /** current node */
  node: Node;
};

defineProps<Props>();
</script>
