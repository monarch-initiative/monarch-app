export const pluralize = (
  n?: number,
  singular = "subclass",
  plural = "subclasses",
  locale = "en",
): string => {
  const c = typeof n === "number" && Number.isFinite(n) ? n : 0;
  if (c === 0) return ""; // show nothing for zero/undefined
  const isOne = new Intl.PluralRules(locale).select(Math.abs(c)) === "one";
  return `${c.toLocaleString(locale)} ${isOne ? singular : plural}`;
};
