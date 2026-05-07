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

      <AppDetail title="Primary Knowledge Source" icon="lightbulb">
        <span>{{ association.primary_knowledge_source }}</span>
      </AppDetail>

      <AppDetail v-if="sourceVersion" title="Source Version" icon="clock">
        <span>
          <span v-if="sourceVersion.primary.name">{{ sourceVersion.primary.name }}</span>
          <span v-else><code>{{ sourceVersion.primary.infores }}</code></span>
          <span v-if="sourceVersion.primary.version"> v{{ sourceVersion.primary.version }}</span>
          <span
            v-if="
              sourceVersion.aggregator &&
              sourceVersion.aggregator.infores !== sourceVersion.primary.infores
            "
          >
            (via {{ sourceVersion.aggregator.name || sourceVersion.aggregator.infores }}
            v{{ sourceVersion.aggregator.version }})
          </span>
          <span v-if="sourceVersion.primary.version_method" class="version-method">
            · {{ sourceVersion.primary.version_method }}
          </span>
        </span>
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
import type { DirectionalAssociation, Node } from "@/api/model";
import AppDetail from "@/components/AppDetail.vue";
import AppDetails from "@/components/AppDetails.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppPredicateBadge from "@/components/AppPredicateBadge.vue";
import { useSourceVersions } from "@/composables/use-source-versions";
import { scrollTo } from "@/router";
import { getAgentTypeMeta } from "@/util/agentType";

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

.version-method {
  color: $gray;
  font-size: 0.9em;
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
</style>
