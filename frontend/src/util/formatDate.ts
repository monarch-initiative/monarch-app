/**
 * Converts an ISO date string to a localized, readable date. Returns null if
 * value is missing or not parseable as a date.
 */
export function formatReleaseDate(
  isoDate: string | null | undefined,
  locale: string = navigator.language || "en-US",
): string | null {
  if (!isoDate) return null;
  const parsedTime = Date.parse(isoDate);
  if (Number.isNaN(parsedTime)) return null;
  return new Intl.DateTimeFormat(locale, {
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(new Date(parsedTime));
}
