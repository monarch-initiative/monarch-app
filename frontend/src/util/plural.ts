export const pluralize = (
  n?: number,
  singular = "subclass",
  plural = "subclasses",
  locale = "en",
): string => {
  const count = typeof n === "number" && Number.isFinite(n) ? n : 0;
  if (count === 0) return "";
  const isOne = new Intl.PluralRules(locale).select(Math.abs(count)) === "one";
  return `${count.toLocaleString(locale)} ${isOne ? singular : plural}`;
};
