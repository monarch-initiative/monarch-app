export type BrandKey = "gard" | "omim" | "orphanet" | "medgen" | "nord";

export const BRAND_STYLES: Record<
  BrandKey,
  {
    label: string;
    bg: string;
    fg: string;
    hover: string;
    border: string;
  }
> = {
  gard: {
    label: "GARD",
    bg: "#7D6992",
    fg: "#FFFFFF",
    hover: "#6C5685",
    border: "#402F53",
  },
  omim: {
    label: "OMIM",
    bg: "#EC7C55",
    fg: "#FFFFFF",
    hover: "#E96B3F",
    border: "#A2401D",
  },
  orphanet: {
    label: "Orphanet",
    bg: "#338EC9",
    fg: "#FFFFFF",
    hover: "#1980C2",
    border: "#005083",
  },
  medgen: {
    label: "MedGen",
    bg: "#3C64A7",
    fg: "#FFFFFF",
    hover: "#23509C",
    border: "#082B66",
  },
  nord: {
    label: "NORD",
    bg: "#F58C4D",
    fg: "#FFFFFF",
    hover: "#F37D37",
    border: "#A94E17",
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
