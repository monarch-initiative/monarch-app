<!--
  node page association details section, viewer for supporting evidence of an 
  association
-->

<template>
  <AppSection v-if="association">
    <h2>Association Details</h2>

    <div>
      <div class="selected">
        <AppNodeBadge
          :node="{
            id: association.subject,
            name: association.subject_label,
            category: association.subject_category,
            info: association.subject_taxon_label,
          }"
        />
        <AppPredicateBadge :association="association" />
        <AppNodeBadge
          :node="{
            id: association.object,
            name: association.object_label,
            category: association.object_category,
            info: association.object_taxon_label,
          }"
        />
      </div>
    </div>

    <AppDetails>
      <AppDetail title="Evidence Codes" icon="flask" :full="true">
        <AppFlex gap="small" align-h="left">
          <AppLink
            v-for="(source, index) in association.has_evidence_links"
            :key="index"
            :to="source.url || ''"
            >{{ source.id }}</AppLink
          >
        </AppFlex>
      </AppDetail>

      <AppDetail v-if="agentMeta" title="Agent Type" :icon="agentMeta.icon">
        <span>{{ agentMeta.label }}</span>
        <span class="agent-description">
          &mdash; {{ agentMeta.description }}
        </span>
      </AppDetail>

      <AppDetail
        v-if="association.knowledge_level"
        title="Knowledge Level"
        icon="scale-balanced"
      >
        <span>{{ startCase(association.knowledge_level) }}</span>
      </AppDetail>

      <AppDetail title="Primary Knowledge Source" icon="lightbulb">
        <span>{{ association.primary_knowledge_source }}</span>
      </AppDetail>

      <AppDetail v-if="sourceVersion" title="Source Version" icon="clock">
        <span>
          <span v-if="sourceVersion.primary.name">{{
            sourceVersion.primary.name
          }}</span>
          <span v-else
            ><code>{{ sourceVersion.primary.infores }}</code></span
          >
          <span v-if="sourceVersion.primary.version">
            v{{ sourceVersion.primary.version }}</span
          >
          <span
            v-if="
              sourceVersion.aggregator &&
              sourceVersion.aggregator.infores !== sourceVersion.primary.infores
            "
          >
            (via
            {{
              sourceVersion.aggregator.name || sourceVersion.aggregator.infores
            }}<template v-if="sourceVersion.aggregator.version">
              v{{ sourceVersion.aggregator.version }}</template
            >)
          </span>
        </span>
      </AppDetail>

      <AppDetail
        v-if="retrievalSources.length"
        title="Provenance"
        icon="sitemap"
        :full="true"
      >
        <AppFlex direction="col" gap="small" align-h="left">
          <div
            v-for="(source, index) in retrievalSources"
            :key="index"
            class="retrieval-source"
          >
            <span class="role">{{ formatRole(source.resource_role) }}:</span>
            <code>{{ source.resource_id }}</code>
            <span v-if="source.upstream_resource_ids?.length" class="upstream">
              &larr; {{ source.upstream_resource_ids.join(", ") }}
            </span>
          </div>
        </AppFlex>
      </AppDetail>

      <AppDetail
        v-if="association.aggregator_knowledge_source?.length"
        title="Aggregator Knowledge Source"
        icon="database"
        :full="true"
      >
        <AppFlex gap="small" align-h="left">
          <code
            v-for="(agg, index) in association.aggregator_knowledge_source"
            :key="index"
            >{{ agg }}</code
          >
        </AppFlex>
      </AppDetail>

      <AppDetail title="Provided By" icon="notes-medical">
        <AppLink :to="association.provided_by_link?.url || ''" :replace="true">
          {{ association.provided_by_link?.id || association.provided_by }}
        </AppLink>
      </AppDetail>

      <AppDetail title="Publications" icon="book" :full="true">
        <AppFlex gap="small" align-h="left">
          <AppLink
            v-for="(publication, index) of association.publications_links"
            :key="index"
            :to="publication.url || ''"
          >
            {{ publication.id }}
          </AppLink>
        </AppFlex>
      </AppDetail>

      <AppDetail
        v-if="association.original_predicate"
        title="Original Predicate"
        icon="code"
      >
        <code>{{ association.original_predicate }}</code>
      </AppDetail>

      <AppDetail
        v-if="qualifierRows.length"
        title="Qualifiers"
        icon="clipboard-list"
        :full="true"
      >
        <AppFlex direction="col" gap="small" align-h="left">
          <div v-for="(qualifier, index) in qualifierRows" :key="index">
            <strong>{{ qualifier.label }}:</strong> {{ qualifier.value }}
          </div>
        </AppFlex>
      </AppDetail>

      <AppDetail
        v-if="hasFrequencyData"
        title="Frequency Data"
        icon="equals"
        :full="true"
      >
        <AppFlex direction="col" gap="small" align-h="left">
          <div v-if="association.has_count != null">
            <strong>Count:</strong> {{ association.has_count }}
          </div>
          <div v-if="association.has_total != null">
            <strong>Total:</strong> {{ association.has_total }}
          </div>
          <div v-if="association.has_percentage != null">
            <strong>Percentage:</strong> {{ association.has_percentage }}
          </div>
          <div v-if="association.has_quotient != null">
            <strong>Quotient:</strong> {{ association.has_quotient }}
          </div>
        </AppFlex>
      </AppDetail>

      <AppDetail
        v-if="association.FDA_adverse_event_level"
        title="FDA Adverse Event Level"
        icon="circle-exclamation"
      >
        <span>{{ association.FDA_adverse_event_level }}</span>
      </AppDetail>

      <AppDetail v-if="association.negated" title="Negated" icon="circle-xmark">
        <span>Yes</span>
      </AppDetail>

      <AppDetail
        v-if="association.supporting_text?.length"
        icon="quote-left"
        title="Supporting Text"
        :full="true"
      >
        <AppFlex direction="col" gap="small" align-h="left">
          <blockquote
            v-for="(text, index) in association.supporting_text"
            :key="index"
            class="supporting-text"
          >
            {{ text }}
          </blockquote>
        </AppFlex>
      </AppDetail>
    </AppDetails>
  </AppSection>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from "vue";
import { startCase } from "lodash";
import type { DirectionalAssociation, Node } from "@/api/model";
import AppDetail from "@/components/AppDetail.vue";
import AppDetails from "@/components/AppDetails.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppPredicateBadge from "@/components/AppPredicateBadge.vue";
import { useSourceVersions } from "@/composables/use-source-versions";
import { scrollTo } from "@/router";
import { getAgentTypeMeta } from "@/util/agentType";
import { parseRetrievalSources } from "@/util/retrievalSources";

type Props = {
  /** current node */
  node: Node;
  /** selected association */
  association: DirectionalAssociation | null;
};

const props = defineProps<Props>();

const agentMeta = computed(() =>
  props.association?.agent_type
    ? getAgentTypeMeta(props.association.agent_type)
    : null,
);

const { versionForEdge } = useSourceVersions();
const sourceVersion = computed(() =>
  props.association ? versionForEdge(props.association) : null,
);

/** parse the nested retrieval-source provenance chain (JSON-encoded) */
const retrievalSources = computed(() =>
  parseRetrievalSources(props.association?.sources),
);

/** humanize a retrieval-source role, e.g. "primary_knowledge_source" */
const formatRole = (role?: string) => (role ? startCase(role) : "Source");

/** present qualifier values, preferring labels over raw ids */
const qualifierRows = computed(() => {
  const a = props.association;
  const rows: { label: string; value: string }[] = [];
  if (!a) return rows;
  const add = (label: string, value?: string | null) => {
    if (value) rows.push({ label, value });
  };
  add("Frequency", a.frequency_qualifier_label || a.frequency_qualifier);
  add("Onset", a.onset_qualifier_label || a.onset_qualifier);
  add("Sex", a.sex_qualifier_label || a.sex_qualifier);
  add("Stage", a.stage_qualifier_label || a.stage_qualifier);
  add(
    "Disease context",
    a.disease_context_qualifier_label || a.disease_context_qualifier,
  );
  add("Object specialization", a.object_specialization_qualifier);
  (a.qualifiers ?? []).forEach((qualifier) => add("Qualifier", qualifier));
  return rows;
});

/** whether any frequency/count representation is present */
const hasFrequencyData = computed(() => {
  const a = props.association;
  return (
    a != null &&
    (a.has_count != null ||
      a.has_total != null ||
      a.has_percentage != null ||
      a.has_quotient != null)
  );
});

/** scroll details section into view */
async function scrollIntoView() {
  scrollTo("#association-details");
}

watch(() => props.association, scrollIntoView);
onMounted(scrollIntoView);
</script>

<style lang="scss" scoped>
.selected {
  display: flex;
  margin-top: 10px;
  padding: 10px;
  gap: 10px 20px;
}

@media (max-width: 600px) {
  .selected {
    flex-direction: column;
  }
}

.arrow {
  color: $gray;
}

.supporting-text {
  margin: 0;
  padding: 0.5em 0 0.5em 1em;
  border-left: 3px solid $light-gray;
  font-style: italic;
}

.agent-description {
  color: $gray;
  font-size: 0.9em;
}

.retrieval-source {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0 0.5em;
}

.retrieval-source .role {
  color: $gray;
}

.retrieval-source .upstream {
  color: $gray;
}
</style>
