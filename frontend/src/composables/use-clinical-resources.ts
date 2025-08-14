import { computed } from "vue";
import type { ExpandedCurie, Node } from "@/api/model";

const RESOURCE_DEFS = [
  {
    prefix: "OMIM:",
    label: "OMIM",
    tooltip:
      "A curated catalog of human genes, variants, and genetic phenotypes",
  },
  {
    prefix: "NORD:",
    label: "NORD",
    tooltip:
      "Lay-friendly rare disease summaries, advocacy resources, and support services",
  },
  {
    prefix: "GARD:",
    label: "GARD",
    tooltip: "Health information on genetic and rare conditions",
  },
  {
    prefix: "Orphanet:",
    label: "ORPHANET",
    tooltip:
      "European reference portal on rare diseases and orphan drugs with disease pages, epidemiology, coding, and expert centers",
  },
  {
    prefix: "MEDGEN:",
    label: "MEDGEN",
    tooltip:
      "NCBI’s structured knowledge base linking diseases, phenotypes, genes, and clinical resources",
  },
] as const;

const RESOURCE_PREFIXES = RESOURCE_DEFS.map((rec) => rec.prefix);

export type ResourceEntry = {
  id: string;
  url: string;
  label: string;
  source: "external" | "mapping";
  tooltip?: string;
};

export function useClinicalResources(node: Node) {
  const clinicalResources = computed<ResourceEntry[]>(() => {
    const out: ResourceEntry[] = [];
    for (const { prefix, label, tooltip } of RESOURCE_DEFS) {
      const ext = node.external_links?.find((l: ExpandedCurie) =>
        l.id.startsWith(prefix),
      );
      if (ext) {
        out.push({
          id: ext.id,
          url: ext.url || "",
          label,
          source: "external",
          tooltip,
        });
        continue;
      }
      const map = node.mappings?.find((item: ExpandedCurie) =>
        item.id.startsWith(prefix),
      );
      if (map) {
        out.push({
          id: map.id,
          url: map.url || "",
          label,
          source: "mapping",
          tooltip,
        });
      }
    }
    return out;
  });

  // Other mappings: exclude all clinical prefixes
  const otherMappings = computed(
    () =>
      node.mappings?.filter(
        (item) => !RESOURCE_PREFIXES.some((pre) => item.id.startsWith(pre)),
      ) || [],
  );

  // External references excluding clinical prefixes
  const externalRefs = computed<ExpandedCurie[]>(
    () =>
      node.external_links?.filter(
        (link) => !RESOURCE_PREFIXES.some((pre) => link.id.startsWith(pre)),
      ) || [],
  );
  return { clinicalResources, otherMappings, externalRefs };
}
