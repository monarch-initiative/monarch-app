<!--
  node page details section. more detailed metadata/info about node.
-->

<template>
  <AppSection>
    <AppHeading icon="clipboard-list">Details</AppHeading>

    <AppDetails>
      <!-- main identifier -->
      <!-- <AppDetail :blank="!node.iri" title="IRI">
        <AppLink :to="node.iri">{{ node.iri.split("/").pop() }}</AppLink>
      </AppDetail> -->

      <!-- inheritance -->
      <AppDetail :blank="!node.inheritance" title="Heritability">
        <AppFlex h-align="left" gap="small">
          <AppLink
            v-tooltip="node.inheritance?.name"
            :to="node.inheritance?.id || ''"
            >{{ node.inheritance?.name }}</AppLink
          >
        </AppFlex>
      </AppDetail>

      <!-- modifiers -->
      <!-- <AppDetail :blank="!node.modifiers.length" title="Clinical Modifiers">
        <p>{{ node.modifiers.join("&nbsp; | &nbsp;") }}</p>
      </AppDetail> -->

      <!-- taxon (gene specific)-->
      <AppDetail
        v-if="node.category?.includes('biolink:Gene')"
        :blank="!node.taxon?.id"
        title="Taxon"
      >
        <AppLink v-tooltip="node?.taxon?.id" :to="node.taxon?.id || ''">{{
          node.taxon?.label
        }}</AppLink>
      </AppDetail>

      <!-- external references -->
      <AppDetail :blank="!node.xref" title="External References" :big="true">
        <AppFlex h-align="left" gap="small">
          <AppLink v-for="(xref, index) of node.xref" :key="index" :to="xref">{{
            xref
          }}</AppLink>
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
