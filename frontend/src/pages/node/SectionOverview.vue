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

      <!-- synonyms -->
      <AppDetail
        :blank="!node.synonym?.length"
        title="Also Known As"
        :full="true"
        :direction="'row'"
      >
        <AppTagList :tags="node.synonym ?? []" />
      </AppDetail>

      <!-- clinical resources -->
      <SectionClinicalReources
        :clinicalSynopsis="clinicalSynopsis"
        :infoForPatients="infoForPatients"
        :nodeInheritance="node.inheritance"
        :casualGenes="node.causal_gene"
        :frequencyLabel="frequencyLabel"
        :node="node"
      />

      <AppDetail
        :blank="!otherMappings.length"
        title="Equivalent disease concepts in other termiologies :"
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
      {{ node.external_links }}
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

      <AppDetail :blank="!node.uri" title="URI">
        <AppLink :to="node.uri || ''">
          {{ node.id }}
        </AppLink>
      </AppDetail>

      <AppDetail :blank="!node.provided_by_link" title="Ingest Documentation">
        <AppLink :to="node.provided_by_link?.url || ''">
          {{ node.provided_by_link?.id || node.provided_by }}
        </AppLink>
      </AppDetail>
    </AppDetails>
  </AppSection>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { omit } from "lodash";
import { faCaretSquareLeft } from "@fortawesome/free-regular-svg-icons";
import type { ExpandedCurie, Node } from "@/api/model";
import AppDetail from "@/components/AppDetail.vue";
import AppDetails from "@/components/AppDetails.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppNodeText from "@/components/AppNodeText.vue";
import AppTagList from "@/components/AppTagList.vue";
import SectionClinicalReources from "./SectionClinicalReources.vue";

type Props = {
  /** current node */
  node: Node;
};

const props = defineProps<Props>();

// The prefixes and their icon filenames
const RESOURCE_DEFS = [
  { prefix: "OMIM:", key: "omim", icon: "omim.png" },
  { prefix: "NORD:", key: "nord", icon: "nord.png" },
  { prefix: "GARD:", key: "gard", icon: "gard.png" },
  { prefix: "Orphanet:", key: "orphanet", icon: "orphanet.png" },
  { prefix: "MEDGEN:", key: "medgen", icon: "medgen.png" },
] as const;

type ResourceEntry = {
  id: string;
  url: string;
  icon: string;
  source: "external" | "mapping";
};

// Compute all five entries, in order, if they exist:
const clinicalResources = computed<ResourceEntry[]>(() => {
  const out: ResourceEntry[] = [];

  for (const { prefix, icon } of RESOURCE_DEFS) {
    // 1) try external_links
    const ext = props.node.external_links?.find((l: ExpandedCurie) =>
      l.id.startsWith(prefix),
    );
    if (ext) {
      out.push({
        id: ext.id,
        url: ext.url || "",
        icon,
        source: "external",
      });
      continue;
    }

    // 2) fallback to mappings
    const map = props.node.mappings?.find((m: ExpandedCurie) =>
      m.id.startsWith(prefix),
    );
    if (map) {
      out.push({
        id: map.id,
        url: map.url || "",
        icon,
        source: "mapping",
      });
    }
  }

  return out;
});

console.log("clinicalResources", clinicalResources);
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

const frequencyLabel = computed((): "Rare" | "Common" => {
  return props.node.subsets?.includes("rare") ? "Rare" : "Common";
});
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
