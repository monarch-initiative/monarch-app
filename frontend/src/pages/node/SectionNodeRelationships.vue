<!--
  Mondo disease<->X relationships. These enter the KG with a generic
  biolink:related_to predicate but retain the real relation (an RO term) in
  original_predicate; the backend resolves that term's label from the KG.
  Grouped by relation label so the RO term's meaning is revealed. Shared by
  the disease and non-disease node header layouts (only one renders at a time).
-->
<template>
  <AppDetail
    v-for="group in relationshipGroups"
    :key="`rel-${group.key}`"
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
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { Entity, Node } from "@/api/model";
import AppDetail from "@/components/AppDetail.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";

type Props = { node: Node };

const { node } = defineProps<Props>();

/**
 * Group the node's Mondo disease<->X relationships by their relation label so
 * each RO relation (e.g. "has material basis in germline mutation in") becomes
 * a titled block. Prefer the KG-resolved label; fall back to the relation CURIE
 * so distinct unlabeled relations stay distinguishable (same chain for key +
 * title).
 */
const relationshipGroups = computed(() => {
  const groups = new Map<
    string,
    { key: string; label: string; entities: Entity[] }
  >();
  for (const rel of node.node_relationships ?? []) {
    if (!rel.related_entity) continue;
    const key = rel.relation_label || rel.relation || "Related to";
    const label = key.charAt(0).toUpperCase() + key.slice(1);
    let group = groups.get(key);
    if (!group) {
      group = { key, label, entities: [] };
      groups.set(key, group);
    }
    group.entities.push(rel.related_entity);
  }
  return [...groups.values()];
});
</script>
