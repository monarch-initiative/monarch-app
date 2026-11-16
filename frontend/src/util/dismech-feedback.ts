import { truncate } from "lodash";
import type {
  DismechEvidence,
  MechanismEdge,
  MechanismNode,
} from "@/api/dismech";
import { dismechDisorderUrl } from "@/util/dismech";
import { collapse } from "@/util/string";

export type DismechFeedbackKind =
  | "phenotype"
  | "gene"
  | "treatment"
  | "mechanism";

/** a dismech record as shown on the page, for a feedback issue */
export type DismechFeedbackRecord = {
  kind: DismechFeedbackKind;
  /** the record's claim in a few words, e.g. Wilson disease: Jaundice */
  claim: string;
  disorder: string;
  disorder_file: string;
  release: string;
  /** what the record says, e.g. ["Frequency", "Very frequent"] */
  fields: [string, string][];
  evidence: DismechEvidence[];
  /** the mechanism chain shown with the record, as labeled edges */
  chain: { source: string; target: string }[];
  /** whether dismech marks the phenotype diagnostic */
  diagnostic?: boolean;
};

/**
 * one-click problems per record kind. a first draft, not a settled error
 * taxonomy: free text is always allowed, and the issue keeps the label
 * verbatim, so these can change without breaking anything downstream.
 */
export const FEEDBACK_REASONS: Record<DismechFeedbackKind, string[]> = {
  phenotype: [
    "Not a feature of this disease",
    "Frequency is wrong",
    "Shouldn't be diagnostic",
    "Wrong phenotype term",
    "Mechanism chain is wrong",
    "Evidence doesn't support it",
  ],
  gene: [
    "Gene isn't associated with this disease",
    "Wrong relationship (causal vs correlated)",
    "Wrong validity classification",
    "Mechanism is wrong",
    "Evidence doesn't support it",
  ],
  treatment: [
    "Not used for this disease",
    "Wrong mechanism target",
    "Wrong phenotypes treated",
    "Matched to the wrong drug",
    "Evidence doesn't support it",
  ],
  mechanism: [
    "Term doesn't apply to this mechanism",
    "Mechanism is wrong",
    "Leads to the wrong phenotypes",
    "Evidence doesn't support it",
  ],
};

/** the one-click problems that apply to a record */
export const reasonsFor = (record: DismechFeedbackRecord) =>
  FEEDBACK_REASONS[record.kind].filter(
    (r) => record.diagnostic || r !== "Shouldn't be diagnostic",
  );

export const KIND_LABELS: Record<DismechFeedbackKind, string> = {
  phenotype: "Phenotype",
  gene: "Gene",
  treatment: "Treatment",
  mechanism: "Disease mechanism",
};

/** largest chain sent in an issue; bigger ones link to the pathograph instead */
const MAX_CHAIN = 40;

/** a mechanism chain's edges, labeled with node names */
export const labeledChain = (
  edges: MechanismEdge[],
  nodes: Record<string, MechanismNode>,
) =>
  edges.map((e) => ({
    source: nodes[e.source]?.name ?? e.source,
    target: nodes[e.target]?.name ?? e.target,
  }));

/** a mermaid flowchart, which GitHub renders in the issue */
const mermaid = (chain: DismechFeedbackRecord["chain"]) => {
  const ids = new Map<string, string>();
  const node = (label: string) => {
    if (!ids.has(label)) ids.set(label, `n${ids.size}`);
    return `${ids.get(label)}["${label.replace(/"/g, "#quot;")}"]`;
  };
  return [
    "```mermaid",
    "flowchart TD",
    ...chain.map((e) => `  ${node(e.source)} --> ${node(e.target)}`),
    "```",
  ];
};

const evidenceLine = (e: DismechEvidence) => {
  const ref = e.reference.startsWith("PMID:")
    ? `[${e.reference}](https://pubmed.ncbi.nlm.nih.gov/${e.reference.slice(5)})`
    : e.reference;
  const supports = e.supports ? ` (${e.supports.toLowerCase()})` : "";
  return `- ${ref}${supports}${e.snippet ? `: "${collapse(e.snippet)}"` : ""}`;
};

/** helpdesk issue title and markdown body for feedback on a record */
export const feedbackIssue = (
  record: DismechFeedbackRecord,
  reasons: string[],
  comment: string,
  contact: { name: string; email: string; github: string },
  details: Record<string, string>,
) => {
  const title = [
    "Dismech feedback",
    KIND_LABELS[record.kind],
    truncate(record.claim, { length: 60 }),
    truncate(reasons.join(", ") || collapse(comment), { length: 60 }),
  ].join(" - ");

  const chain = record.chain.slice(0, MAX_CHAIN);
  const body = [
    `**Dismech ${KIND_LABELS[record.kind].toLowerCase()} record**: ${record.claim}`,
    "",
    `**Problem**: ${reasons.join("; ") || "(none selected)"}`,
    "",
    comment || "_No comment_",
    "",
    "### Record",
    "",
    "| | |",
    "|-|-|",
    `| Disorder | [${record.disorder}](${dismechDisorderUrl(record.disorder_file)}) |`,
    ...record.fields.map(([k, v]) => `| ${k} | ${v.replace(/\|/g, "\\|")} |`),
    `| Dismech release | ${record.release} |`,
    "",
    "### Evidence",
    "",
    ...(record.evidence.length
      ? record.evidence.map(evidenceLine)
      : ["_None cited_"]),
    "",
    ...(chain.length
      ? [
          "### Mechanism chain",
          "",
          ...mermaid(chain),
          ...(record.chain.length > MAX_CHAIN
            ? [`_${record.chain.length - MAX_CHAIN} more edges not shown_`]
            : []),
          "",
        ]
      : []),
    ...(contact.name || contact.email || contact.github
      ? [
          "### Reporter",
          "",
          `Name: ${contact.name}`,
          `Email: ${contact.email}`,
          `GitHub: ${contact.github}`,
          "",
        ]
      : []),
    "### Details",
    "",
    ...Object.entries(details).map(([key, value]) => `${key}: ${value}`),
  ].join("\n");

  return { title, body };
};
