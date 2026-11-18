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
      <template v-else> Causal mechanism for {{ node.name }}. </template>
      From Dismech &mdash; curated using AI, may have mistakes.
      <AppLink :to="sourceLink">{{
        pathograph.category === "disease"
          ? "View this disorder on Dismech"
          : "Explore these disorders on Dismech"
      }}</AppLink
      >.
      <AppLink to="https://dismech.monarchinitiative.org/details/"
        >Learn more about Dismech</AppLink
      >.
    </p>

    <div class="graph-scroll">
      <svg
        :viewBox="`0 0 ${layout.width} ${layout.height}`"
        :style="{ width: layout.width + 'px', maxWidth: '100%' }"
        class="graph"
      >
        <defs>
          <marker
            :id="arrowId"
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
          :marker-end="`url(#${arrowId})`"
        >
          <title>
            {{ edge.predicate
            }}{{ edge.description ? `: ${edge.description}` : "" }}
          </title>
        </path>

        <!--
          Native svg text rather than html in a foreignObject: Safari lays
          foreignObject content out in a different coordinate space than the
          viewBox transform, so node text drifted further out of its box the
          further the node sat from the origin. Svg text scales with the
          viewBox, at the cost of wrapping the label ourselves.
        -->
        <g
          v-for="lnode in layout.nodes"
          :key="lnode.id"
          v-tooltip="{
            content: nodeTooltip(lnode),
            allowHTML: true,
            maxWidth: 360,
            interactive: true,
            appendTo: appendToBody,
          }"
          class="node"
          :class="{ shared: lnode.shared, orphan: lnode.is_orphan }"
        >
          <rect
            :x="lnode.x"
            :y="lnode.y"
            :width="NODE_W"
            :height="NODE_H"
            rx="6"
            ry="6"
            class="node-box"
            :style="{ fill: lnode.color || '#f3f4f6' }"
          />
          <text
            v-for="(line, i) in lnode.lines"
            :key="i"
            :x="lnode.x + NODE_W / 2"
            :y="labelBaseline(lnode, i)"
            class="node-label"
            text-anchor="middle"
          >
            {{ line }}
          </text>
          <text
            v-if="lnode.entityId"
            :x="lnode.x + NODE_W / 2"
            :y="idBaseline(lnode)"
            class="node-id"
            text-anchor="middle"
          >
            {{ idText(lnode.entityId) }}
          </text>
        </g>
      </svg>
    </div>

    <!-- per-disorder legend for the merged gene view -->
    <ul
      v-if="pathograph.category === 'gene' && pathograph.sources.length > 1"
      class="legend"
    >
      <li v-for="source in pathograph.sources" :key="source.id">
        <AppLink :to="`/${source.id}`">{{ source.name }}</AppLink>
        <AppLink v-if="source.url" :to="source.url" class="legend-dismech"
          >Dismech</AppLink
        >
      </li>
    </ul>
  </AppSection>
</template>

<script setup lang="ts">
import { computed, getCurrentInstance, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import dagre from "@dagrejs/dagre";
import type { Node } from "@/api/model";
import {
  getPathograph,
  type Pathograph,
  type PathographNode,
} from "@/api/pathograph";
import { useQuery } from "@/composables/use-query";
import { appendToBody } from "@/global/tooltip";
import { pathographTooltip as nodeTooltip } from "@/util/pathographTooltip";

type Props = { node: Node };
const props = defineProps<Props>();
const route = useRoute();

const DISMECH_HOME = "https://dismech.monarchinitiative.org";

/** unique per-instance SVG marker id (a global id breaks if rendered twice) */
const arrowId = `pathograph-arrow-${getCurrentInstance()?.uid ?? 0}`;

/**
 * "Source" link target: when a single disorder backs this pathograph (every
 * disease, and genes tied to just one disorder), deep-link straight to that
 * disorder's dismech page; for multi-disorder gene merges the per-disorder
 * legend below carries the individual links, so fall back to the dismech home.
 */
const sourceLink = computed(() => {
  const sources = pathograph.value?.sources ?? [];
  if (sources.length === 1 && sources[0]?.url) return sources[0].url;
  return DISMECH_HOME;
});

/** node box geometry + layout spacing */
const NODE_W = 184;
const NODE_H = 66;
const H_GAP = 28;
const V_GAP = 52;
const MARGIN = 20;

/**
 * Node text metrics. These are duplicated in the stylesheet below (svg text
 * cannot be measured from its own css), so keep the two in step: the label font
 * must match $sans, and the id font must match the .node-id rule.
 */
const PAD_X = 8;
const LABEL_FS = 12.5;
const LABEL_LH = 15;
const LABEL_LINES = 2;
const LABEL_FONT = `${LABEL_FS}px "Poppins", sans-serif`;
const ID_FS = 10;
const ID_FONT = `${ID_FS}px monospace`;
const ID_GAP = 3;
/** usable text width inside the node box */
const TEXT_W = NODE_W - PAD_X * 2;
/** rough cap-height ratio, to turn a line's top edge into a text baseline */
const BASELINE_RATIO = 0.8;

/** canvas text measurement, so label wrapping matches what actually renders */
let measureCtx: CanvasRenderingContext2D | null | undefined;
const measure = (text: string, font: string): number => {
  if (measureCtx === undefined)
    measureCtx = document.createElement("canvas").getContext("2d");
  if (!measureCtx) return text.length * LABEL_FS * 0.55;
  measureCtx.font = font;
  return measureCtx.measureText(text).width;
};

/** trim a line until it fits inside max width with an ellipsis appended */
const ellipsize = (text: string, maxWidth: number, font: string): string => {
  let trimmed = text;
  while (trimmed.length > 1 && measure(`${trimmed}…`, font) > maxWidth)
    trimmed = trimmed.slice(0, -1);
  return `${trimmed.trimEnd()}…`;
};

/** greedy word wrap, clamped to maxLines, ellipsizing whatever does not fit */
const wrapLabel = (
  text: string,
  maxWidth: number,
  font: string,
  maxLines: number,
): string[] => {
  const lines: string[] = [];
  let current = "";
  for (const word of text.split(/\s+/).filter(Boolean)) {
    const trial = current ? `${current} ${word}` : word;
    if (current && measure(trial, font) > maxWidth) {
      lines.push(current);
      current = word;
    } else current = trial;
  }
  if (current) lines.push(current);
  const kept = lines.slice(0, maxLines);
  /**
   * Two ways a line can still not fit: it is the last one we kept and the rest
   * of the label was dropped, or it is a single word too long to have had any
   * wrap point (hyphenated compounds are common here). Nothing clips svg text,
   * so measure every kept line rather than assuming only the last overflows.
   */
  const dropped = lines.length > kept.length;
  return kept.map((line, i) =>
    (dropped && i === kept.length - 1) || measure(line, font) > maxWidth
      ? ellipsize(line, maxWidth, font)
      : line,
  );
};

/**
 * Poppins is a webfont, so the first layout can measure against the fallback
 * font and wrap slightly wrong. Flip once it loads to re-wrap against the real
 * metrics.
 */
const fontsReady = ref(false);
onMounted(() => {
  document.fonts?.ready.then(() => (fontsReady.value = true));
});

/**
 * The id line, truncated to the box. Curies are always short enough today, but
 * meta.term_id is upstream data and svg text has no overflow of its own.
 */
const idText = (id?: string): string => {
  if (!id) return "";
  return measure(id, ID_FONT) > TEXT_W ? ellipsize(id, TEXT_W, ID_FONT) : id;
};

/** total height of a node's stacked label lines + optional id line */
const textHeight = (lnode: LaidOutNode): number =>
  lnode.lines.length * LABEL_LH + (lnode.entityId ? ID_GAP + ID_FS : 0);

/** top edge of the centred text block within the node box */
const textTop = (lnode: LaidOutNode): number =>
  lnode.y + (NODE_H - textHeight(lnode)) / 2;

const labelBaseline = (lnode: LaidOutNode, i: number): number =>
  textTop(lnode) +
  i * LABEL_LH +
  (LABEL_LH - LABEL_FS) / 2 +
  LABEL_FS * BASELINE_RATIO;

const idBaseline = (lnode: LaidOutNode): number =>
  textTop(lnode) +
  lnode.lines.length * LABEL_LH +
  ID_GAP +
  ID_FS * BASELINE_RATIO;

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
  /** label word-wrapped to fit the box, since svg text does not wrap itself */
  lines: string[];
  /** ontology id displayed on the node, when it is itself an entity */
  entityId?: string;
  /** Monarch node route for that entity, when resolvable */
  link?: string;
};

type Point = { x: number; y: number };

/**
 * A well-formed single CURIE (one colon, no whitespace) - excludes the
 * `<mondo>::<name>` disorder-local pseudo-ids and bare free-text node ids.
 */
const isCurie = (value: unknown): value is string =>
  typeof value === "string" && /^[^:\s]+:[^:\s]+$/.test(value);

/**
 * Uppercase only the prefix so Monarch routes resolve (e.g. `hgnc:1956` ->
 * `HGNC:1956`) without corrupting a local id that contains letters.
 */
const normalizeCurie = (curie: string): string => {
  const [prefix, local] = curie.split(":");
  return `${prefix.toUpperCase()}:${local}`;
};

/**
 * The ontology id + Monarch route for nodes that are themselves a term: any
 * node carrying a real term CURIE (HP phenotype, MONDO disease-like phenotype,
 * CHEBI biomarker, HGNC gene, …). Prefer the authoritative `meta.term_id`, then
 * fall back to the merged anchor `node.id` when it is itself a CURIE.
 */
const nodeEntity = (
  node: PathographNode,
): { entityId?: string; link?: string } => {
  const termId = (node.meta as Record<string, unknown> | undefined)?.term_id;
  const raw = isCurie(termId) ? termId : isCurie(node.id) ? node.id : undefined;
  if (!raw) return {};
  const curie = normalizeCurie(raw);
  return { entityId: curie, link: `/${curie}` };
};

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
  /** re-wrap labels once the real font metrics are available */
  void fontsReady.value;
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

  /** dagre node coords are centers; convert to the box's top-left corner */
  const nodes: LaidOutNode[] = data.nodes.map((n) => {
    const p = g.node(n.id) as Point;
    return {
      ...n,
      x: (p?.x ?? 0) - NODE_W / 2,
      y: (p?.y ?? 0) - NODE_H / 2,
      shared: sharedNodes.has(n.id),
      lines: wrapLabel(n.label, TEXT_W, LABEL_FONT, LABEL_LINES),
      ...nodeEntity(n),
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
  cursor: default;
}

.node-box {
  stroke: rgba(0, 0, 0, 0.25);
  stroke-width: 1;

  .shared & {
    stroke: rgba(0, 0, 0, 0.7);
    stroke-width: 2;
  }

  .orphan & {
    stroke-dasharray: 4 3;
  }
}

/* font-size/family here must match the LABEL_* and ID_* metrics in the script,
   which measure and wrap this text ahead of render. */
.node-label {
  fill: currentColor;
  font-size: 12.5px;
}

.node-id {
  fill: currentColor;
  font-size: 10px;
  font-family: monospace;
  opacity: 0.55;
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

.legend-dismech {
  margin-left: 4px;
  font-size: 0.75rem;
  opacity: 0.7;
}
</style>
