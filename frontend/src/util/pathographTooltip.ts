/**
 * Hover tooltip markup for dismech pathograph nodes, shared by the full
 * pathograph and the per-phenotype mechanism graphs.
 */

/** what a tooltip needs from a node: pathograph nodes satisfy this as-is */
export type TooltipNode = {
  label: string;
  node_type: string;
  description?: string | null;
  meta?: Record<string, unknown> | null;
  /** ontology id displayed on the node, when it is itself an entity */
  entityId?: string;
  /** Monarch route for that entity */
  link?: string;
};

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
  { key: "cellular_components", label: "Cellular components" },
  { key: "chemical_entities", label: "Chemical entities" },
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

/**
 * Only allow relative or http(s) hrefs in the hand-built tooltip HTML — never a
 * javascript:/data: URI, even if the upstream artifact format ever changes.
 */
const safeHref = (href: string): string =>
  /^(\/|https?:\/\/)/i.test(href) ? href : "#";

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
export const pathographTooltip = (node: TooltipNode): string => {
  const meta = (node.meta || {}) as Record<string, unknown>;
  const parts: string[] = [
    `<div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.04em;opacity:0.65">${esc(prettyType(node.node_type))}</div>`,
    `<div style="font-weight:600;margin:1px 0 2px">${esc(node.label)}</div>`,
  ];
  if (node.entityId)
    parts.push(
      node.link
        ? `<div style="font-size:0.74rem;margin-bottom:4px"><a href="${esc(safeHref(node.link))}" target="_blank" rel="noopener noreferrer">${esc(node.entityId)} — open in Monarch ↗</a></div>`
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
