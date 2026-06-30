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

      <!--Temperory condition for diesease node-->
      <AppDetails v-if="isDiseaseNode" gap="20px">
        <SectionClinicalReources
          :frequency-label="frequencyLabel"
          :node="node"
        />
        <!--
          Mondo disease<->X relationships. These enter the KG with a generic
          biolink:related_to predicate but retain the real relation (an RO term)
          in original_predicate; the backend resolves that term's label from the
          KG. Grouped by relation label so the RO term's meaning is revealed.
        -->
        <AppDetail
          v-for="group in relationshipGroups"
          :key="`rel-${group.label}`"
          :title="group.label"
          :full="true"
        >
          <AppFlex align-h="left">
            <AppNodeBadge
              v-for="entity in group.entities"
              :key="entity.id"
              :node="entity"
            />
          </AppFlex>
        </AppDetail>
        <AppDetail
          :blank="!otherMappings.length"
          title="Equivalent disease concepts in other termiologies"
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
          :blank="!externalRefs?.length"
          title="External References"
          :full="true"
        >
          <AppFlex align-h="left" gap="small">
            <AppLink
              v-for="(link, index) of externalRefs"
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

        <AppDetail v-if="nodeVersion" :title="nodeVersionTitle">
          <span>{{ nodeVersion.version || "unknown" }}</span>
        </AppDetail>
      </AppDetails>

      <!--For all other nodes other than diesease nodes-->
      <AppDetails v-else gap="20px">
        <!-- URI -->
        <AppDetail :blank="!node.uri" title="URI">
          <AppLink :to="node.uri || ''">
            {{ node.id }}
          </AppLink>
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
          <span>{{ frequencyLabel }}</span>
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

        <AppDetail v-if="nodeVersion" :title="nodeVersionTitle">
          <span>{{ nodeVersion.version || "unknown" }}</span>
        </AppDetail>

        <!-- Mondo related_to relationships (RO original_predicate), grouped by relation label -->
        <AppDetail
          v-for="group in relationshipGroups"
          :key="`rel-${group.label}`"
          :title="group.label"
          :full="true"
        >
          <AppFlex align-h="left">
            <AppNodeBadge
              v-for="entity in group.entities"
              :key="entity.id"
              :node="entity"
            />
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
    </AppDetails>
  </AppSection>
</template>

<script setup lang="ts">
import { computed } from "vue";
import omit from "lodash/omit";
import type { Entity, Node } from "@/api/model";
import AppDetail from "@/components/AppDetail.vue";
import AppDetails from "@/components/AppDetails.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppNodeText from "@/components/AppNodeText.vue";
import AppTagList from "@/components/AppTagList.vue";
import { useClinicalResources } from "@/composables/use-clinical-resources";
import { useSourceVersions } from "@/composables/use-source-versions";
import SectionClinicalReources from "./SectionClinicalReources.vue";

type Props = { node: Node };

const { node } = defineProps<Props>();
const isDiseaseNode = computed(() => node.category === "biolink:Disease");

/**
 * Group the node's Mondo disease<->gene relationships by their relation label
 * so each RO relation (e.g. "has material basis in germline mutation in")
 * becomes a titled block. Falls back to the relation CURIE if the KG had no
 * label.
 */
const relationshipGroups = computed(() => {
  const groups = new Map<string, { label: string; entities: Entity[] }>();
  for (const rel of node.node_relationships ?? []) {
    if (!rel.related_entity) continue;
    // Prefer the KG-resolved label; fall back to the relation CURIE so distinct
    // unlabeled relations stay distinguishable (same chain for key and title).
    const key = rel.relation_label || rel.relation || "Related to";
    const label = key.charAt(0).toUpperCase() + key.slice(1);
    let group = groups.get(key);
    if (!group) {
      group = { label, entities: [] };
      groups.set(key, group);
    }
    group.entities.push(rel.related_entity);
  }
  return [...groups.values()];
});
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

const frequencyLabel = computed((): "Rare" | "Common" => {
  // subsets may be a true multi-valued array or a single pipe-delimited string;
  // split on "|" to handle both
  const allSubsets = (node.subsets ?? []).flatMap((s) => s.split("|"));
  return allSubsets.includes("rare") ? "Rare" : "Common";
});

const { otherMappings, externalRefs } = useClinicalResources(node);

/**
 * Derive the infores from a node's curie prefix (e.g. MONDO:0007947 →
 * infores:mondo). Lossy for sources whose infores name doesn't match the curie
 * prefix lowercased — those silently fall through to no version.
 */
const { versionForInfores } = useSourceVersions();
const nodeVersion = computed(() => {
  const prefix = node.id?.split(":")[0];
  if (!prefix) return null;
  return versionForInfores(`infores:${prefix.toLowerCase()}`);
});

/**
 * Use the source's own name in the field title (e.g. "Mondo Version") so
 * disease/gene/etc. pages don't say a generic "Source Version".
 */
const nodeVersionTitle = computed(() => {
  const v = nodeVersion.value;
  if (!v) return "Source Version";
  const label = v.name?.trim() || v.infores.replace(/^infores:/, "");
  return `${label} Version`;
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
