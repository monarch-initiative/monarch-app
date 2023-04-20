import { sortBy } from "lodash";
import { biolink, request } from "./";
import { categories, mapCategory } from "./categories";
import type { Gene } from "./genes";
import { getGene } from "./genes";
import { getPublication } from "./publications";
import { getXrefLink } from "./xrefs";

/** Node lookup info (from backend) */
type _Node = {
  id: string;
  label: string;
  iri: string;
  category?: Array<string> | null;
  description: string | null;
  types: Array<string>;
  inheritance?: Array<{
    id: string;
    label: string;
    iri: string;
  }>;
  synonyms?: [
    {
      val: string;
      pred: string;
      xrefs: Array<string>;
    }
  ];
  clinical_modifiers?: Array<{ label: string }>;
  deprecated: true;
  replaced_by: Array<string>;
  consider: Array<string>;
  taxon?: {
    id: string;
    label: string;
  };
  association_counts: Record<
    string,
    {
      counts?: number;
      counts_by_taxon?: number;
    }
  >;
  xrefs: Array<string>;
}

/** Lookup metadata for a node id */
export const lookupNode = async (id = "", category = ""): Promise<Node> => {
  /** Set flags */
  const params = {
    fetch_objects: false,
    unselect_evidence: true,
    exclude_automatic_assertions: true,
    use_compact_associations: false,
    get_association_counts: true /** Missing in biolink docs, but essential */,
    rows: 1,
  };

  /** Make query */
  const url = `${biolink}/bioentity/${category ? category + "/" : ""}${id}`;
  const response = await request<_Node>(url, params);

  /** Convert into desired result format */
  const metadata: Node = {
    id: response.id,
    originalId: id,
    name: response.label,
    category: mapCategory(response.category || []),

    synonyms: (response.synonyms || []).map(({ val }) => val),
    description: response.description || "",

    iri: response.iri,
    inheritance: (response.inheritance || []).map(({ id, label, iri }) => ({
      id,
      name: label,
      link: iri,
    })),
    modifiers: (response.clinical_modifiers || []).map(({ label }) => label),
    xrefs: response.xrefs.map((id) => ({ id, link: getXrefLink(id) })),

    taxon: {
      id: response.taxon?.id || "",
      name: response.taxon?.label || "",
      link: getXrefLink(response.taxon?.id || ""),
    },

    associationCounts: sortBy(
      Object.entries(response.association_counts || {})
        /** Don't include other facets */
        .filter(([, data]) => data.counts !== undefined)
        /** Only include categories supported by app */
        .filter(([category]) => categories.includes(category))
        .map(([category, data]) => ({
          id: category || "",
          count: data.counts || 0,
          countByTaxon: data.counts_by_taxon,
        })),
      /** Sort by specific order, and put unmatched at end */
      (category) => categories.indexOf(category.id) + 1 || Infinity
    ),
  };

  /** Supplement gene with metadata from mygene */
  if (category === "gene" || category === "variant") {
    try {
      const gene = await getGene(id);
      metadata.description = gene.description;
      metadata.symbol = gene.symbol;
      metadata.genome = gene.genome;
    } catch (error) {
      console.warn("Couldn't load gene-specific metadata");
    }
  }

  /** Supplement publication with metadata from entrez */
  if (category === "publication") {
    try {
      const publication = await getPublication(id);
      metadata.name = publication.title;
      metadata.description = publication.abstract;
      metadata.authors = publication.authors;
      metadata.date = publication.date;
      metadata.doi = publication.doi;
      metadata.journal = publication.journal;
    } catch (error) {
      console.warn("Couldn't load publication-specific metadata");
    }
  }

  return metadata;
};

/** Node (for frontend). structure/order mirrors sections on node page. */
export type Node = {
  /** Title section */
  id: string;
  /** Title section */
  originalId: string;
  /** Title section */
  name: string;
  /** Title section */
  category: string;

  /** Overview section */
  synonyms: Array<string>;
  /** Overview section */
  description: string;

  /** Details section */
  iri: string;
  /** Details section */
  inheritance: Array<{
    id: string;
    name: string;
    link: string;
  }>;
  /** Details section */
  modifiers: Array<string>;
  /** Details section */
  xrefs: Array<{
    id: string;
    link: string;
  }>;

  /** Details section (gene specific) */
  taxon?: {
    id?: string;
    name?: string;
    link?: string;
  };
  /** Details section (gene specific) */
  symbol?: string;
  /** Details section (gene specific) */
  genome?: Gene["genome"];

  /** Details section (publication specific) */
  authors?: Array<string>;
  /** Details section (publication specific) */
  date?: Date;
  /** Details section (publication specific) */
  doi?: string;
  /** Details section (publication specific) */
  journal?: string;

  /** Associations section */
  associationCounts: Array<{
    id: string;
    count: number;
    countByTaxon?: number;
  }>;
}
