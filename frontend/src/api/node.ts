import { getPublication } from "@/api/publications";
import { monarch, request } from "./index";
import type { Node } from "./model";

export const getNode = async (id: string) => {
  const url = `${monarch}/entity/${id}`;
  const response = await request<Node>(url);

  const metadata: Metadata & Partial<typeof response> = {};

  /** supplement publication with metadata from entrez */
  if (response.category_label === "Publication") {
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

  const transformedResponse = {
    ...response,
    ...metadata,
  };

  return transformedResponse;
};

/** category-specific metadata */
type Metadata = {
  /** publication specific */
  authors?: string[];
  date?: Date;
  doi?: string;
  journal?: string;
};
