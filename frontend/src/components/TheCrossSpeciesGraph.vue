<!--
  SVG visualization for a CrossSpeciesTermClique.
  Shows the cross-species parent at top center with species-specific children
  below, connected by vertical (subclass_of) and horizontal (same_as,
  homologous_to) edges.
-->

<template>
  <div ref="container" class="cross-species-graph">
    <svg
      :width="svgWidth"
      :height="svgHeight"
      :viewBox="`0 0 ${svgWidth} ${svgHeight}`"
    >
      <!-- Vertical edges (children → root) -->
      <line
        v-for="(child, i) in childNodes"
        :key="'v-' + i"
        :x1="rootNode.x"
        :y1="rootNode.y + rootNode.h / 2"
        :x2="child.x"
        :y2="child.y - child.h / 2"
        class="edge edge-vertical"
      />

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
          :x="(edge.sourceNode.x + edge.targetNode.x) / 2"
          :y="sidewaysLabelY(edge)"
          class="edge-label"
          text-anchor="middle"
        >
          {{ edge.predicate === "biolink:same_as" ? "same_as" : "homologous" }}
        </text>
      </g>

      <!-- Root node -->
      <g>
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
      </g>

      <!-- Child nodes -->
      <g v-for="(child, i) in childNodes" :key="'n-' + i">
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
          <!-- Taxon icon -->
          <image
            v-if="getTaxonIcon(child.entity)"
            :x="child.x - 10"
            :y="child.y - child.h / 2 + 6"
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
            {{ truncate(child.entity.name || "", 18) }}
          </text>
        </a>
      </g>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import type { CrossSpeciesTermClique, Entity } from "@/api/model";
import humanIcon from "@/assets/icons/humanIcon.svg?url";
import mouseIcon from "@/assets/icons/mouseIcon.svg?url";
import zebrafishIcon from "@/assets/icons/zebrafishIcon.svg?url";

const props = defineProps<{
  clique: CrossSpeciesTermClique;
  currentId: string;
}>();

const container = ref<HTMLElement | null>(null);

const ICON_MAP: Record<string, string> = {
  HP: humanIcon,
  MP: mouseIcon,
  ZP: zebrafishIcon,
};

const NODE_W = 140;
const NODE_H = 60;
const ROOT_W = 200;
const ROOT_H = 50;
const SPACING = 160;
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
}

const numChildren = computed(() => props.clique.clique_entities.length);

const svgWidth = computed(
  () => Math.max(numChildren.value, 1) * SPACING + SPACING,
);

const svgHeight = computed(() => CHILD_Y + NODE_H + 20);

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
  return props.clique.clique_entities.map((entity, i) => ({
    entity,
    x: startX + i * SPACING,
    y: CHILD_Y,
    w: NODE_W,
    h: NODE_H,
  }));
});

const sidewaysEdges = computed<SidewaysEdge[]>(() => {
  const childMap = new Map<string, LayoutNode>();
  childNodes.value.forEach((n) => childMap.set(n.entity.id, n));

  const edges: SidewaysEdge[] = [];
  for (const assoc of props.clique.clique_associations) {
    if (
      assoc.predicate === "biolink:same_as" ||
      assoc.predicate === "biolink:homologous_to"
    ) {
      const source = childMap.get(assoc.subject);
      const target = childMap.get(assoc.object);
      if (source && target) {
        edges.push({
          sourceNode: source,
          targetNode: target,
          predicate: assoc.predicate,
        });
      }
    }
  }
  return edges;
});

function sidewaysPath(edge: SidewaysEdge): string {
  const y = edge.sourceNode.y + edge.sourceNode.h / 2 + 12;
  const x1 = edge.sourceNode.x;
  const x2 = edge.targetNode.x;
  const midX = (x1 + x2) / 2;
  const curveOffset = 15;
  return `M ${x1} ${y - curveOffset} Q ${midX} ${y + curveOffset} ${x2} ${y - curveOffset}`;
}

function sidewaysLabelY(edge: SidewaysEdge): number {
  return edge.sourceNode.y + edge.sourceNode.h / 2 + 28;
}

function getTaxonIcon(entity: Entity): string | undefined {
  const prefix = entity.id.split(":")[0];
  return ICON_MAP[prefix] || undefined;
}

function truncate(text: string, max: number): string {
  return text.length > max ? text.slice(0, max - 1) + "\u2026" : text;
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
  stroke-width: 1.5;
  stroke-dasharray: 6 3;
}

.edge-label {
  font-size: 10px;
  fill: #888;
}

.node {
  stroke-width: 1.5;
}

.node-root {
  fill: hsl(185, 55%, 38%);
  stroke: hsl(185, 55%, 30%);
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

.node-current .node-id,
.node-current .node-name {
  fill: #404040;
}

.node-text {
  font-family: "Poppins", sans-serif;
  pointer-events: none;
}

.node-id {
  font-size: 12px;
  font-weight: bold;
  fill: #fff;
}

.node-name {
  font-size: 11px;
  fill: hsla(0, 0%, 100%, 0.9);
}

.node-current ~ text .node-id,
a:has(.node-current) .node-id,
a:has(.node-current) .node-name {
  fill: #404040;
}
</style>
