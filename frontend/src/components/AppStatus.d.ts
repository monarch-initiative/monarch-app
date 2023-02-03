/** possible status codes */
export const Codes = [
  "loading",
  "success",
  "warning",
  "error",
  "paused",
  "unknown",
] as const;

export type Code = typeof Codes[number];
