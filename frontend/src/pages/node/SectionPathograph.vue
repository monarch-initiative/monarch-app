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
      }}</AppLink>.
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
            v-tooltip="{
              content: nodeTooltip(lnode),
              allowHTML: true,
              maxWidth: 360,
              interactive: true,
              appendTo: appendToBody,
            }"
            class="node"
            :class="{ shared: lnode.shared, orphan: lnode.is_orphan }"
            :style="{ background: lnode.color || '#f3f4f6' }"
          >
            <span class="node-label">{{ lnode.label }}</span>
            <span v-if="lnode.entityId" class="node-id">{{
              lnode.entityId
            }}</span>
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
        <AppLink v-if="source.url" :to="source.url" class="legend-dismech"
          >Dismech</AppLink
        >
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
import { appendToBody } from "@/global/tooltip";

type Props = { node: Node };
const props = defineProps<Props>();
const route = useRoute();

const DISMECH_HOME = "https://dismech.monarchinitiative.org";

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
  /** ontology id displayed on the node, when it is itself an entity */
  entityId?: string;
  /** Monarch node route for that entity, when resolvable */
  link?: string;
};

type Point = { x: number; y: number };

/**
 * The ontology id + Monarch route for nodes that are themselves a term: HP
 * phenotypes and HGNC genes (from the merged anchor id), or any node carrying a
 * meta.term_id (e.g. biochemical CHEBI terms).
 */
const nodeEntity = (
  node: PathographNode,
): { entityId?: string; link?: string } => {
  if (node.id.startsWith("HP:"))
    return { entityId: node.id, link: `/${node.id}` };
  if (node.id.startsWith("GENE:hgnc:")) {
    const num = node.id.slice("GENE:hgnc:".length);
    return { entityId: `HGNC:${num}`, link: `/HGNC:${num}` };
  }
  const termId = (node.meta as Record<string, unknown> | undefined)?.term_id;
  if (typeof termId === "string" && termId.includes(":"))
    return { entityId: termId, link: `/${termId}` };
  return {};
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

/** html-escape dynamic text going into the tooltip markup */
const ESC: Record<string, string> = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
};
const esc = (s: unknown): string => String(s).replace(/[&<>"]/g, (c) => ESC[c]);

/** title-case a dismech node_type ("biological_process" → "Biological process") */
const prettyType = (t: string): string =>
  t.replace(/_/g, " ").replace(/^\w/, (c) => c.toUpperCase());

/** meta list fields that hold the "thingy" terms composing a stringy node */
const TERM_GROUPS = [
  { key: "gene_terms", label: "Genes" },
  { key: "cell_types", label: "Cell types" },
  { key: "biological_processes", label: "Biological processes" },
  { key: "molecular_functions", label: "Molecular functions" },
  { key: "locations", label: "Locations" },
  { key: "therapeutic_agents", label: "Therapeutic agents" },
  { key: "readouts", label: "Readouts" },
];

/** scalar meta worth a compact footer line */
const META_FIELDS = [
  { key: "frequency", label: "Frequency" },
  { key: "relationship_type", label: "Relationship" },
  { key: "variant_origin", label: "Variant origin" },
  { key: "clinical_significance", label: "Significance" },
];

const chip = (text: string): string =>
  `<span style="display:inline-block;background:rgba(0,0,0,0.06);border-radius:4px;padding:1px 6px;margin:2px 3px 0 0">${esc(text)}</span>`;

const termLabel = (item: unknown): string =>
  typeof item === "string"
    ? item
    : ((item as { label?: string })?.label ?? String(item));

type Evidence = {
  reference: string;
  reference_title?: string;
  snippet?: string;
  supports?: string;
};

/** PubMed link for a PMID reference, else no link (plain text) */
const refUrl = (reference: string): string | undefined =>
  reference.startsWith("PMID:")
    ? `https://pubmed.ncbi.nlm.nih.gov/${reference.slice("PMID:".length)}`
    : undefined;

const truncate = (s: string, n = 160): string =>
  s.length > n ? s.slice(0, n - 1).trimEnd() + "…" : s;

/** render the evidence references (linked PMIDs + title + snippet) */
const evidenceHtml = (evidence: Evidence[]): string => {
  const items = evidence
    .slice(0, 4)
    .map((e) => {
      const url = refUrl(e.reference);
      const ref = url
        ? `<a href="${url}" target="_blank" rel="noopener noreferrer" style="font-weight:500">${esc(e.reference)}</a>`
        : `<span style="font-weight:500">${esc(e.reference)}</span>`;
      const refutes =
        e.supports && e.supports !== "SUPPORT"
          ? ` <span style="opacity:0.7">(${esc(e.supports.toLowerCase())})</span>`
          : "";
      const title = e.reference_title
        ? ` — ${esc(truncate(e.reference_title, 90))}`
        : "";
      const snippet = e.snippet
        ? `<div style="opacity:0.75;font-style:italic;margin-top:1px">“${esc(truncate(e.snippet))}”</div>`
        : "";
      return `<div style="margin:3px 0;padding-left:6px;border-left:2px solid rgba(0,0,0,0.15)">${ref}${refutes}${title}${snippet}</div>`;
    })
    .join("");
  const more =
    evidence.length > 4
      ? `<div style="opacity:0.6;margin-top:2px">+${evidence.length - 4} more</div>`
      : "";
  return `<div style="margin-top:6px;font-size:0.75rem"><div style="opacity:0.6;margin-bottom:1px">Evidence (${evidence.length})</div>${items}${more}</div>`;
};

/**
 * Hover tooltip: the node label + type + description, then the constituent
 * ontology terms (genes, cell types, processes, locations, …) pulled from meta
 * — making the "thingy" composition of a free-text node explicit.
 */
const nodeTooltip = (node: LaidOutNode): string => {
  const meta = (node.meta || {}) as Record<string, unknown>;
  const parts: string[] = [
    `<div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.04em;opacity:0.65">${esc(prettyType(node.node_type))}</div>`,
    `<div style="font-weight:600;margin:1px 0 2px">${esc(node.label)}</div>`,
  ];
  if (node.entityId)
    parts.push(
      node.link
        ? `<div style="font-size:0.74rem;margin-bottom:4px"><a href="${esc(node.link)}" target="_blank" rel="noopener noreferrer">${esc(node.entityId)} — open in Monarch ↗</a></div>`
        : `<div style="font-size:0.74rem;opacity:0.7;margin-bottom:4px;font-family:monospace">${esc(node.entityId)}</div>`,
    );
  if (node.description)
    parts.push(
      `<div style="font-size:0.82rem;opacity:0.9;margin-bottom:5px">${esc(node.description)}</div>`,
    );

  for (const { key, label } of TERM_GROUPS) {
    const list = meta[key];
    if (!Array.isArray(list) || !list.length) continue;
    const shown = list.slice(0, 10).map((i) => chip(termLabel(i)));
    if (list.length > 10) shown.push(chip(`+${list.length - 10} more`));
    parts.push(
      `<div style="margin:3px 0;font-size:0.78rem"><span style="opacity:0.6">${esc(label)}:</span> ${shown.join("")}</div>`,
    );
  }

  const footer = META_FIELDS.filter(
    (f) => meta[f.key] != null && meta[f.key] !== "",
  )
    .map((f) => `${esc(f.label)}: ${esc(meta[f.key])}`)
    .join(" · ");
  if (footer)
    parts.push(
      `<div style="font-size:0.74rem;opacity:0.65;margin-top:5px">${footer}</div>`,
    );

  const evidence = meta.evidence;
  if (Array.isArray(evidence) && evidence.length)
    parts.push(evidenceHtml(evidence as Evidence[]));
  else if (meta.evidence_count)
    parts.push(
      `<div style="font-size:0.74rem;opacity:0.65;margin-top:5px">Evidence: ${esc(meta.evidence_count)}</div>`,
    );

  return `<div style="text-align:left;line-height:1.3">${parts.join("")}</div>`;
};
</script>

<style lang="scss" scoped>
.caption {
  margin: 0 0 10px;
  color: $gray;
  font-size: 0.9rem;
}

.disclaimer {
  margin: 0 0 12px;
  padding: 6px 10px;
  border-left: 3px solid $gray;
  background: rgba(0, 0, 0, 0.03);
  color: $gray;
  font-size: 0.8rem;
  line-height: 1.35;
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
  flex-direction: column;
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

.node-id {
  max-width: 100%;
  margin-top: 2px;
  overflow: hidden;
  font-size: 0.6rem;
  font-family: monospace;
  text-overflow: ellipsis;
  white-space: nowrap;
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
