/** Converts an ISO date string to a localized, readable date. */
export function formatReleaseDate(
  isoDate: string,
  locale: string = navigator.language || "en-US",
): string {
  const dt = new Date(isoDate);
  return new Intl.DateTimeFormat(locale, {
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(dt);
}
