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
