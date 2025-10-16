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
      <AppDetail v-if="node.description" title="Description" :full="true">
        <p
          v-tooltip="'Click to expand'"
          class="description truncate-10"
          tabindex="0"
        >
          <AppNodeText :text="node.description?.trim()" />
        </p>
      </AppDetail>

      <!-- synonyms -->
      <AppDetail
        v-if="node.synonym?.length"
        title="Also Known As"
        :full="true"
        :direction="'row'"
      >
        <AppTagList :tags="node.synonym ?? []" />
      </AppDetail>

      <SectionDiseaseOverview v-if="isDiseaseNode" :node="node" />
      <!--For all other nodes other than diesease nodes-->
      <AppDetails v-else gap="20px">
        <AppDetail
          v-if="otherMappings.length && !isPhenotypeNode"
          :title="`Equivalent ${categoryLabel} concepts in other terminologies`"
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
          v-if="node.external_links?.length"
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
          <AppLink :to="node.uri || ''">
            {{ node.id }}
          </AppLink>
        </AppDetail>

        <!-- mappings -->
        <AppDetail v-if="clinicalSynopsis.length" title="Clinical Synopsis">
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
          v-if="infoForPatients.length"
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

        <AppDetail v-if="node.provided_by_link" title="Ingest Documentation">
          <AppLink :to="node.provided_by_link?.url || ''">
            {{ node.provided_by_link?.id || node.provided_by }}
          </AppLink>
        </AppDetail>
      </AppDetails>
    </AppDetails>
  </AppSection>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { Node } from "@/api/model";
import AppDetail from "@/components/AppDetail.vue";
import AppDetails from "@/components/AppDetails.vue";
import AppNodeText from "@/components/AppNodeText.vue";
import AppTagList from "@/components/AppTagList.vue";
import { useClinicalResources } from "@/composables/use-clinical-resources";
import SectionDiseaseOverview from "./SectionDiseaseOverview.vue";

type Props = { node: Node };

const { node } = defineProps<Props>();
const isDiseaseNode = computed(() => node.category === "biolink:Disease");
const isPhenotypeNode = computed(
  () => node.category === "biolink:PhenotypicFeature",
);

const { otherMappings } = useClinicalResources(node);
const CATEGORY_MAP: Record<string, string> = {
  "biolink:Disease": "disease",
  "biolink:PhenotypicFeature": "phenotype",
};
/** separate out mappings into categories */
const clinicalSynopsis = computed(
  () =>
    node.mappings?.filter(({ id }) =>
      ["OMIM:"].some((prefix) => id.startsWith(prefix)),
    ) || [],
);
const infoForPatients = computed(
  () =>
    node.external_links?.filter(({ id }) =>
      ["GARD:"].some((prefix) => id.startsWith(prefix)),
    ) || [],
);

const categoryLabel = computed(
  () => CATEGORY_MAP[node?.category ?? ""] ?? node?.category ?? "",
);
</script>

<style lang="scss" scoped>
.description {
  width: 100%;
  overflow-x: auto;
  white-space: pre-line;
}
</style>
