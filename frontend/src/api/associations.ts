import { monarch, request } from "./index";
import type { AssociationResults, SearchResults } from "./model";

import type { Filters, Query } from "./facets";
import { facetsToFilters, queryToParams } from "./facets";
import { getSummaries } from "./publications";
import type { Sort } from "@/components/AppTable.vue";


export const getAllAssociations = async (params: AssociationsParams): Promise<AssociationResults> => {
    // const sort = params.sort;
    // delete params.sort;
    const url = `${monarch}/association/all`;
    const response = await request<AssociationResults>(url, params);
    return response;
};


export const getTabulatedAssociations = async (
    nodeId = "",
    associationType = "",
    limit = 5,
    offset = 0,
    // search = "",
    // sort: Sort = null,
    // availableFilters: Query = {},
    // activeFilters: Query = {}
  ): Promise<AssociationResults> => {

    /** make query params */
    const params = {
      entity: nodeId,
      association_type: associationType,
      limit: limit,
      offset: offset+1,
    //   facet: true,
    //   q: search || null,
    //   sort: sort
    //     ? `${sort.id} ${sort.direction === "up" ? "asc" : "desc"}`
    //     : null,
    //   ...(await queryToParams(availableFilters, activeFilters)),
    };
    const url = `${monarch}/association/all`;
    const response = await request<AssociationResults>(url, params);
    return response;
  };
  

/** get top few associations */
export const getTopAssociations = async (
    nodeId = "",
    associationCategory = ""
  ): Promise<AssociationResults> => {
    return await getTabulatedAssociations(nodeId, associationCategory, 5);
};
/*******************
* Type definitions *
********************/

/** Allowed parameters for association queries */
type AssociationsParams = {
    entity?: string;
    association_type?: string;
    subject_closure?: string;
    object_closure?: string;
    between?: string;
    direct?: boolean;    
    offset?: number;
    limit?: number;
    // sort?: any;
    // search?: string;
    // facet?: boolean;
};

/** Association Type Mapping */
// disease_phenotype = "disease_phenotype"
// gene_phenotype = "gene_phenotype"
// gene_interaction = "gene_interaction"
// gene_pathway = "gene_pathway"
// gene_expression = "gene_expression"
// gene_orthology = "gene_orthology"
// chemical_pathway = "chemical_pathway"
// gene_function = "gene_function"
// correlated_gene = "correlated_gene"
// causal_gene = "causal_gene"

/** Function to map association types to valid values */
export const getAssociationType = (associationType: string): string => {
    switch (associationType.toLocaleLowerCase()) {
        case "phenotype":
            return "disease_phenotype";
        case "gene_phenotype":
            return "gene_phenotype";
        case "gene_interaction":
            return "gene_interaction";
        case "gene_pathway":
            return "gene_pathway";
        case "gene_expression":
            return "gene_expression";
        case "gene_orthology":
            return "gene_orthology";
        case "chemical_pathway":
            return "chemical_pathway";
        case "gene_function":
            return "gene_function";
        case "correlated_gene":
            return "correlated_gene";
        case "causal_gene":
            return "causal_gene";
        default:
            // return original lowercased
            return associationType.toLowerCase();
    }
};
