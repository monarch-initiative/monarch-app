/** possible properties of a source on the sources page */
export interface Source {
  id?: string;
  name?: string;
  type?: "dataset" | "ontology";
  link?: string;
  license?: string;
  distribution?: string;
  date?: string;
  image?: string;
  description?: string;
  usage?: string;
  vocabulary?: string;
  files?: Array<string>;
}
