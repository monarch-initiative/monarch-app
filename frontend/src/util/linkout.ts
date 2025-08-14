// Brand keys we support
export type BrandKey = "gard" | "omim" | "orphanet" | "medgen" | "nord";

// Very-near but NOT exact colors + safe font stacks (no brand fonts)
export const BRAND_STYLES: Record<
  BrandKey,
  {
    label: string;
    bg: string;
    fg: string;
    border: string;
    font: string;
    transform?: "uppercase" | "capitalize";
    letterSpacing?: string;
    weight?: number;
  }
> = {
  gard: {
    label: "GARD",
    bg: "#5C4377",
    fg: "#FFFFFF",
    border: "#49355F",
    font: "system-ui, Segoe UI, Roboto, Arial, sans-serif",
    transform: "uppercase",
    letterSpacing: "0.06em",
    weight: 800,
  },
  omim: {
    label: "OMIM",
    bg: "#fbc249ff",
    fg: "#ffffff",
    border: "#cc8a00",
    font: "Georgia, 'Times New Roman', Times, serif",
    transform: "uppercase",
    letterSpacing: "0.04em",
    weight: 700,
  },
  orphanet: {
    label: "Orphanet",
    bg: "#0072BB",
    fg: "#ffffff",
    border: "#004F84",
    font: "system-ui, Segoe UI, Roboto, Arial, sans-serif",
    transform: "capitalize",
    letterSpacing: "0.02em",
    weight: 700,
  },
  medgen: {
    label: "MedGen",
    bg: "#0B3D91",
    fg: "#FFFFFF",
    border: "#082E6B",
    font: "system-ui, Segoe UI, Roboto, Arial, sans-serif",
    weight: 700,
  },
  nord: {
    label: "NORD",
    bg: "#F26F21", // banner orange
    fg: "#FFFFFF", // white text
    border: "#D94F1C", // slightly darker orange
    font: "system-ui, Segoe UI, Roboto, Arial, sans-serif",
    transform: "uppercase",
    letterSpacing: "0.06em",
    weight: 900,
  },
};

export function brandFromId(id: string) {
  const prefix = id.split(":")[0]?.toUpperCase();
  switch (prefix) {
    case "GARD":
      return "gard";
    case "OMIM":
      return "omim";
    case "ORPHANET":
    case "ORPHA":
      return "orphanet";
    case "MEDGEN":
      return "medgen";
    case "NORD":
      return "nord";
    default:
      return null;
  }
}
