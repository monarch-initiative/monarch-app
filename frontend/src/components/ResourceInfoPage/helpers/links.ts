export function formatLabel(label: string): string {
  return label.replace(/_/g, " ").replace(/^\w/, (c) => c.toUpperCase());
}

export function normalizeResourceLinks(raw: Record<string, any>) {
  const seen = new Set<string>();
  const links: { key: string; value: string }[] = [];

  const add = (key: string, url: string) => {
    if (url && !seen.has(url)) {
      links.push({ key, value: url });
      seen.add(url);
    }
  };

  if (raw.website) add("website", raw.website);

  Object.keys(raw)
    .filter((k) => k !== "website" && k !== "other")
    .sort()
    .forEach((k) => {
      const urls = Array.isArray(raw[k]) ? raw[k] : [raw[k]];
      urls.forEach((url) => typeof url === "string" && add(k, url.trim()));
    });

  const other = raw.other;
  (Array.isArray(other) ? other : [other]).forEach(
    (url) => typeof url === "string" && add("other", url.trim()),
  );

  return links;
}
