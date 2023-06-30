import { kebabCase, startCase } from "lodash";

/** get human-readable label from category */
export const getCategoryLabel = (category?: string | string[]) =>
  startCase(
    (Array.isArray(category) ? category[0] : category)?.replace(
      "biolink:",
      ""
    ) || ""
  );

/** get icon name from category */
export const getCategoryIcon = (category?: string) =>
  "category-" + kebabCase(category?.replace("biolink:", "") || "");
