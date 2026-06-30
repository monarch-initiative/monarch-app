import { apiUrl, request } from "./index";

export type PathographNode = {
  /** stable merged id (anchor curie, or <mondo>::<name> when disorder-local) */
  id: string;
  label: string;
  node_type: string;
  color?: string | null;
  is_orphan: boolean;
  description?: string | null;
  meta?: Record<string, unknown> | null;
  /** mondo ids of the disorders contributing this node */
  sources: string[];
};

export type PathographEdge = {
  source: string;
  target: string;
  predicate?: string | null;
  description?: string | null;
  sources: string[];
};

export type PathographSource = {
  /** mondo id */
  id: string;
  name: string;
  /** direct link to this disorder's dismech page, when available */
  url?: string | null;
};

export type Pathograph = {
  node_id: string;
  category: "disease" | "gene";
  nodes: PathographNode[];
  edges: PathographEdge[];
  sources: PathographSource[];
};

/**
 * Get the dismech pathograph for a disease (MONDO) or gene (HGNC) node. The
 * backend returns 404 (→ thrown error) when no pathograph exists for the node.
 */
export const getPathograph = async (id: string): Promise<Pathograph> => {
  const url = `${apiUrl}/pathograph/${id}`;
  return await request<Pathograph>(url);
};
