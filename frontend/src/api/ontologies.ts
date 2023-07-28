import { mergeArrays } from "@/util/object";
import { request } from "./";
import staticData from "./ontologies.json";
import type { Source } from "./source";

/** source for ontology metadata */
export const obo = "https://obofoundry.org/registry/ontologies.jsonld";

/** knowledge graph ontologies (from backend) */
type _Ontologies = {
  ontologies: {
    id: string;
    title?: string;
    homepage?: string;
    license?: { url?: string };
    depicted_by?: string;
    description?: string;
  }[];
};

/** get metadata of all ontologies listed on obo */
export const getOntologies = async (): Promise<Ontologies> => {
  const response = await request<_Ontologies>(obo);

  /** convert results to desired format */
  let ontologies = response.ontologies.map(
    (ontology): Source => ({
      id: ontology.id,
      name: ontology.title,
      link: ontology.homepage,
      license: ontology.license?.url,
      image: ontology.depicted_by,
      description: ontology.description,
    }),
  );

  /**
   * merge static (manually entered) data in with dynamic (fetched) data (but
   * only including entries in static)
   */
  ontologies = mergeArrays(staticData, ontologies, true);

  /** tag as ontology type of source */
  ontologies.forEach((ontology) => (ontology.type = "ontology"));

  return ontologies;
};

/** knowledge graph ontologies (for frontend) */
type Ontologies = Source[];
