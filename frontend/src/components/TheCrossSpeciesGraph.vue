<!--
  SVG visualization for a CrossSpeciesTermClique.
  Shows the cross-species parent at top center with species-specific children
  below, connected by vertical (subclass_of) and horizontal (same_as,
  homologous_to) edges.
-->

<template>
  <div class="cross-species-graph">
    <svg
      :width="svgWidth"
      :height="svgHeight"
      :viewBox="`0 0 ${svgWidth} ${svgHeight}`"
    >
      <!-- Vertical edges (children → root) -->
      <g v-for="(edge, i) in verticalEdges" :key="'v-' + i">
        <line
          :x1="rootNode.x"
          :y1="rootNode.y + rootNode.h / 2"
          :x2="edge.child.x"
          :y2="edge.child.y - edge.child.h / 2"
          class="edge edge-vertical"
        />
        <text
          v-tooltip="
            edgeTooltip(edge.predicate, edge.source, edge.subject, edge.object)
          "
          :x="edge.child.x"
          :y="edge.child.y - edge.child.h / 2 - 14"
          class="edge-label"
          text-anchor="middle"
        >
          {{ edge.label }}
        </text>
      </g>

      <!-- Horizontal edges (same_as / homologous_to between children) -->
      <g v-for="(edge, i) in sidewaysEdges" :key="'h-' + i">
        <path
          :d="sidewaysPath(edge)"
          :class="[
            'edge',
            edge.predicate === 'biolink:same_as'
              ? 'edge-same-as'
              : 'edge-homologous',
          ]"
          fill="none"
        />
        <text
          v-tooltip="
            edgeTooltip(edge.predicate, edge.source, edge.subject, edge.object)
          "
          :x="(edge.sourceNode.x + edge.targetNode.x) / 2"
          :y="sidewaysLabelY(edge)"
          class="edge-label"
          text-anchor="middle"
        >
          {{ edge.predicate === "biolink:same_as" ? "same_as" : "homologous" }}
        </text>
      </g>

      <!-- Root node -->
      <g v-tooltip="nodeTooltip(clique.root_term)">
        <a :href="`/${clique.root_term.id}`">
          <rect
            :x="rootNode.x - rootNode.w / 2"
            :y="rootNode.y - rootNode.h / 2"
            :width="rootNode.w"
            :height="rootNode.h"
            rx="8"
            ry="8"
            class="node node-root"
          />
          <text
            :x="rootNode.x"
            :y="rootNode.y - 8"
            class="node-text node-id"
            text-anchor="middle"
          >
            {{ clique.root_term.id }}
          </text>
          <text
            :x="rootNode.x"
            :y="rootNode.y + 10"
            class="node-text node-name"
            text-anchor="middle"
          >
            {{ truncate(clique.root_term.name || "", 30) }}
          </text>
        </a>
      </g>

      <!-- Child nodes -->
      <g
        v-for="(child, i) in childNodes"
        :key="'n-' + i"
        v-tooltip="nodeTooltip(child.entity)"
      >
        <a :href="`/${child.entity.id}`">
          <rect
            :x="child.x - child.w / 2"
            :y="child.y - child.h / 2"
            :width="child.w"
            :height="child.h"
            rx="8"
            ry="8"
            :class="[
              'node',
              'node-child',
              child.entity.id === currentId ? 'node-current' : '',
            ]"
          />
          <!-- Taxon icon (top-left badge) -->
          <image
            v-if="getTaxonIcon(child.entity)"
            :x="child.x - child.w / 2 + 5"
            :y="child.y - child.h / 2 + 3"
            width="20"
            height="20"
            :href="getTaxonIcon(child.entity)"
          />
          <text
            :x="child.x"
            :y="child.y + 2"
            class="node-text node-id"
            text-anchor="middle"
          >
            {{ child.entity.id }}
          </text>
          <text
            :x="child.x"
            :y="child.y + 20"
            class="node-text node-name"
            text-anchor="middle"
          >
            {{ truncate(child.entity.name || "", 22) }}
          </text>
        </a>
        <!-- "+N more" badge when collapsed -->
        <text
          v-if="visibleChildren.groupCounts.get(child.entity.id)"
          :x="child.x"
          :y="child.y + child.h / 2 + 16"
          class="more-badge"
          text-anchor="middle"
        >
          +{{ visibleChildren.groupCounts.get(child.entity.id) }} more
        </text>
      </g>
    </svg>
    <button
      v-if="hiddenCount > 0 || expanded"
      class="toggle-btn"
      @click="expanded = !expanded"
    >
      {{
        expanded ? "Show 1 per species" : `Show all ${totalChildren} children`
      }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import type { CrossSpeciesTermClique, Entity } from "@/api/model";
import frogIcon from "@/assets/icons/frogIcon.svg?url";
import humanIcon from "@/assets/icons/humanIcon.svg?url";
import mouseIcon from "@/assets/icons/mouseIcon.svg?url";
import zebrafishIcon from "@/assets/icons/zebrafishIcon.svg?url";

const props = defineProps<{
  clique: CrossSpeciesTermClique;
  currentId: string;
}>();

const ICON_MAP: Record<string, string> = {
  HP: humanIcon,
  MP: mouseIcon,
  ZP: zebrafishIcon,
  XPO: frogIcon,
};

const NODE_W = 170;
const NODE_H = 60;
const ROOT_W = 200;
const ROOT_H = 50;
const SPACING = 190;
const PARENT_Y = 50;
const CHILD_Y = 180;

interface LayoutNode {
  entity: Entity;
  x: number;
  y: number;
  w: number;
  h: number;
}

interface SidewaysEdge {
  sourceNode: LayoutNode;
  targetNode: LayoutNode;
  predicate: string;
  /** Vertical offset index for stacking multiple edges between the same pair */
  offsetIndex: number;
  source?: string;
  subject: string;
  object: string;
}

/** Collapse/expand state */
const expanded = ref(false);

/**
 * Group clique entities by ID prefix; return visible entities and per-prefix
 * counts
 */
const visibleChildren = computed(() => {
  const all = props.clique.clique_entities;
  const groups = new Map<string, Entity[]>();
  for (const entity of all) {
    const prefix = entity.id.split(":")[0];
    if (!groups.has(prefix)) groups.set(prefix, []);
    groups.get(prefix)!.push(entity);
  }
  if (expanded.value) {
    return { entities: all, groupCounts: new Map<string, number>() };
  }
  const entities: Entity[] = [];
  const groupCounts = new Map<string, number>();
  for (const [, members] of groups) {
    entities.push(members[0]);
    if (members.length > 1) {
      groupCounts.set(members[0].id, members.length - 1);
    }
  }
  return { entities, groupCounts };
});

const totalChildren = computed(() => props.clique.clique_entities.length);
const hiddenCount = computed(
  () => totalChildren.value - visibleChildren.value.entities.length,
);

const numChildren = computed(() => visibleChildren.value.entities.length);

const svgWidth = computed(
  () => Math.max(numChildren.value, 1) * SPACING + SPACING,
);

const svgHeight = computed(() => {
  const maxDepth = sidewaysEdges.value.reduce(
    (max, edge) => Math.max(max, curveDepth(edge)),
    20,
  );
  return CHILD_Y + NODE_H / 2 + maxDepth * 0.5 + 28;
});

const rootNode = computed(() => ({
  entity: props.clique.root_term,
  x: svgWidth.value / 2,
  y: PARENT_Y,
  w: ROOT_W,
  h: ROOT_H,
}));

const childNodes = computed<LayoutNode[]>(() => {
  const n = numChildren.value;
  const totalWidth = (n - 1) * SPACING;
  const startX = svgWidth.value / 2 - totalWidth / 2;
  return visibleChildren.value.entities.map((entity, i) => ({
    entity,
    x: startX + i * SPACING,
    y: CHILD_Y,
    w: NODE_W,
    h: NODE_H,
  }));
});

const verticalEdges = computed(() => {
  const assocMap = new Map<
    string,
    { predicate: string; source?: string; object: string }
  >();
  for (const assoc of props.clique.clique_associations) {
    if (
      assoc.predicate !== "biolink:same_as" &&
      assoc.predicate !== "biolink:homologous_to"
    ) {
      assocMap.set(assoc.subject, {
        predicate: assoc.predicate,
        source: assoc.primary_knowledge_source,
        object: assoc.object,
      });
    }
  }
  return childNodes.value.map((child) => {
    const info = assocMap.get(child.entity.id);
    const predicate = info?.predicate ?? "biolink:subclass_of";
    return {
      child,
      label: predicate.replace("biolink:", "").replace(/_/g, " "),
      predicate,
      source: info?.source,
      subject: child.entity.id,
      object: info?.object ?? props.clique.root_term.id,
    };
  });
});

const sidewaysEdges = computed<SidewaysEdge[]>(() => {
  const childMap = new Map<string, LayoutNode>();
  childNodes.value.forEach((n) => childMap.set(n.entity.id, n));

  const pairCount = new Map<string, number>();
  const edges: SidewaysEdge[] = [];
  for (const assoc of props.clique.clique_associations) {
    if (
      assoc.predicate === "biolink:same_as" ||
      assoc.predicate === "biolink:homologous_to"
    ) {
      const source = childMap.get(assoc.subject);
      const target = childMap.get(assoc.object);
      if (source && target) {
        const pairKey = [assoc.subject, assoc.object].sort().join("--");
        const idx = pairCount.get(pairKey) ?? 0;
        pairCount.set(pairKey, idx + 1);
        edges.push({
          sourceNode: source,
          targetNode: target,
          predicate: assoc.predicate,
          offsetIndex: idx,
          source: assoc.primary_knowledge_source,
          subject: assoc.subject,
          object: assoc.object,
        });
      }
    }
  }
  return edges;
});

function curveDepth(edge: SidewaysEdge): number {
  const span = Math.abs(edge.targetNode.x - edge.sourceNode.x);
  return span * 0.15 + edge.offsetIndex * 20;
}

function sidewaysPath(edge: SidewaysEdge): string {
  const nodeBottom = edge.sourceNode.y + edge.sourceNode.h / 2;
  const x1 = edge.sourceNode.x;
  const x2 = edge.targetNode.x;
  const midX = (x1 + x2) / 2;
  const depth = curveDepth(edge);
  return `M ${x1} ${nodeBottom} Q ${midX} ${nodeBottom + depth} ${x2} ${nodeBottom}`;
}

function sidewaysLabelY(edge: SidewaysEdge): number {
  const nodeBottom = edge.sourceNode.y + edge.sourceNode.h / 2;
  return nodeBottom + curveDepth(edge) * 0.5 + 12;
}

function getTaxonIcon(entity: Entity): string | undefined {
  const prefix = entity.id.split(":")[0];
  return ICON_MAP[prefix] || undefined;
}

function truncate(text: string, max: number): string {
  return text.length > max ? text.slice(0, max - 1) + "\u2026" : text;
}

function nodeTooltip(entity: Entity): string {
  return `<strong>${entity.id}</strong><br/>${entity.name || ""}`;
}

function edgeTooltip(
  predicate: string,
  source: string | undefined,
  subject: string,
  object: string,
): string {
  let html = `<strong>${predicate}</strong><br/>${subject} → ${object}`;
  if (source) html += `<br/>Source: ${source}`;
  return html;
}
</script>

<style scoped>
.cross-species-graph {
  width: 100%;
  overflow-x: auto;
}

svg {
  display: block;
  margin: 0 auto;
}

.edge {
  stroke-width: 1.5;
}

.edge-vertical {
  stroke: #b0b0b0;
}

.edge-same-as {
  stroke: hsl(185, 40%, 55%);
  stroke-width: 1.5;
}

.edge-homologous {
  stroke: hsl(240, 15%, 62%);
  stroke-dasharray: 6 3;
  stroke-width: 1.5;
}

.edge-label {
  fill: #888;
  font-size: 10px;
  cursor: help;
}

.node {
  stroke-width: 1.5;
}

.node-root {
  fill: hsl(185, 55%, 38%);
  stroke: hsl(185, 55%, 30%);
  cursor: pointer;
}

.node-root:hover {
  fill: hsl(185, 55%, 45%);
}

.node-child {
  fill: hsl(200, 15%, 55%);
  stroke: hsl(200, 15%, 45%);
}

.node-current {
  fill: hsl(185, 50%, 94%);
  stroke: hsl(185, 60%, 42%);
  stroke-width: 2.5;
}

.node-text {
  font-family: "Poppins", sans-serif;
}

.node-id {
  fill: #fff;
  font-weight: bold;
  font-size: 12px;
}

.node-name {
  fill: hsla(0, 0%, 100%, 0.9);
  font-size: 11px;
}

a:has(.node-current) .node-id,
a:has(.node-current) .node-name {
  fill: #404040;
}

.more-badge {
  fill: hsl(200, 15%, 40%);
  font-style: italic;
  font-size: 11px;
  font-family: "Poppins", sans-serif;
}

.toggle-btn {
  display: block;
  margin: 8px auto 0;
  padding: 4px 14px;
  border: 1px solid hsl(200, 15%, 70%);
  border-radius: 4px;
  background: #fff;
  color: hsl(200, 15%, 35%);
  font-size: 13px;
  font-family: "Poppins", sans-serif;
  cursor: pointer;
}

.toggle-btn:hover {
  background: hsl(200, 15%, 95%);
}
</style>
