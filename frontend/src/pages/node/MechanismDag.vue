<!--
  compact left→right causal DAG of the mechanism paths behind one phenotype row.
  paths are merged so each mechanism node renders once, however many paths share it.
-->

<template>
  <div class="dag-scroll">
    <svg
      :viewBox="`0 0 ${layout.width} ${layout.height}`"
      :width="layout.width"
      :height="layout.height"
      :style="{
        maxWidth: '100%',
        aspectRatio: `${layout.width} / ${layout.height}`,
      }"
      class="dag"
    >
      <defs>
        <marker
          :id="arrowId"
          viewBox="0 0 10 10"
          refX="9"
          refY="5"
          markerWidth="6"
          markerHeight="6"
          orient="auto-start-reverse"
        >
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#9ca3af" />
        </marker>
      </defs>
      <path
        v-for="(edge, i) in layout.edges"
        :key="`e${i}`"
        :d="edge.path"
        class="edge"
        :marker-end="`url(#${arrowId})`"
      >
        <title>{{ edge.linkType }}</title>
      </path>
      <g
        v-for="node in layout.nodes"
        :key="node.id"
        v-tooltip="{
          content: node.tooltip,
          allowHTML: true,
          maxWidth: 360,
          interactive: true,
          appendTo: appendToBody,
        }"
        :class="['node', node.kind]"
      >
        <rect
          :x="node.x"
          :y="node.y"
          :width="NODE_W"
          :height="NODE_H"
          rx="5"
          ry="5"
        />
        <text
          v-for="(line, i) in node.lines"
          :key="i"
          :x="node.x + NODE_W / 2"
          :y="node.y + NODE_H / 2 + (i - (node.lines.length - 1) / 2) * LINE_H"
          dominant-baseline="central"
          text-anchor="middle"
        >
          {{ line }}
        </text>
      </g>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed, getCurrentInstance } from "vue";
import dagre from "@dagrejs/dagre";
import { appendToBody } from "@/global/tooltip";

export type DagNode = {
  id: string;
  label: string;
  /** mechanism node, sequela phenotype on the way, or the terminal phenotype */
  kind: "mechanism" | "sequela" | "phenotype";
  /** tooltip html */
  tooltip?: string;
};

export type DagEdge = {
  source: string;
  target: string;
  linkType?: string | null;
};

type Props = {
  nodes: DagNode[];
  edges: DagEdge[];
};

const props = defineProps<Props>();

const arrowId = `mechanism-arrow-${getCurrentInstance()?.uid ?? 0}`;

const NODE_W = 150;
const NODE_H = 38;
const LINE_H = 13;
const FONT = '11px "Poppins", sans-serif';
const TEXT_W = NODE_W - 12;

let ctx: CanvasRenderingContext2D | null | undefined;
const measure = (text: string): number => {
  if (ctx === undefined)
    ctx = document.createElement("canvas").getContext("2d");
  if (!ctx) return text.length * 6;
  ctx.font = FONT;
  return ctx.measureText(text).width;
};

/** word wrap into at most two lines, ellipsizing the remainder */
const wrap = (text: string): string[] => {
  const lines: string[] = [];
  let current = "";
  for (const word of text.split(/\s+/).filter(Boolean)) {
    const trial = current ? `${current} ${word}` : word;
    if (current && measure(trial) > TEXT_W) {
      lines.push(current);
      current = word;
    } else current = trial;
  }
  if (current) lines.push(current);
  const kept = lines.slice(0, 2);
  return kept.map((line, i) => {
    const overflow = (lines.length > 2 && i === 1) || measure(line) > TEXT_W;
    if (!overflow) return line;
    let trimmed = line;
    while (trimmed.length > 1 && measure(`${trimmed}…`) > TEXT_W)
      trimmed = trimmed.slice(0, -1);
    return `${trimmed.trimEnd()}…`;
  });
};

type Point = { x: number; y: number };

const smooth = (points: Point[]): string => {
  let d = `M ${points[0].x} ${points[0].y}`;
  for (let i = 1; i < points.length - 1; i++) {
    const mid = {
      x: (points[i].x + points[i + 1].x) / 2,
      y: (points[i].y + points[i + 1].y) / 2,
    };
    d += ` Q ${points[i].x} ${points[i].y} ${mid.x} ${mid.y}`;
  }
  const last = points[points.length - 1];
  return `${d} L ${last.x} ${last.y}`;
};

const layout = computed(() => {
  const g = new dagre.graphlib.Graph();
  g.setGraph({
    rankdir: "LR",
    nodesep: 12,
    ranksep: 36,
    marginx: 8,
    marginy: 8,
  });
  g.setDefaultEdgeLabel(() => ({}));
  for (const n of props.nodes)
    g.setNode(n.id, { width: NODE_W, height: NODE_H });
  for (const e of props.edges) g.setEdge(e.source, e.target);
  dagre.layout(g);

  const nodes = props.nodes.map((n) => {
    const p = g.node(n.id) as Point;
    return {
      ...n,
      x: p.x - NODE_W / 2,
      y: p.y - NODE_H / 2,
      lines: wrap(n.label),
    };
  });
  const edges = props.edges
    .map((e) => {
      const points = (g.edge(e.source, e.target)?.points || []) as Point[];
      return points.length < 2
        ? null
        : { path: smooth(points), linkType: e.linkType };
    })
    .filter((e): e is NonNullable<typeof e> => e !== null);
  const graph = g.graph();
  return { nodes, edges, width: graph.width || 0, height: graph.height || 0 };
});
</script>

<style lang="scss" scoped>
.dag-scroll {
  overflow-x: auto;
}

.dag {
  display: block;
  height: auto;
}

.edge {
  fill: none;
  stroke: #9ca3af;
  stroke-width: 1.3;
}

.node {
  rect {
    fill: $white;
    stroke: $theme;
    stroke-width: 1;
  }

  text {
    fill: $black;
    font-size: 11px;
  }
}

.node.sequela rect {
  stroke-dasharray: 4 3;
}

.node.phenotype {
  rect {
    fill: $theme;
  }

  text {
    fill: $white;
  }
}
</style>
