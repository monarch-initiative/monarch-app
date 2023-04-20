import { mergeArrays } from "@/util/object";
import { request } from "./";
import staticData from "./ontologies.json";
import type { Source } from "./source";

/** Source for ontology metadata */
export const obo = "https://obofoundry.org/registry/ontologies.jsonld";

/** Knowledge graph ontologies (from backend) */
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

/** Get metadata of all ontologies listed on obo */
export const getOntologies = async (): Promise<Ontologies> => {
  const response = await request<_Ontologies>(obo);

  /** Convert results to desired format */
  let ontologies = response.ontologies.map(
    (ontology): Source => ({
      id: ontology.id,
      name: ontology.title,
      link: ontology.homepage,
      license: ontology.license?.url,
      image: ontology.depicted_by,
      description: ontology.description,
    })
  );

  /**
   * Merge static (manually entered) data in with dynamic (fetched) data (but
   * only including entries in static)
   */
  ontologies = mergeArrays(staticData, ontologies, true);

  /** Tag as ontology type of source */
  ontologies.forEach((ontology) => (ontology.type = "ontology"));

  return ontologies;
};

/** Knowledge graph ontologies (for frontend) */
type Ontologies = Source[];
