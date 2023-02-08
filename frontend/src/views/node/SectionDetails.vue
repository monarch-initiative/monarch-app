<!--
  node page details section. more detailed metadata/info about node.
-->

<template>
  <AppSection>
    <AppHeading icon="clipboard-list">Details</AppHeading>

    <AppDetails>
      <!-- main identifier -->
      <AppDetail :blank="!node.iri" title="IRI">
        <AppLink :to="node.iri">{{ node.iri.split("/").pop() }}</AppLink>
      </AppDetail>

      <!-- inheritance -->
      <AppDetail :blank="!node.inheritance.length" title="Heritability">
        <AppFlex h-align="left" gap="small">
          <AppLink
            v-for="(inheritance, index) of node.inheritance"
            :key="index"
            v-tooltip="inheritance.id"
            :to="inheritance.link"
            >{{ inheritance.name }}</AppLink
          >
        </AppFlex>
      </AppDetail>

      <!-- modifiers -->
      <AppDetail :blank="!node.modifiers.length" title="Clinical Modifiers">
        <p>{{ node.modifiers.join("&nbsp; | &nbsp;") }}</p>
      </AppDetail>

      <!-- taxon (gene specific)-->
      <AppDetail
        v-if="node.category === 'gene'"
        :blank="!node.taxon?.id"
        title="Taxon"
      >
        <AppLink v-tooltip="node?.taxon?.id" :to="node.taxon?.link || ''">{{
          node.taxon?.name
        }}</AppLink>
      </AppDetail>

      <!-- external references -->
      <AppDetail
        :blank="!node.xrefs.length"
        title="External References"
        :big="true"
      >
        <AppFlex h-align="left" gap="small">
          <AppLink
            v-for="(xref, index) of node.xrefs"
            :key="index"
            :to="xref.link"
            >{{ xref.id }}</AppLink
          >
        </AppFlex>
      </AppDetail>
    </AppDetails>
  </AppSection>
</template>

<script setup lang="ts">
import { Node } from "@/api/node-lookup";
import AppDetail from "@/components/AppDetail.vue";
import AppDetails from "@/components/AppDetails.vue";

interface Props {
  /** current node */
  node: Node;
}

defineProps<Props>();
</script>
