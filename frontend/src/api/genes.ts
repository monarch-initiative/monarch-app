import { request } from ".";

/**
 * map our id prefixes to prefixes that mygene expects
 * http://docs.mygene.info/en/latest/doc/data.html#species
 * http://docs.mygene.info/en/latest/doc/query_service.html#available-fields
 */
const map: Record<string, { replace: string; species: string }> = {
  "NCBIGene:": { replace: "", species: "all" },
  "OMIM:": { replace: "mim:", species: "9606" },
  "MGI:": { replace: "mgi:MGI\\:", species: "10090" },
  "FlyBase:": { replace: "flybase:", species: "7227" },
  "Wormbase:": { replace: "wormbase:", species: "6239" },
  "ZFIN:": { replace: "zfin:", species: "7955" },
  "RGD:": { replace: "rgd:", species: "10116" },
};

/** gene (from backend) */
interface _Gene {
  hits: Array<{
    name: string;
    summary: string;
    symbol: string;
    taxid: number;
    genomic_pos: {
      chr: string;
      start: number;
      end: number;
      ensemblgene: string;
      strand: number;
    };
  }>;
}

/** get metadata of gene from mygene */
export const getGene = async (id = ""): Promise<Gene> => {
  /** format id for mygene */
  const prefix = (id.split(":")[0] || "") + ":";
  const { replace = prefix, species = "all" } = map[prefix] || {};
  id = id.replace(prefix, replace);

  /** make query */
  const params = {
    q: id,
    fields: "summary,genomic_pos,name,symbol,taxid",
    species,
  };
  const url = "https://mygene.info/v3/query";
  const { hits } = await request<_Gene>(url, params);

  /** take first result */
  const hit = hits[0] || {};

  /** convert into desired result format */
  return {
    name: hit.name || "",
    description: hit.summary || "",
    symbol: hit.symbol || "",
    genome: hit.genomic_pos || {},
  };
};

/** gene (for frontend) */
export interface Gene {
  name: string;
  description: string;
  symbol: string;
  genome?: {
    chr: string;
    start: number;
    end: number;
    strand: number;
    ensemblgene: string;
  };
}
