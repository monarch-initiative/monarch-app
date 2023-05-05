import { sortBy } from "lodash";
import { biolink, request } from "./";
import { categories, mapCategory } from "./categories";
import type { Gene } from "./genes";
import { getGene } from "./genes";
import { getPublication } from "./publications";
import { getXrefLink } from "./xrefs";

/** node lookup info (from backend) */
type _Node = {
  id: string;
  label: string;
  iri: string;
  category?: string[] | null;
  description: string | null;
  types: string[];
  inheritance?: {
    id: string;
    label: string;
    iri: string;
  }[];
  synonyms?: [
    {
      val: string;
      pred: string;
      xrefs: string[];
    }
  ];
  clinical_modifiers?: { label: string }[];
  deprecated: true;
  replaced_by: string[];
  consider: string[];
  taxon?: {
    id: string;
    label: string;
  };
  association_counts: {
    [key: string]: {
      counts?: number;
      counts_by_taxon?: number;
    };
  };
  xrefs: string[];
};

/** lookup metadata for a node id */
export const lookupNode = async (id = "", category = ""): Promise<Node> => {
  /** set flags */
  const params = {
    fetch_objects: false,
    unselect_evidence: true,
    exclude_automatic_assertions: true,
    use_compact_associations: false,
    get_association_counts: true /** missing in biolink docs, but essential */,
    rows: 1,
  };

  /** make query */
  const url = `${biolink}/bioentity/${category ? category + "/" : ""}${id}`;
  const response = await request<_Node>(url, params);

  /** convert into desired result format */
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
        /** don't include other facets */
        .filter(([, data]) => data.counts !== undefined)
        /** only include categories supported by app */
        .filter(([category]) => categories.includes(category))
        .map(([category, data]) => ({
          id: category || "",
          count: data.counts || 0,
          countByTaxon: data.counts_by_taxon,
        })),
      /** sort by specific order, and put unmatched at end */
      (category) => categories.indexOf(category.id) + 1 || Infinity
    ),
  };

  /** supplement gene with metadata from mygene */
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

  /** supplement publication with metadata from entrez */
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

/** node (for frontend). structure/order mirrors sections on node page. */
export type Node = {
  /** title section */
  id: string;
  originalId: string;
  name: string;
  category: string;

  /** overview section */
  synonyms: string[];
  description: string;

  /** details section */
  iri: string;
  inheritance: {
    id: string;
    name: string;
    link: string;
  }[];
  modifiers: string[];
  xrefs: {
    id: string;
    link: string;
  }[];

  /** details section (gene specific) */
  taxon?: {
    id?: string;
    name?: string;
    link?: string;
  };
  symbol?: string;
  genome?: Gene["genome"];

  /** details section (publication specific) */
  authors?: string[];
  date?: Date;
  doi?: string;
  journal?: string;

  /** associations section */
  associationCounts: {
    id: string;
    count: number;
    countByTaxon?: number;
  }[];
};
