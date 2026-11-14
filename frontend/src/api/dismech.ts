import { apiUrl, request } from "./index";

/** one KG edge's contribution to a collapsed phenotype row */
export type PhenotypeObservation = {
  source: string;
  record?: string | null;
  frequency?: string | null;
  frequency_label?: string | null;
  percentage?: number | null;
  count?: number | null;
  total?: number | null;
  onset?: string | null;
  sex?: string | null;
  publications?: string[] | null;
  evidence?: string[] | null;
};

export type DismechEvidence = {
  reference: string;
  title?: string | null;
  supports?: string | null;
  source?: string | null;
  snippet?: string | null;
};

/** one edge of the causal subgraph upstream of a dismech phenotype */
export type MechanismEdge = {
  source: string;
  target: string;
  link_type?: string | null;
};

/** a dismech phenotype record attached to a row */
export type DismechMatch = {
  /**
   * same HP term as the row, a subclass of it, or no KG row at all
   * (dismech-only)
   */
  match: "exact" | "more_specific" | "dismech_only";
  hpo_id: string;
  hpo_label?: string | null;
  phenotype_name: string;
  mondo_id?: string | null;
  disorder: string;
  disorder_file: string;
  diagnostic: boolean;
  frequency_hp?: string | null;
  frequency_text?: string | null;
  evidence: DismechEvidence[];
  nearest_mechanisms: string[];
  /** this record's own node in the mechanism graph */
  phenotype_node_id: string;
  /** edges among every node that leads to this phenotype */
  upstream_edges: MechanismEdge[];
};

/**
 * one collapsed row: a phenotype of a disease (hpo_id set), or a disease with a
 * phenotype (disease_id set)
 */
export type PhenotypeProfileRow = {
  hpo_id?: string;
  disease_id?: string;
  label?: string | null;
  negated: boolean;
  /** consensus frequency estimate across KG sources (small counts discounted) */
  frequency_score?: number | null;
  sources: string[];
  observations: PhenotypeObservation[];
  dismech: DismechMatch[];
  /** no KG row; dismech is the only source */
  dismech_only: boolean;
};

export type MechanismNode = {
  kind: "mechanism" | "phenotype";
  name: string;
  /** HP id, for phenotype nodes */
  term_id?: string | null;
  description?: string | null;
  biological_scale?: string | null;
  frequency?: string | null;
  evidence: DismechEvidence[];
  descriptors: {
    slot: string;
    id: string;
    label?: string | null;
    modifier?: string | null;
  }[];
};

export type PhenotypeProfile = {
  id: string;
  /** dismech release the data was built from */
  release: string;
  /** rows after filtering, before paging */
  total: number;
  rows: PhenotypeProfileRow[];
  dismech_available: boolean;
  /** counts before filtering */
  kg_total: number;
  dismech_corroborated: number;
  dismech_unmatched: number;
  mechanism_nodes: Record<string, MechanismNode>;
};

export type ProfileOptions = {
  corroboratedOnly?: boolean;
  dismechOnly?: boolean;
  limit?: number;
  offset?: number;
};

export type TreatmentAgent = {
  id: string;
  label?: string | null;
  /** whether Monarch has a page for this agent */
  in_kg: boolean;
};

export type DismechTreatment = {
  mondo_id?: string | null;
  disorder: string;
  disorder_file: string;
  treatment_node_id: string;
  name: string;
  description?: string | null;
  modality?: string | null;
  action_category?: string | null;
  treatment_term_id?: string | null;
  treatment_term_label?: string | null;
  agents: TreatmentAgent[];
  target_mechanisms: {
    node_id: string;
    name: string;
    /** whether the target names a mechanism node in the disorder */
    resolved: boolean;
    effect?: string | null;
    description?: string | null;
    evidence: DismechEvidence[];
  }[];
  target_phenotypes: { hpo_id: string; label?: string | null }[];
  evidence: DismechEvidence[];
};

export type DismechTreatments = {
  id: string;
  release: string;
  rows: DismechTreatment[];
  mechanism_nodes: Record<string, MechanismNode>;
};

export type DismechMechanism = {
  mondo_id?: string | null;
  disorder: string;
  disorder_file: string;
  node_id: string;
  node_name: string;
  /** descriptor slots the term appears in, e.g. cell_types */
  slots: string[];
  modifier?: string | null;
  /** phenotypes downstream of this mechanism */
  leads_to: {
    hpo_id: string;
    hpo_label?: string | null;
    diagnostic: boolean;
  }[];
};

export type DismechMechanisms = {
  id: string;
  release: string;
  label?: string | null;
  rows: DismechMechanism[];
  mechanism_nodes: Record<string, MechanismNode>;
};

/**
 * experimental endpoints. on localhost they default to a locally running api
 * (it needs only dismech.duckdb, not solr), while the rest of the page keeps
 * using the deployed api. override with VITE_DISMECH_API.
 */
const base =
  import.meta.env.VITE_DISMECH_API ||
  (window.location.hostname === "localhost"
    ? "http://127.0.0.1:8000/v3/api"
    : apiUrl);

const profileParams = (options: ProfileOptions) => ({
  corroborated_only: options.corroboratedOnly ?? false,
  dismech_only: options.dismechOnly ?? false,
  ...(options.limit ? { limit: options.limit } : {}),
  offset: options.offset ?? 0,
});

/** a disease's phenotypes, collapsed across sources, with dismech corroboration */
export const getPhenotypeProfile = async (
  id: string,
  options: ProfileOptions = {},
): Promise<PhenotypeProfile> =>
  await request<PhenotypeProfile>(
    `${base}/dismech/phenotype-profile/${id}`,
    profileParams(options),
  );

/**
 * diseases with a phenotype, collapsed across sources, with dismech
 * corroboration
 */
export const getPhenotypeDiseases = async (
  id: string,
  options: ProfileOptions = {},
): Promise<PhenotypeProfile> =>
  await request<PhenotypeProfile>(
    `${base}/dismech/phenotype-diseases/${id}`,
    profileParams(options),
  );

/** dismech treatments for a disease, or the diseases a drug is used for */
export const getDismechTreatments = async (
  id: string,
): Promise<DismechTreatments> =>
  await request<DismechTreatments>(`${base}/dismech/treatments/${id}`);

/** dismech mechanisms annotated with an ontology term */
export const getDismechMechanisms = async (
  id: string,
): Promise<DismechMechanisms> =>
  await request<DismechMechanisms>(`${base}/dismech/mechanisms/${id}`);
