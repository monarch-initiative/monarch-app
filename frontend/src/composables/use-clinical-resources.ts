// src/composables/useClinicalResources.ts
import { computed } from "vue";
import type { ExpandedCurie, Node } from "@/api/model";

const RESOURCE_DEFS = [
  { prefix: "OMIM:", label: "OMIM" },
  { prefix: "NORD:", label: "NORD" },
  { prefix: "GARD:", label: "GARD" },
  { prefix: "Orphanet:", label: "ORPHANET" },
  { prefix: "MEDGEN:", label: "MEDGEN" },
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
    for (const { prefix, label } of RESOURCE_DEFS) {
      const ext = node.external_links?.find((l: ExpandedCurie) =>
        l.id.startsWith(prefix),
      );
      if (ext) {
        out.push({ id: ext.id, url: ext.url || "", label, source: "external" });
        continue;
      }
      const map = node.mappings?.find((item: ExpandedCurie) =>
        item.id.startsWith(prefix),
      );
      if (map) {
        out.push({ id: map.id, url: map.url || "", label, source: "mapping" });
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
