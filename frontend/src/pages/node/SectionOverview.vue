<!--
  node page overview section. basic, high level information about node.
-->

<template>
  <AppSection>
    <AppHeading icon="lightbulb">Overview</AppHeading>

    <AppDetails>
      <!-- symbol (gene specific) -->
      <AppDetail
        v-if="node.category === 'biolink:Gene'"
        :blank="!node.full_name"
        title="Name"
      >
        <p>{{ node.full_name }}</p>
      </AppDetail>

      <!-- taxon (gene specific)-->
      <AppDetail
        v-if="node.category === 'biolink:Gene'"
        :blank="!node.in_taxon_label"
        title="Taxon"
      >
        <AppLink v-tooltip="node?.in_taxon_label" :to="node.in_taxon || ''">{{
          node.in_taxon_label
        }}</AppLink>
      </AppDetail>

      <!-- paragraph description -->
      <AppDetail :blank="!node.description" title="Description" :full="true">
        <p
          v-tooltip="'Click to expand'"
          class="description truncate-10"
          tabindex="0"
          v-html="node.description?.trim()"
        ></p>
      </AppDetail>

      <!-- inheritance -->
      <AppDetail
        v-if="node.category === 'biolink:Disease'"
        :blank="!node.inheritance"
        title="Heritability"
      >
        <AppFlex align-h="left" gap="small">
          <AppLink
            v-tooltip="node.inheritance?.name"
            :to="node.inheritance?.id || ''"
            >{{ node.inheritance?.name }}</AppLink
          >
        </AppFlex>
      </AppDetail>

      <!-- disease causal genes -->
      <AppDetail
        v-if="node.category === 'biolink:Disease'"
        :blank="!node.causal_gene?.length"
        title="Causal Genes"
      >
        <AppFlex align-h="left">
          <AppNodeBadge
            v-for="(gene, index) in node.causal_gene"
            :key="index"
            :node="omit(gene, 'in_taxon_label')"
          />
        </AppFlex>
      </AppDetail>

      <!-- synonyms -->
      <AppDetail
        :blank="!node.synonym?.length"
        title="Also Known As"
        :full="true"
      >
        <p
          class="truncate-2"
          tabindex="0"
          v-html="node.synonym?.join(',\n&nbsp;')"
        ></p>
      </AppDetail>

      <!-- association counts -->
      <AppDetail
        :blank="!node.association_counts.length"
        title="Association Counts"
        :full="true"
      >
        <AppFlex align-h="left">
          <AppLink
            v-for="(count, index) in node.association_counts"
            :key="index"
            :to="{ query: { associations: count.category || '' } }"
          >
            {{ count.label }} {{ count.count?.toLocaleString() || 0 }}
          </AppLink>
        </AppFlex>
      </AppDetail>
    </AppDetails>
  </AppSection>
</template>

<script setup lang="ts">
import { omit } from "lodash";
import type { Node } from "@/api/model";
import AppDetail from "@/components/AppDetail.vue";
import AppDetails from "@/components/AppDetails.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";

type Props = {
  /** current node */
  node: Node;
};

defineProps<Props>();
</script>

<style lang="scss" scoped>
.description {
  width: 100%;
  overflow-x: auto;
  white-space: pre-line;
}
</style>
