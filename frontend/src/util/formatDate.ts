/** Converts an ISO date string to a localized, readable date. */
export function formatReleaseDate(
  isoDate: string,
  locale: string = navigator.language || "en-US",
): string {
  if (!isoDate || typeof isoDate !== 'string') {
    return `Invalid date: ${isoDate}`;
  }
  
  const dt = new Date(isoDate);
  
  // Check if date is valid
  if (isNaN(dt.getTime())) {
    return `Invalid date: ${isoDate}`;
  }
  
  return new Intl.DateTimeFormat(locale, {
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(dt);
}
