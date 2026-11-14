import { computed } from "vue";
import { useRoute } from "vue-router";
import type { DismechMatch, MechanismNode } from "@/api/dismech";
import type { DagEdge, DagNode } from "@/pages/node/MechanismDag.vue";
import { pathographTooltip } from "@/util/pathographTooltip";

/**
 * experimental dismech integrations show only with ?dismech=1 (or the older
 * ?profile=1)
 */
export const useDismechPreview = () => {
  const route = useRoute();
  return computed(
    () => route.query.dismech === "1" || route.query.profile === "1",
  );
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
