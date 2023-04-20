import type { Sort } from "@/components/AppTable.vue";
import { biolink, request } from "./";
import { getAssociationEndpoint, mapCategory } from "./categories";
import type { Filters, Query } from "./facets";
import { facetsToFilters, queryToParams } from "./facets";
import { getSummaries } from "./publications";
import { getXrefLink } from "./xrefs";

/** Node associations (from backend) */
type _Associations = {
  numFound: number;
  associations: Array<{
    id: string;
    type?: string;
    subject: {
      id: string;
      label: string;
      iri: string;
      category?: Array<string> | null;
      taxon: {
        id: null;
        label: null;
      };
    };
    object: {
      id: string;
      label: string;
      iri: string;
      category?: Array<string> | null;
      taxon?: {
        id: null;
        label: null;
      };
    };
    relation: {
      id: string;
      label: string;
      iri: string;
      category?: Array<string> | null;
      inverse: boolean;
    };
    evidence_types?: Array<{
      id: string;
      label: string;
    }>;
    provided_by?: Array<string>;
    publications?: Array<{
      id: string;
      label: string;
    }>;
    frequency?: {
      id?: string;
      label?: string;
    };
    onset?: {
      id?: string;
      label?: string;
    };
  }>;
  facet_counts: Record<string, Record<string, number>>;
}

/** Get associations between a node and a category */
export const getTabulatedAssociations = async (
  nodeId = "",
  nodeCategory = "",
  associationCategory = "",
  rows = 10,
  start = 0,
  search = "",
  sort: Sort = null,
  availableFilters: Query = {},
  activeFilters: Query = {}
): Promise<Associations> => {
  /** Get causal/correlated param */
  let type = "both";
  if (associationCategory.startsWith("causal-")) type = "causal";
  if (associationCategory.startsWith("correlated-")) type = "non_causal";

  /** Make query params */
  const params = {
    rows,
    start,
    association_type: type,
    facet: true,
    q: search || null,
    sort: sort
      ? `${sort.id} ${sort.direction === "up" ? "asc" : "desc"}`
      : null,
    ...(await queryToParams(availableFilters, activeFilters)),
  };

  /** Make query */
  const url = `${biolink}/bioentity/${nodeCategory}/${nodeId}/${getAssociationEndpoint(
    associationCategory
  )}`;
  const response = await request<_Associations>(url, params);

  /** Convert into desired result format */
  const associations: Associations["associations"] = response.associations.map(
    (association) =>
      ({
        id: association.id,

        object: {
          id: association.object.id,
          name: association.object.label,
          iri: association.object.iri,
          category: mapCategory(association.object.category || []),
        },

        subject: {
          id: association.subject.id,
          name: association.subject.label,
          iri: association.subject.iri,
          category: mapCategory(association.subject.category || []),
        },

        relation: {
          id: association.relation.id,
          name: association.relation.label,
          iri: association.relation.iri,
          category: (association.relation?.category || [])[0] || "",
          inverse: association.relation.inverse,
        },

        evidence: [],

        taxon:
          association.object.taxon?.id || association.object.taxon?.label
            ? {
                id: association.object.taxon?.id || "",
                name: association.object.taxon?.label || "",
              }
            : undefined,

        frequency:
          association.frequency?.id || association.frequency?.label
            ? {
                name: association.frequency?.label || "",
                link: getXrefLink(association.frequency?.id || ""),
              }
            : undefined,
        onset:
          association.onset?.id || association.onset?.label
            ? {
                name: association.onset?.label || "",
                link: getXrefLink(association.onset?.id || ""),
              }
            : undefined,

        supportCount:
          (association.evidence_types || []).length +
          (association.publications || []).filter((publication) =>
            publication.id.startsWith("PMID:")
          ).length +
          (association.provided_by || []).length,
      } as Association)
  );

  /** Supplement publication with metadata from entrez */
  try {
    /** Get list of publication ids */
    const ids = associations
      .filter((association) => association.object.category === "publication")
      .map((association) => association.object.id);

    /** Get summaries for all ids at same time */
    const summaries = await getSummaries(ids);

    for (const [id, publication] of Object.entries(summaries)) {
      /** Find original association */
      const association = associations.find(
        (association) => association.object.id === id
      );
      if (!association) continue;

      /** Incorporate response data back into associations */
      association.author = publication.authors[0] || "";
      association.year = String(publication.date?.getFullYear() || "");
      association.publisher = publication.journal;
    }
  } catch (error) {
    console.warn("Couldn't get publication-specific metadata");
  }

  /** Get facets for filters */
  const facets = facetsToFilters(response.facet_counts);

  return { count: response.numFound || 0, associations, facets };
};

/** Single association */
export type Association = {
  /** Allow arbitrary key access */
  [key: string]: unknown;

  /** Unique id of association */
  id: string;

  /** Subject of association, i.e. current node */
  subject: {
    id: string;
    name: string;
    iri: string;
    category: string;
  };

  /** Object of association, i.e. what current node has association with */
  object: {
    id: string;
    name: string;
    iri: string;
    category: string;
  };

  /** Info about the association */
  relation: {
    id: string;
    name: string;
    iri: string;
    category: string;
    inverse: boolean;
  };

  /** Evidence info supporting this association */
  evidence: Array<Record<string, unknown>>;

  /** Mixed-type total of pieces of supporting evidence */
  supportCount: number;

  /** Taxon/species (gene/genotype/model/variant/homolog/ortholog) */
  taxon?: {
    id: string;
    name: string;
  };

  /** Phenotype frequency */
  frequency?: {
    name: string;
    link: string;
  };
  /** Phenotype onset */
  onset?: {
    name: string;
    link: string;
  };

  /** Publication author */
  author?: string;
  /** Publication year */
  year?: string;
  /** Publication publisher */
  publisher?: string;
}

/** Node associations (for frontend) */
export type Associations = {
  count: number;
  associations: Array<Association>;

  facets: Filters;
}

/** Get top few associations */
export const getTopAssociations = async (
  nodeId = "",
  nodeCategory = "",
  associationCategory = ""
): Promise<Associations["associations"]> =>
  (await getTabulatedAssociations(nodeId, nodeCategory, associationCategory, 5))
    .associations;
