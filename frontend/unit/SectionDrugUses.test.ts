import { beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises } from "@vue/test-utils";
import type {
  AssociationSummary,
  AssociationSummaryParams,
} from "@/api/association-summary";
import { mount } from "./setup";

const APPROVED_FILTER = /^predicate:\(/;

const summary = (over: Partial<AssociationSummary>): AssociationSummary => ({
  total: 0,
  group_by: "",
  group_total: 0,
  offset: 0,
  limit: 0,
  unique: {},
  facets: {},
  groups: [],
  ...over,
});

/**
 * one disease with two approved drugs and one drug used only off-label: the tab
 * counts are 2 with the approved-only filter and 3 without it
 */
const getAssociationSummary = vi.fn(
  async (_id: string, _section: string, params: AssociationSummaryParams) => {
    const approvedOnly = (params.filterQueries ?? []).some((f) =>
      APPROVED_FILTER.test(f),
    );
    if (params.groupBy === "predicate")
      return summary({
        groups: [
          {
            value: "biolink:treats",
            count: 2,
            unique: {},
            stats: {},
            fields: {},
            facets: {},
          },
          {
            value: "biolink:applied_to_treat",
            count: 1,
            unique: {},
            stats: {},
            fields: {},
            facets: {},
          },
        ],
      });
    if (params.groupBy === "medic_jurisdiction")
      return summary({
        groups: [
          {
            value: "USA",
            count: 2,
            unique: { subject: 2 },
            stats: {},
            fields: {},
            facets: {},
          },
        ],
      });
    if (params.groupBy === "grouping_key")
      return summary({
        group_total: 1,
        groups: [
          {
            value: "CHEBI:3||biolink:applied_to_treat|MONDO:1",
            count: 1,
            unique: {},
            stats: {},
            fields: {
              predicate: "biolink:applied_to_treat",
              object: "MONDO:1",
              object_label: "test disease",
            },
            facets: {},
          },
        ],
      });
    const n = approvedOnly ? 2 : 3;
    return summary({
      total: n,
      group_total: n,
      unique: { grouping_key: n },
      groups: [
        {
          value: "CHEBI:3",
          count: 1,
          unique: { grouping_key: 1, object: 1 },
          stats: {},
          fields: {
            subject_label: "off-label drug",
            subject_category: "biolink:Drug",
          },
          facets: {
            object: [{ value: "MONDO:1", count: 1, label: "test disease" }],
          },
        },
      ],
    });
  },
);

/** a CURE ID record: no supporting text, only the case report's PMID */
const getAssociations = vi.fn(async () => ({
  items: [
    {
      id: "a1",
      subject: "CHEBI:3",
      predicate: "biolink:applied_to_treat",
      object: "MONDO:1",
      primary_knowledge_source: "infores:cureid",
      agent_type: "manual_agent",
      knowledge_level: "knowledge_assertion",
      publications: ["PMID:19804494"],
    },
  ],
  total: 1,
  limit: 200,
  offset: 0,
}));

vi.mock("@/api/association-summary", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/api/association-summary")>()),
  getAssociationSummary: (...args: Parameters<typeof getAssociationSummary>) =>
    getAssociationSummary(...args),
}));
vi.mock("@/api/associations", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/api/associations")>()),
  getAssociations: () => getAssociations(),
}));

const node = {
  id: "MONDO:1",
  name: "test disease",
  category: "biolink:Disease",
};

/** the gate's state is module-level, so each test mounts a fresh copy */
const mountSection = async () => {
  vi.resetModules();
  const { default: SectionDrugUses } =
    await import("@/pages/node/SectionDrugUses.vue");
  const wrapper = mount(SectionDrugUses, {
    props: { node, sectionKey: "drug_indications", sectionLabel: "Treatments" },
  });
  await flushPromises();
  return wrapper;
};

beforeEach(() => {
  window.sessionStorage.clear();
  getAssociationSummary.mockClear();
  getAssociations.mockClear();
});

describe("SectionDrugUses", () => {
  it("shows only the notice, and fetches nothing, until acknowledged", async () => {
    const wrapper = await mountSection();
    expect(wrapper.find(".notice").exists()).toBe(true);
    expect(wrapper.find(".content").exists()).toBe(false);
    expect(getAssociationSummary).not.toHaveBeenCalled();

    await wrapper.find(".acknowledge").trigger("click");
    await flushPromises();
    expect(wrapper.find(".acknowledge").exists()).toBe(false);
    expect(getAssociationSummary).toHaveBeenCalled();
    expect(wrapper.findAll(".group").length).toBe(1);
  });

  it("shows every drug when the disease has only investigational uses", async () => {
    // the section's only predicate is applied_to_treat, so the approved-only
    // default doesn't apply and the section isn't left empty
    getAssociationSummary.mockImplementationOnce(async () =>
      summary({
        groups: [
          {
            value: "biolink:applied_to_treat",
            count: 1,
            unique: {},
            stats: {},
            fields: {},
            facets: {},
          },
        ],
      }),
    );
    window.sessionStorage.setItem(
      "drug-sections-research-use-acknowledged",
      "true",
    );
    const wrapper = await mountSection();
    const filtered = getAssociationSummary.mock.calls.some(([, , params]) =>
      (params.filterQueries ?? []).some((f) => APPROVED_FILTER.test(f)),
    );
    expect(filtered).toBe(false);
    expect(wrapper.find(".overview").text()).toContain("3 drugs");
  });

  it("counts the drugs '+ investigational' would add", async () => {
    window.sessionStorage.setItem(
      "drug-sections-research-use-acknowledged",
      "true",
    );
    const wrapper = await mountSection();
    // 3 drugs without the approved-only filter, 2 with it
    expect(wrapper.find(".overview").text()).toContain("2 drugs");
    const chip = wrapper
      .findAll(".chip")
      .find((c) => c.text().includes("investigational"));
    expect(chip?.text()).toContain("1");
    expect(chip?.attributes("aria-pressed")).toBe("false");
  });

  it("links the publication when an assertion has no supporting text", async () => {
    window.sessionStorage.setItem(
      "drug-sections-research-use-acknowledged",
      "true",
    );
    const wrapper = await mountSection();
    await wrapper.find(".group-row .expand").trigger("click");
    await flushPromises();
    await wrapper.find(".statement-row .expand").trigger("click");
    await flushPromises();
    const text = wrapper.find(".assertion .supporting");
    expect(text.text()).toContain("Reported in PMID:19804494");
    expect(text.find("a").attributes("href")).toBe(
      "https://pubmed.ncbi.nlm.nih.gov/19804494",
    );
    expect(wrapper.text()).not.toContain("(no text)");
  });
});
