/**
 * Converts an ISO date string to a localized, readable date. Returns null if
 * value is missing or not parseable as a date.
 *
 * Formatted in UTC deliberately. The input is a calendar-date label -- a KG
 * release is "the 2026-09-04 release" everywhere, not an instant that falls on
 * different days in different places. `Date.parse` reads a date-only ISO string
 * as UTC midnight, so formatting it in the viewer's zone rendered the previous
 * day for everyone west of UTC: 2026-09-04 showed as September 3 across the
 * Americas. It looked correct to anyone in UTC or further east, which is why it
 * survived.
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
    timeZone: "UTC",
  }).format(new Date(parsedTime));
}
