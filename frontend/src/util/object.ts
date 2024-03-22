import { merge } from "lodash";

/** object with id field */
type Obj = { id?: string };

/** merge two arrays of objects by id */
export const mergeArrays = (
  arrayA: Obj[],
  arrayB: Obj[],
  /** only include entries that are in array A */
  exclusive = false,
): Obj[] => {
  /** store to keep id-deduped list of entries */
  const result: { [key: string]: Obj } = {};

  /** merge func */
  const mergeWithResult =
    (add = true) =>
    (object: Obj) => {
      const { id = "" } = object;
      /** if add flag true, or entry already in store, add to store */
      if (add || result[id])
        /** deep merge array entry with store entry using lodash */
        result[id] = merge(result[id] || {}, object);
    };

  /** run merge func for each array */
  arrayA.forEach(mergeWithResult(true));
  arrayB.forEach(mergeWithResult(!exclusive));

  /** convert object back to array */
  return Object.values(result);
};

/** rename key in object in place */
export const renameKey = (
  object: { [key: string]: unknown },
  oldKey: string,
  newKey: string,
): void => {
  if (object[oldKey]) {
    object[newKey] = object[oldKey];
    delete object[oldKey];
  }
};

/** safe json stringify */
export const stringify = (value: unknown, space = 0) => {
  try {
    if (!value) return "";
    else return JSON.stringify(value, null, space);
  } catch (error) {
    console.warn("Invalid JSON stringify");
    console.debug(value);
    console.debug(error);
    return "";
  }
};

/** safe json parse */
export const parse = <Type>(value: string, defaultValue: Type) => {
  try {
    if (!value) return defaultValue;
    else return JSON.parse(value) as Type;
  } catch (error) {
    console.warn("Invalid JSON parse");
    console.debug(value);
    console.debug(error);
    return defaultValue;
  }
};
