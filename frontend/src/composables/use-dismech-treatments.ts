import { computed, ref, watch } from "vue";
import type { Ref } from "vue";
import { getAssociationSummary } from "@/api/association-summary";
import { getDismechTreatments } from "@/api/dismech";
import type { DismechTreatment, DismechTreatments } from "@/api/dismech";
import type { Node } from "@/api/model";
import { useDismech } from "@/util/dismech";

/** whole-word, case-insensitive match of a drug label in a treatment's text */
const mentions = (text: string | null | undefined, label: string) => {
  if (!text || label.length < 3) return false;
  const escaped = label.toLowerCase().replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return new RegExp(`\\b${escaped}\\b`).test(text.toLowerCase());
};

/**
 * dismech treatments for a drug section (indications): on a disease page, the
 * disease's treatments matched to drug rows; on a drug page, the diseases the
 * drug treats matched to condition rows. Treatments matching no row in the
 * whole section (not just the current page) are dismech-only.
 */
export const useDismechTreatments = (
  node: Ref<Node>,
  sectionKey: Ref<string>,
  isDiseasePage: Ref<boolean>,
  acknowledged: Ref<boolean>,
) => {
  const dismech = useDismech();
  const enabled = computed(
    () => dismech.value && sectionKey.value === "drug_indications",
  );

  const data = ref<DismechTreatments>({
    id: "",
    release: "",
    rows: [],
    mechanism_nodes: {},
  });
  /** every row id and label in the section, for dismech-only */
  const sectionRows = ref<{ id: string; label: string }[]>([]);

  /** does a treatment match a section row (a drug, or a condition)? */
  const matches = (t: DismechTreatment, id: string, label?: string | null) =>
    isDiseasePage.value
      ? t.agents.some((a) => a.id === id) ||
        (!!label &&
          (mentions(t.name, label) ||
            t.agents.some((a) => mentions(a.label, label))))
      : t.mondo_id === id;

  const forRow = (id: string, label?: string | null) =>
    enabled.value ? data.value.rows.filter((t) => matches(t, id, label)) : [];

  const unmatched = computed(() =>
    enabled.value
      ? data.value.rows.filter(
          (t) => !sectionRows.value.some((r) => matches(t, r.id, r.label)),
        )
      : [],
  );

  /** every drug / condition in the section, a page (the API's max) at a time */
  const loadSectionRows = async () => {
    const side = isDiseasePage.value ? "subject" : "object";
    const rows: { id: string; label: string }[] = [];
    for (let offset = 0; ; offset += 500) {
      const summary = await getAssociationSummary(
        node.value.id,
        sectionKey.value,
        { groupBy: side, labelFields: [`${side}_label`], offset, limit: 500 },
      );
      rows.push(
        ...summary.groups.map((g) => ({
          id: g.value,
          label: String(g.fields[`${side}_label`] ?? ""),
        })),
      );
      if (offset + 500 >= summary.group_total) return rows;
    }
  };

  const load = async () => {
    if (!enabled.value || !acknowledged.value) return;
    data.value = await getDismechTreatments(
      node.value.id,
      isDiseasePage.value ? undefined : node.value.name,
    );
    sectionRows.value = await loadSectionRows();
  };

  watch(
    () => [node.value.id, enabled.value, acknowledged.value],
    () => {
      data.value = { id: "", release: "", rows: [], mechanism_nodes: {} };
      sectionRows.value = [];
      load().catch(() => {
        /* dismech is an enrichment: the section still works without it */
      });
    },
    { immediate: true },
  );

  return { enabled, data, forRow, unmatched };
};
