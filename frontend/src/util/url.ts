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

/** https://stackoverflow.com/a/54520829/9878785 */
type KeysMatching<T, V> = {
  [K in keyof T]-?: T[K] extends V ? K : never;
}[keyof T];
