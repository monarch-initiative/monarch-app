import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import { getDismechStatus } from "@/api/dismech";
import type {
  DismechMatch,
  DismechTreatment,
  MechanismNode,
} from "@/api/dismech";
import type { DagEdge, DagNode } from "@/pages/node/MechanismDag.vue";
import { pathographTooltip } from "@/util/pathographTooltip";

/** whether the api serves dismech integrations; asked once per page load */
const available = ref<boolean | null>(null);
let asked = false;

/**
 * dismech integrations show wherever the api serves them (not against an api
 * without dismech.duckdb, where the existing tables show instead). ?dismech=0
 * turns them off, to compare.
 */
export const useDismech = () => {
  const route = useRoute();
  if (!asked) {
    asked = true;
    getDismechStatus()
      .then(() => (available.value = true))
      .catch(() => (available.value = false));
  }
  return computed(() => !!available.value && route.query.dismech !== "0");
};

export const DISMECH_SITE = "https://dismech.monarchinitiative.org";

export const dismechDisorderUrl = (file: string) =>
  `${DISMECH_SITE}/pages/disorders/${file}.html`;

export const SOURCE_LABELS: Record<string, string> = {
  "infores:omim": "OMIM",
  "infores:orphanet": "Orphanet",
  "infores:mondo": "Mondo",
  "infores:decipher": "DECIPHER",
};

export const sourceLabel = (source: string) =>
  SOURCE_LABELS[source] ?? source.replace("infores:", "");

/** dismech frequency enum, as HP frequency terms */
export const FREQUENCY_LABELS: Record<string, string> = {
  "HP:0040280": "Obligate",
  "HP:0040281": "Very frequent",
  "HP:0040282": "Frequent",
  "HP:0040283": "Occasional",
  "HP:0040284": "Very rare",
  "HP:0040285": "Excluded",
};

/** title-case a dismech enum, e.g. SMALL_MOLECULE -> Small molecule */
export const enumLabel = (value?: string | null) =>
  value
    ? value.charAt(0) + value.slice(1).toLowerCase().replace(/_/g, " ")
    : "";

/** descriptor slots, keyed the way the pathograph tooltip groups its term chips */
const TERM_KEYS: Record<string, string> = {
  gene: "gene_terms",
  genes: "gene_terms",
};

/** hover markup matching the full pathograph's node tooltips */
export const nodeTooltip = (
  nodes: Record<string, MechanismNode>,
  nodeId: string,
  terminal = false,
) => {
  const node = nodes[nodeId];
  if (!node) return "";
  const meta: Record<string, unknown> = {
    frequency: node.frequency,
    evidence: node.evidence.map((e) => ({
      reference: e.reference,
      reference_title: e.title,
      snippet: e.snippet,
      supports: e.supports,
    })),
  };
  for (const d of node.descriptors) {
    const key = TERM_KEYS[d.slot] ?? d.slot;
    meta[key] = [
      ...((meta[key] as unknown[]) ?? []),
      { label: d.label ?? d.id },
    ];
  }
  return pathographTooltip({
    label: node.name,
    node_type:
      node.kind === "mechanism"
        ? (node.biological_scale?.toLowerCase() ?? "pathophysiology")
        : terminal
          ? "phenotype"
          : "sequela",
    description: node.description,
    meta,
    entityId: node.term_id ?? undefined,
    link: node.term_id ? `/${node.term_id}` : undefined,
  });
};

/**
 * merge the upstream causal subgraphs behind a set of dismech records into one
 * graph, so shared mechanism nodes render once
 */
export const mechanismGraph = (
  matches: DismechMatch[],
  nodes: Record<string, MechanismNode>,
) => {
  const terminals = new Set(matches.map((m) => m.phenotype_node_id));
  const edges = new Map<string, DagEdge>();
  for (const m of matches)
    for (const e of m.upstream_edges)
      edges.set(`${e.source}>${e.target}`, {
        source: e.source,
        target: e.target,
        linkType: e.link_type,
      });
  const ids = new Set([...edges.values()].flatMap((e) => [e.source, e.target]));
  const dagNodes: DagNode[] = [...ids].map((id) => {
    const node = nodes[id];
    const terminal = terminals.has(id);
    return {
      id,
      label: node?.name ?? id,
      kind:
        node?.kind === "mechanism"
          ? "mechanism"
          : terminal
            ? "phenotype"
            : "sequela",
      tooltip: nodeTooltip(nodes, id, terminal),
    };
  });
  return { nodes: dagNodes, edges: [...edges.values()] };
};

/**
 * a treatment's graph: the treatment, the mechanisms it targets (labeled with
 * its effect), the phenotypes downstream of them, and the phenotypes it treats
 */
export const treatmentGraph = (
  t: DismechTreatment,
  nodes: Record<string, MechanismNode>,
) => {
  const treated = new Set(t.target_phenotypes.map((p) => p.hpo_id));
  const edges = new Map<string, DagEdge>();
  const add = (e: DagEdge) => edges.set(`${e.source}>${e.target}`, e);
  for (const m of t.target_mechanisms)
    if (m.resolved)
      add({
        source: t.treatment_node_id,
        target: m.node_id,
        linkType: enumLabel(m.effect) || "Targets",
      });
  for (const e of t.edges)
    add({ source: e.source, target: e.target, linkType: e.link_type });
  const sources = new Set([...edges.values()].map((e) => e.source));
  const ids = new Set([...edges.values()].flatMap((e) => [e.source, e.target]));
  /** treated phenotypes the targets don't lead to hang off the treatment */
  const reached = new Set(
    [...ids].map((id) => nodes[id]?.term_id).filter(Boolean),
  );
  const extra: DagNode[] = t.target_phenotypes
    .filter((p) => !reached.has(p.hpo_id))
    .map((p) => {
      const id = `${t.treatment_node_id}>${p.hpo_id}`;
      add({ source: t.treatment_node_id, target: id, linkType: "Treats" });
      return { id, label: p.label || p.hpo_id, kind: "phenotype", focus: true };
    });
  const dagNodes: DagNode[] = [...ids]
    .filter((id) => id !== t.treatment_node_id)
    .map((id) => {
      const node = nodes[id];
      const terminal = node?.kind === "phenotype" && !sources.has(id);
      return {
        id,
        label: node?.name ?? id,
        kind:
          node?.kind === "mechanism"
            ? "mechanism"
            : terminal
              ? "phenotype"
              : "sequela",
        tooltip: nodeTooltip(nodes, id, terminal),
        focus: treated.has(node?.term_id ?? ""),
      };
    });
  return trimGraph(
    [
      {
        id: t.treatment_node_id,
        label: t.name,
        kind: "treatment",
        focus: true,
      },
      ...dagNodes,
      ...extra,
    ],
    [...edges.values()],
  );
};

/** "1 gene", "2 genes" */
export const plural = (count: number, noun: string) =>
  `${count.toLocaleString()} ${noun}${count === 1 ? "" : "s"}`;

/**
 * keep a mini graph readable: the nodes nearest the focus nodes, level by
 * level, until about `max` are kept. returns how many were left out.
 */
export const trimGraph = (
  nodes: DagNode[],
  edges: DagEdge[],
  max = 40,
): { nodes: DagNode[]; edges: DagEdge[]; hidden: number } => {
  if (nodes.length <= max) return { nodes, edges, hidden: 0 };
  const children = new Map<string, string[]>();
  for (const e of edges)
    children.set(e.source, [...(children.get(e.source) ?? []), e.target]);
  const focus = nodes.filter((n) => n.focus).map((n) => n.id);
  const keep = new Set(focus.length ? focus : [nodes[0].id]);
  let level = [...keep];
  while (level.length && keep.size < max) {
    const next = level
      .flatMap((id) => children.get(id) ?? [])
      .filter((id) => !keep.has(id));
    for (const id of next) if (keep.size < max) keep.add(id);
    level = next;
  }
  return {
    nodes: nodes.filter((n) => keep.has(n.id)),
    edges: edges.filter((e) => keep.has(e.source) && keep.has(e.target)),
    hidden: nodes.length - keep.size,
  };
};
