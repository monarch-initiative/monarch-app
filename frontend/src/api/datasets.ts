import { mergeArrays } from "@/util/object";
import { biolink, request } from "./";
import staticData from "./datasets.json";
import type { Source } from "./source";
import { getXrefLink } from "./xrefs";

/** knowledge graph datasets (from backend) */
type _Datasets = {
  nodes: {
    id: string;
    meta: {
      "http://purl.org/dc/terms/created": string[];
    };
  }[];
  edges: {
    sub: string;
    obj: string;
    pred: string;
  }[];
};

/**
 * get metadata of all datasets used in monarch from biolink, in format of
 * source
 */
export const getDatasets = async (): Promise<Datasets> => {
  /** make query */
  const url = `${biolink}/metadata/datasets`;
  const { nodes, edges } = await request<_Datasets>(url);

  const filteredNodes = edges
    /** only get edges whose type is a dataset */
    .filter((edge) => edge.pred === "dc:isVersionOf")
    /** find corresponding node by id */
    .map((edge) => nodes.find((node) => node.id === edge.sub))
    /** filter out any un-found nodes */
    .filter((node) => node) as _Datasets["nodes"];

  /** convert results to desired format */
  let datasets = filteredNodes.map(
    (node): Source => ({
      id:
        edges.find((edge) => edge.obj === node.id && edge.pred === "versionIRI")
          ?.sub || "",
      date: node.meta["http://purl.org/dc/terms/created"][0],
      distribution: getXrefLink(
        edges.find(
          (edge) => edge.sub === node.id && edge.pred === "dcat:distribution",
        )?.obj || "",
      ),
      files: edges
        .filter((edge) => edge.sub === node.id && edge.pred === "dc:source")
        .map((edge) => getXrefLink(edge.obj)),
    }),
  );

  /** merge static (manually entered) data in with dynamic (fetched) data */
  datasets = mergeArrays(staticData, datasets);

  /** tag as dataset type of source */
  datasets.forEach((dataset) => (dataset.type = "dataset"));

  return datasets;
};

/** knowledge graph datasets (for frontend) */
type Datasets = Source[];
