<!--
  node page overview section. basic, high level information about node.
-->

<template>
  <AppSection width="full" alignment="left">
    <AppDetails gap="20px">
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
        >
          <AppNodeText :text="node.description?.trim()" />
        </p>
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

      <!-- disease frequecy -->
      <AppDetail v-if="node.category === 'biolink:Disease'" title="Frequency">
        <span>{{ node?.subsets?.includes("rare") ? "Rare" : "Common" }}</span>
      </AppDetail>

      <!-- synonyms -->
      <AppDetail
        :blank="!node.synonym?.length"
        title="Also Known As"
        :full="true"
      >
        <AppTagList :tags="node.synonym ?? []" />
      </AppDetail>

      <!-- URI -->
      <AppDetail :blank="!node.uri" title="URI">
        <AppLink :to="node.uri || ''">
          {{ node.id }}
        </AppLink>
      </AppDetail>

      <!-- mappings -->
      <AppDetail :blank="!clinicalSynopsis.length" title="Clinical Synopsis">
        <AppFlex align-h="left" gap="small">
          <AppLink
            v-for="(mapping, index) in clinicalSynopsis"
            :key="index"
            :to="mapping.url || ''"
          >
            {{ mapping.id }}
          </AppLink>
        </AppFlex>
      </AppDetail>
      <AppDetail
        :blank="!infoForPatients.length"
        title="Clinical Info for Patients"
      >
        <AppFlex align-h="left" gap="small">
          <AppLink
            v-for="(mapping, index) in infoForPatients"
            :key="index"
            :to="mapping.url || ''"
          >
            {{ mapping.id }}
          </AppLink>
        </AppFlex>
      </AppDetail>
      <AppDetail :blank="!node.provided_by_link" title="Ingest Documentation">
        <AppLink :to="node.provided_by_link?.url || ''">
          {{ node.provided_by_link?.id || node.provided_by }}
        </AppLink>
      </AppDetail>
      <AppDetail
        :blank="!otherMappings.length"
        title="Other Mappings"
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
      <!-- external references -->
      <AppDetail
        :blank="!node.external_links?.length"
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
import { computed } from "vue";
import { omit } from "lodash";
import type { Node } from "@/api/model";
import AppDetail from "@/components/AppDetail.vue";
import AppDetails from "@/components/AppDetails.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppNodeText from "@/components/AppNodeText.vue";
import AppTagList from "@/components/AppTagList.vue";

// import { scrollTo } from "@/router";
// import { sleep } from "@/util/debug";

type Props = {
  /** current node */
  node: Node;
};

const props = defineProps<Props>();

/** separate out mappings into categories */
const clinicalSynopsis = computed(
  () =>
    props.node.mappings?.filter(({ id }) =>
      ["OMIM:"].some((prefix) => id.startsWith(prefix)),
    ) || [],
);
const infoForPatients = computed(
  () =>
    props.node.external_links?.filter(({ id }) =>
      ["GARD:"].some((prefix) => id.startsWith(prefix)),
    ) || [],
);
const otherMappings = computed(
  () =>
    props.node.mappings?.filter(
      ({ id }) => !["OMIM:", "GARD:"].some((prefix) => id.startsWith(prefix)),
    ) || [],
);

// async function scrollToAssociations() {
//   await sleep(100);
//   scrollTo("#associations");
// }
</script>

<style lang="scss" scoped>
.description {
  width: 100%;
  overflow-x: auto;
  white-space: pre-line;
}
</style>
