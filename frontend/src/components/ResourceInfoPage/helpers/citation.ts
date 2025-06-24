export function formatApaCitation(rawCitation: string): string {
  const trimmed = rawCitation.trim();

  if (/^Cite the GH repo/i.test(trimmed)) {
    const url = trimmed.split(":")[1]?.trim();
    const project =
      url?.split("/").pop()?.replace(/-/g, " ") || "GitHub Project";
    return `${capitalizeWords(project)}. (n.d.). Retrieved from ${url}`;
  }

  if (/^https?:\/\//.test(trimmed)) {
    const url = new URL(trimmed);
    return `${url.hostname.replace("www.", "")}. (n.d.). Retrieved from ${trimmed}`;
  }

  if (/doi|PMID|PMCID|[A-Z][a-z]+ J[a-z]*\./.test(trimmed)) {
    return trimmed.endsWith(".") ? trimmed : trimmed + ".";
  }

  return `(n.d.). ${trimmed}`;
}

function capitalizeWords(str: string): string {
  return str.replace(/\b\w/g, (char) => char.toUpperCase());
}
