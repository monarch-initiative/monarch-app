import { mapKeys, mapValues } from "lodash";
import { request } from "./";

/** entrez endpoint for getting publication metadata */
const entrez = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils";

/** get metadata of publication from entrez */
export const getPublication = async (id = ""): Promise<Publication> => {
  const summary = (await getSummaries([id]))[id];
  const abstract = await getAbstract(id);

  return { ...summary, abstract };
};

/** publication summary info (from backend) */
interface _Summary {
  result: {
    [key: string]: {
      uid: string;
      pubdate: string;
      epubdate: string;
      source: string;
      authors: Array<{ name: string }>;
      title: string;
      volume: string;
      issue: string;
      pages: string;
      lang: Array<string>;
      issn: string;
      essn: string;
      pubtype: Array<string>;
      articleids: Array<{ idtype: string; value: string }>;
      fulljournalname: string;
      elocationid: string;
      doctype: string;
      medium: string;
      edition: string;
      publishername: string;
    };
  };
}

/** get summary information of publication(s) from entrez */
export const getSummaries = async (ids: Array<string>): Promise<Summaries> => {
  /** strip prefix as entrez expects */
  ids = ids
    .map((id) => id.replace("PMID:", ""))
    .map((id) => id.trim())
    .filter((id) => id);

  if (!ids.length) return {};

  /** make query */
  const params = { db: "pubmed", retmode: "json", id: ids.join(",") };
  const url = `${entrez}/esummary.fcgi`;
  const { result } = await request<_Summary>(url, params);

  /** convert into desired result format */
  let publications = mapValues(result, (publication) => ({
    id: publication.uid,
    title: publication.title,
    authors: (publication.authors || []).map(({ name }) => name),
    date: new Date(publication.epubdate),
    doi:
      (publication.articleids || []).find(({ idtype }) => idtype === "doi")
        ?.value || "",
    journal: publication.fulljournalname,
  }));

  publications = mapKeys(publications, (value, key) => "PMID:" + key);

  return publications;
};

/** get abstract text of publication from entrez */
export const getAbstract = async (id = ""): Promise<Abstract> => {
  /** strip prefix as entrez expects */
  id = id.replace("PMID:", "");

  /** make query */
  const params = { db: "pubmed", retmode: "text", rettype: "abstract", id };
  const url = `${entrez}/efetch.fcgi`;
  return await request<string>(url, params, {}, "text");
};

interface Summaries {
  [key: string]: {
    id: string;
    title: string;
    authors: Array<string>;
    date: Date;
    doi: string;
    journal: string;
  };
}

type Abstract = string;

/** publication (for frontend) */
interface Publication {
  id: string;
  title: string;
  authors: Array<string>;
  date: Date;
  doi: string;
  journal: string;
  abstract: string;
}
