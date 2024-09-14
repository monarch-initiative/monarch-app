<!--
  node page overview section. basic, high level information about node.
-->

<template>
  <AppSection design="bare">
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

      <!-- association counts -->
      <AppDetail
        :blank="!node.association_counts.length"
        title="Association Counts"
        :full="true"
      >
        <AppFlex align-h="left" gap="small">
          <AppLink
            v-for="(count, index) in node.association_counts"
            :key="index"
            :to="{ query: { associations: count.category || '' } }"
            @click="scrollToAssociations"
          >
            {{ count.label }} ({{ count.count?.toLocaleString() || 0 }})
          </AppLink>
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
import { scrollTo } from "@/router";
import { sleep } from "@/util/debug";

type Props = {
  /** current node */
  node: Node;
};

const props = defineProps<Props>();

/** separate out mappings into categories */
const clinicalSynopsis = computed(
  () =>
    props.node.mappings?.filter(({ id }) =>
      ["OMIM:", "Orphanet:"].some((prefix) => id.startsWith(prefix)),
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
      ({ id }) =>
        !["OMIM:", "GARD:", "Orphanet:"].some((prefix) =>
          id.startsWith(prefix),
        ),
    ) || [],
);

async function scrollToAssociations() {
  await sleep(100);
  scrollTo("#associations");
}
</script>

<style lang="scss" scoped>
.description {
  width: 100%;
  overflow-x: auto;
  white-space: pre-line;
}
</style>
