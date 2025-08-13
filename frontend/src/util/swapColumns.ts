export const swapCols = <T extends string>(
  cols: Array<{ key?: T }>,
  a: T,
  b: T,
) => {
  const iA = cols.findIndex((c) => c.key === a);
  const iB = cols.findIndex((c) => c.key === b);
  if (iA < 0 || iB < 0) return cols;
  const next = cols.slice();
  [next[iA], next[iB]] = [next[iB], next[iA]];
  return next;
};
