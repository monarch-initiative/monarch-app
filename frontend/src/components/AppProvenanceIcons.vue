<!--
  agent type and knowledge level markers for one or more associations, with
  the same icons and tooltips as the association tables
-->

<template>
  <span class="provenance">
    <span
      v-for="meta in agentMetas"
      :key="meta.label"
      v-tooltip="`<b>${meta.label}</b><br>${meta.description}`"
      :class="['marker', { labelled: showLabels, machine: meta.machine }]"
      :aria-label="`${meta.label}: ${meta.description}`"
    >
      <AppIcon :icon="meta.icon" />
      <span v-if="showLabels">{{ meta.label }}</span>
    </span>
    <span
      v-for="meta in levelMetas"
      :key="meta.label"
      v-tooltip="`<b>${meta.label}</b><br>${meta.description}`"
      :class="['marker', { labelled: showLabels }]"
      :aria-label="`${meta.label}: ${meta.description}`"
    >
      <AppIcon :icon="meta.icon" />
      <span v-if="showLabels">{{ meta.label }}</span>
    </span>
  </span>
</template>

<script setup lang="ts">
import { computed } from "vue";
import AppIcon from "@/components/AppIcon.vue";
import { getAgentTypeMeta } from "@/util/agentType";
import { getKnowledgeLevelMeta } from "@/util/knowledgeLevel";

type Props = {
  /** agent_type values, e.g. text_mining_agent */
  agentTypes?: string[];
  /** knowledge_level values, e.g. knowledge_assertion */
  knowledgeLevels?: string[];
  /** show each marker's label next to its icon */
  showLabels?: boolean;
};

const props = withDefaults(defineProps<Props>(), {
  agentTypes: () => [],
  knowledgeLevels: () => [],
  showLabels: false,
});

/**
 * agent types whose statements come from software, not a person reading the
 * source
 */
const MACHINE_AGENTS = new Set([
  "automated_agent",
  "computational_model",
  "text_mining_agent",
  "image_processing_agent",
]);

const agentMetas = computed(() =>
  [...new Set(props.agentTypes)].map((agentType) => ({
    ...getAgentTypeMeta(agentType),
    machine: MACHINE_AGENTS.has(agentType),
  })),
);
const levelMetas = computed(() =>
  [...new Set(props.knowledgeLevels)].map(getKnowledgeLevelMeta),
);
</script>

<style lang="scss" scoped>
.provenance {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  color: $dark-gray;
}

.marker {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.85rem;
}

/* machine-generated statements stand out from curated ones */
.marker.machine {
  padding: 1px 6px;
  border-radius: $rounded;
  background: $light-gray;
  color: $off-black;
}
</style>
