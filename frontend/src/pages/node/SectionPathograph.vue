<!--
  dismech disease-mechanism pathograph for a disease or gene node.

  Fetches the merged pathograph from the backend (which proxies the dismech
  artifact and, for genes, anchor-merges every disorder the gene participates
  in) and lays it out as a left→right causal DAG. Renders nothing when the node
  has no pathograph (the common case), so it self-hides.
-->

<template>
  <AppSection
    v-if="pathograph && layout.nodes.length"
    width="full"
    class="inset"
    alignment="left"
  >
    <AppHeading icon="diagram-project">Disease Mechanism Pathograph</AppHeading>

    <p class="caption">
      <template v-if="pathograph.category === 'gene'">
        Mechanisms involving {{ node.name }} across
        {{ pathograph.sources.length }} disorder{{
          pathograph.sources.length === 1 ? "" : "s"
        }}.
      </template>
      <template v-else>
        Curated causal mechanism for {{ node.name }}.
      </template>
      Source:
      <AppLink to="https://dismech.monarchinitiative.org">dismech</AppLink>.
    </p>

    <div class="graph-scroll">
      <svg
        :viewBox="`0 0 ${layout.width} ${layout.height}`"
        :style="{ width: layout.width + 'px', maxWidth: '100%' }"
        class="graph"
      >
        <defs>
          <marker
            id="pathograph-arrow"
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            markerWidth="7"
            markerHeight="7"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#9ca3af" />
          </marker>
        </defs>

        <!-- edges -->
        <path
          v-for="(edge, i) in layout.edges"
          :key="`e${i}`"
          :d="edge.path"
          class="edge"
          marker-end="url(#pathograph-arrow)"
        >
          <title>
            {{ edge.predicate
            }}{{ edge.description ? `: ${edge.description}` : "" }}
          </title>
        </path>

        <!-- nodes -->
        <foreignObject
          v-for="lnode in layout.nodes"
          :key="lnode.id"
          :x="lnode.x"
          :y="lnode.y"
          :width="NODE_W"
          :height="NODE_H"
        >
          <div
            class="node"
            :class="{ shared: lnode.shared, orphan: lnode.is_orphan }"
            :style="{ background: lnode.color || '#f3f4f6' }"
            :title="lnode.tooltip"
          >
            <span class="node-label">{{ lnode.label }}</span>
          </div>
        </foreignObject>
      </svg>
    </div>

    <!-- per-disorder legend for the merged gene view -->
    <ul
      v-if="pathograph.category === 'gene' && pathograph.sources.length > 1"
      class="legend"
    >
      <li v-for="source in pathograph.sources" :key="source.id">
        <AppLink :to="`/${source.id}`">{{ source.name }}</AppLink>
      </li>
    </ul>
  </AppSection>
</template>

<script setup lang="ts">
import { computed, watch } from "vue";
import { useRoute } from "vue-router";
import dagre from "@dagrejs/dagre";
import type { Node } from "@/api/model";
import {
  getPathograph,
  type Pathograph,
  type PathographNode,
} from "@/api/pathograph";
import { useQuery } from "@/composables/use-query";

type Props = { node: Node };
const props = defineProps<Props>();
const route = useRoute();

/** node box geometry + layout spacing */
const NODE_W = 184;
const NODE_H = 58;
const H_GAP = 28;
const V_GAP = 52;
const MARGIN = 20;

const { query: runGetPathograph, data: pathograph } = useQuery<
  Pathograph | null,
  []
>(async () => {
  /** pathographs only exist for diseases and genes; skip the fetch otherwise */
  const category = props.node.category;
  if (category !== "biolink:Disease" && category !== "biolink:Gene")
    return null;
  return getPathograph(props.node.id || "");
}, null);

/**
 * refetch on node change; 404 (no pathograph) leaves data null and hides
 * section
 */
watch([() => route.path, () => props.node.id], runGetPathograph, {
  immediate: true,
});

type LaidOutNode = PathographNode & {
  x: number;
  y: number;
  shared: boolean;
  tooltip: string;
};

type Point = { x: number; y: number };

/** smooth an edge polyline through its bend points with quadratic curves */
const smoothPath = (points: Point[]): string => {
  if (points.length < 2) return "";
  let d = `M ${points[0].x} ${points[0].y}`;
  for (let i = 1; i < points.length - 1; i++) {
    const mid = {
      x: (points[i].x + points[i + 1].x) / 2,
      y: (points[i].y + points[i + 1].y) / 2,
    };
    d += ` Q ${points[i].x} ${points[i].y} ${mid.x} ${mid.y}`;
  }
  const last = points[points.length - 1];
  d += ` L ${last.x} ${last.y}`;
  return d;
};

/** dagre layered DAG layout (rankdir left→right, crossing-minimized) */
const layout = computed(() => {
  const data = pathograph.value;
  const empty = {
    nodes: [] as LaidOutNode[],
    edges: [] as {
      path: string;
      predicate?: string | null;
      description?: string | null;
    }[],
    width: 0,
    height: 0,
  };
  if (!data || !data.nodes.length) return empty;

  const g = new dagre.graphlib.Graph();
  g.setGraph({
    // left→right: the (often many) terminal phenotypes stack vertically, so a
    // big graph grows in height (page-scrollable) instead of overflowing width.
    rankdir: "LR",
    nodesep: H_GAP,
    ranksep: V_GAP,
    marginx: MARGIN,
    marginy: MARGIN,
  });
  g.setDefaultEdgeLabel(() => ({}));
  for (const n of data.nodes)
    g.setNode(n.id, { width: NODE_W, height: NODE_H });
  for (const e of data.edges)
    if (g.hasNode(e.source) && g.hasNode(e.target))
      g.setEdge(e.source, e.target);
  dagre.layout(g);

  const sharedNodes = new Set(
    data.nodes.filter((n) => (n.sources?.length || 0) > 1).map((n) => n.id),
  );

  /** dagre node coords are centers; convert to top-left for foreignObject */
  const nodes: LaidOutNode[] = data.nodes.map((n) => {
    const p = g.node(n.id) as Point;
    return {
      ...n,
      x: (p?.x ?? 0) - NODE_W / 2,
      y: (p?.y ?? 0) - NODE_H / 2,
      shared: sharedNodes.has(n.id),
      tooltip: [n.label, n.description].filter(Boolean).join(" — "),
    };
  });

  const edges = data.edges
    .map((e) => {
      if (!g.hasNode(e.source) || !g.hasNode(e.target)) return null;
      const points = (g.edge(e.source, e.target)?.points || []) as Point[];
      if (points.length < 2) return null;
      return {
        path: smoothPath(points),
        predicate: e.predicate,
        description: e.description,
      };
    })
    .filter((e): e is NonNullable<typeof e> => e !== null);

  const graph = g.graph();
  return { nodes, edges, width: graph.width || 0, height: graph.height || 0 };
});
</script>

<style lang="scss" scoped>
.caption {
  margin: 0 0 10px;
  color: $gray;
  font-size: 0.9rem;
}

.graph-scroll {
  width: 100%;
  overflow-x: auto;
}

.graph {
  display: block;
  height: auto;
}

.edge {
  fill: none;
  stroke: #9ca3af;
  stroke-width: 1.5;
}

.node {
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  padding: 4px 8px;
  border: 1px solid rgba(0, 0, 0, 0.25);
  border-radius: 6px;
  text-align: center;
  cursor: default;

  &.shared {
    border-width: 2px;
    border-color: rgba(0, 0, 0, 0.7);
    box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.08);
  }

  &.orphan {
    border-style: dashed;
  }
}

.node-label {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-size: 0.78rem;
  line-height: 1.15;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  margin: 10px 0 0;
  padding: 0;
  gap: 6px 16px;
  font-size: 0.85rem;
  list-style: none;
}
</style>
