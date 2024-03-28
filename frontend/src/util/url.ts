import init, {Converter, getOboConverter, getBioregistryConverter} from "@biopragmatics/curies";

/** is url absolute (as opposed to relative) */
export const isAbsolute = (url = ""): boolean =>
  ["http:", "https:", "ftp:", "mailto:"].some((prefix) =>
    url.startsWith(prefix),
  );

/** is url outside of monarch domain */
export const isExternal = (url = ""): boolean =>
  isAbsolute(url) && !getUrl(url, "hostname").endsWith("monarchinitiative.org");

/** safely get part of url */
export const getUrl = (
  url: string,
  part: KeysMatching<URL, string>,
): string => {
  try {
    return new URL(url)[part];
  } catch (error) {
    return "";
  }
};

/** https://stackoverflow.com/questions/54520676/in-typescript-how-to-get-the-keys-of-an-object-type-whose-values-are-of-a-given */
type KeysMatching<T, V> = {
  [K in keyof T]-?: T[K] extends V ? K : never;
}[keyof T];

const curieMap: Record<string, string> = {
    "MONDO": "http://purl.obolibrary.org/obo/MONDO_",
    "HP": "http://purl.obolibrary.org/obo/HP_",
    "GO": "http://purl.obolibrary.org/obo/GO_",
    "CL": "http://purl.obolibrary.org/obo/CL_",
    "OMIM": "http://purl.obolibrary.org/obo/OMIM_",
    "NCIT": "http://purl.obolibrary.org/obo/NCIT_",
    "DOID": "http://purl.obolibrary.org/obo/DOID_",
    "Orphanet": "http://purl.obolibrary.org/obo/Orphanet_",
}

//@ts-expect-error
let curieConverter;

export async function initCurieConverter() {
    //@ts-ignore
    await init();
    curieConverter = await Converter.fromExtendedPrefixMap("https://raw.githubusercontent.com/biopragmatics/bioregistry/main/exports/contexts/bioregistry.epm.json")
}

export function expandCurie(curie: string | undefined): string  {
    if (!curie) {
        return "";
    }

    //@ts-expect-error
    return curieConverter.expand(curie);
}

export const expand = (curie: string): string => {
    if (!curie.includes(":")) {
        return curie;
    }
    const [prefix, id] = curie.split(":");
    if (!curieMap[prefix]) {
        return curie;
    }
    return curieMap[prefix] + id;
}
