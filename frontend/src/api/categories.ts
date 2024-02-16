import { kebabCase, mapKeys, startCase } from "lodash";

/** get human-readable label from category */
export const getCategoryLabel = (category?: string | string[]) =>
  startCase(
    (Array.isArray(category) ? category[0] : category)?.replace(
      "biolink:",
      "",
    ) || "",
  );

/** get icon name from category */
export const getCategoryIcon = (category?: string) =>
  "category-" + kebabCase(category?.replace("biolink:", "") || "");

/**
 * color palette
 *
 * professionally curated, do not edit, only add or remove
 *
 * https://github.com/tailwindlabs/tailwindcss/blob/master/src/public/colors.js
 */
const colors = {
  slate: "#64748b",
  red: {
    light: "#f87171",
    mid: "#ef4444",
    dark: "#dc2626",
  },
  orange: {
    light: "#fb923c",
    mid: "#f97316",
    dark: "#ea580c",
  },
  amber: {
    light: "#fbbf24",
    mid: "#f59e0b",
    dark: "#d97706",
  },
  yellow: {
    light: "#facc15",
    mid: "#eab308",
    dark: "#ca8a04",
  },
  lime: {
    light: "#a3e635",
    mid: "#84cc16",
    dark: "#65a30d",
  },
  green: {
    light: "#4ade80",
    mid: "#22c55e",
    dark: "#16a34a",
  },
  emerald: {
    light: "#34d399",
    mid: "#10b981",
    dark: "#059669",
  },
  teal: {
    light: "#2dd4bf",
    mid: "#14b8a6",
    dark: "#0d9488",
  },
  cyan: {
    light: "#22d3ee",
    mid: "#06b6d4",
    dark: "#0891b2",
  },
  sky: {
    light: "#38bdf8",
    mid: "#0ea5e9",
    dark: "#0284c7",
  },
  blue: {
    light: "#60a5fa",
    mid: "#3b82f6",
    dark: "#2563eb",
  },
  indigo: {
    light: "#818cf8",
    mid: "#6366f1",
    dark: "#4f46e5",
  },
  violet: {
    light: "#a78bfa",
    mid: "#8b5cf6",
    dark: "#7c3aed",
  },
  purple: {
    light: "#c084fc",
    mid: "#a855f7",
    dark: "#9333ea",
  },
  fuchsia: {
    light: "#e879f9",
    mid: "#d946ef",
    dark: "#c026d3",
  },
  pink: {
    light: "#f472b6",
    mid: "#ec4899",
    dark: "#db2777",
  },
  rose: {
    light: "#fb7185",
    mid: "#f43f5e",
    dark: "#e11d48",
  },
};

/**
 * roughly grouped by similar concepts (to keep similar colors clustered).
 * groups roughly sorted in order of subjective importance.
 */
const colorMap: { [key: string]: string } = mapKeys(
  {
    "biolink:Gene": colors.sky.dark,

    "biolink:PhenotypicFeature": colors.emerald.dark,
    "biolink:PhenotypicQuality": colors.emerald.dark,
    "biolink:PathologicalProcess": colors.emerald.dark,
    "biolink:BehavioralFeature": colors.emerald.dark,

    "biolink:Disease": colors.pink.dark,

    "biolink:MolecularEntity": colors.lime.dark,
    "biolink:CellularComponent": colors.lime.dark,
    "biolink:BiologicalProcess": colors.lime.dark,
    "biolink:BiologicalProcessOrActivity": colors.lime.dark,
    "biolink:Pathway": colors.lime.dark,
    "biolink:MolecularActivity": colors.lime.dark,

    "biolink:GrossAnatomicalStructure": colors.cyan.dark,
    "biolink:Cell": colors.cyan.dark,

    "biolink:ChemicalEntity": colors.violet.dark,
    "biolink:Drug": colors.violet.dark,

    "biolink:AnatomicalEntity": colors.fuchsia.dark,
    "biolink:LifeStage": colors.fuchsia.dark,

    "biolink:CellularOrganism": colors.amber.dark,
    "biolink:Vertebrate": colors.amber.dark,

    "biolink:MacromolecularComplex": colors.red.dark,
    "biolink:Protein": colors.red.dark,
    "biolink:Virus": colors.red.dark,
  },
  (_, key) => getCategoryIcon(key),
);

/** get color from category icon name */
export const getCategoryColor = (icon: string) =>
  icon ? colorMap[icon] || colors.slate : colors.slate;
