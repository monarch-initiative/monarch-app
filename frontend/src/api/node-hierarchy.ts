import { uniqBy } from "lodash";
import type { Association } from "@/api/node-associations";
import { biolink, request } from "./";
import { mapCategory } from "./categories";

/** graph info to construct hierarchy (from backend) */
type _Hierarchy = {
  nodes: [
    {
      id: string;
      lbl: string;
      meta?: {
        category?: string[];
      };
    }
  ];
  edges: [
    {
      sub: string;
      pred: string;
      obj: string;
    }
  ];
};

/** "part of" relationship type */
const partOf = "BFO:0000050";

/** super/equivalent/sub-class relations */
const superRelation: Association["relation"] = {
  id: "",
  name: "is super class of",
  iri: "",
  category: "",
  inverse: true,
};
const equivalentRelation: Association["relation"] = {
  id: "",
  name: "is equivalent class of",
  iri: "",
  category: "",
  inverse: true,
};
const subRelation: Association["relation"] = {
  id: "",
  name: "is subclass of",
  iri: "",
  category: "",
  inverse: true,
};

/** lookup hierarchy info for a node id */
export const getHierarchy = async (
  id = "",
  category = ""
): Promise<Hierarchy> => {
  const superClasses: Class[] = [];
  const equivalentClasses: Class[] = [];
  const subClasses: Class[] = [];

  /** make query params */
  const params = {
    relationship_type: ["disease", "phenotype", "anatomy", "function"].includes(
      category
    )
      ? /** only do subclass and "part of" for certain node types */
        ["equivalentClass", "subClassOf", partOf]
      : /** otherwise just look for equivalent classes */
        "equivalentClass",
  };

  /** make query */
  const url = `${biolink}/graph/edges/from/${id}`;
  const response = await request<_Hierarchy>(url, params);
  const { nodes, edges } = response;

  /** take id of subject or object and find associated node label */
  const idToClass = (id = "", relation: Association["relation"]): Class => {
    const matchingNode = nodes.find((node) => node.id === id);

    return {
      id,
      name: matchingNode?.lbl || "",
      category: mapCategory(matchingNode?.meta?.category),
      relation,
    };
  };

  /** populate super/equivalent/sub classes */
  for (const { sub, pred, obj } of edges) {
    if (pred === "subClassOf" || pred === partOf) {
      if (sub === id) {
        superClasses.push(idToClass(obj, superRelation));
      } else if (obj === id) {
        subClasses.push(idToClass(sub, subRelation));
      }
    } else if (pred === "equivalentClass") {
      if (sub === id) {
        equivalentClasses.push(idToClass(obj, equivalentRelation));
      } else {
        equivalentClasses.push(idToClass(sub, equivalentRelation));
      }
    }
  }

  return {
    superClasses: uniqBy(superClasses, "id"),
    equivalentClasses: uniqBy(equivalentClasses, "id"),
    subClasses: uniqBy(subClasses, "id"),
  };
};

type Class = {
  id: string;
  name: string;
  category: string;
  relation: Association["relation"];
};

/** hierarchy (for frontend) */
export type Hierarchy = {
  superClasses: Class[];
  equivalentClasses: Class[];
  subClasses: Class[];
};
