/** is url absolute (as opposed to relative) */
export const isAbsolute = (url = ""): boolean =>
  ["http:", "https:", "ftp:", "mailto:"].some((prefix) =>
    url.startsWith(prefix)
  );

/** is url outside of monarch domain */
export const isExternal = (url = ""): boolean =>
  isAbsolute(url) && !getDomain(url).endsWith("monarchinitiative.org");

/** get domain of url */
const getDomain = (url = ""): string => {
  try {
    return new URL(url).hostname;
  } catch (error) {
    return "";
  }
};
