import { beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises } from "@vue/test-utils";
import type {
  DismechMatch,
  PhenotypeProfile,
  PhenotypeProfileRow,
} from "@/api/dismech";
import PhenotypeProfileTable from "@/pages/node/PhenotypeProfileTable.vue";
import { mount } from "./setup";

const record = (over: Partial<DismechMatch> = {}): DismechMatch => ({
  match: "more_specific",
  hpo_id: "HP:0001394",
  hpo_label: "Cirrhosis",
  phenotype_name: "Cirrhosis",
  mondo_id: "MONDO:0010200",
  disorder: "Wilson Disease",
  disorder_file: "Wilson_Disease",
  diagnostic: true,
  frequency_hp: "HP:0040281",
  evidence: [{ reference: "PMID:1", snippet: "copper in the liver" }],
  nearest_mechanisms: ["Copper"],
  phenotype_node_id: "dismech:Wilson_Disease#Cirrhosis",
  upstream_edges: [
    {
      source: "dismech:Wilson_Disease#Copper",
      target: "dismech:Wilson_Disease#Cirrhosis",
    },
  ],
  ...over,
});

const row = (over: Partial<PhenotypeProfileRow> = {}): PhenotypeProfileRow => ({
  disease_id: "MONDO:0010200",
  label: "Wilson disease",
  negated: false,
  sources: ["infores:omim"],
  observations: [],
  dismech: [],
  dismech_only: false,
  ...over,
});

const profile = (over: Partial<PhenotypeProfile> = {}): PhenotypeProfile => ({
  id: "",
  release: "v0.1.47",
  total: 1,
  rows: [row()],
  dismech_available: true,
  kg_total: 1,
  dismech_corroborated: 0,
  dismech_unmatched: 0,
  mechanism_nodes: {},
  ...over,
});

const getPhenotypeProfile = vi.fn<
  unknown[],
  Promise<ReturnType<typeof profile>>
>(async () => profile());
const getPhenotypeDiseases = vi.fn<
  unknown[],
  Promise<ReturnType<typeof profile>>
>(async () => profile());

vi.mock("@/api/dismech", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/api/dismech")>()),
  getPhenotypeProfile: (...args: unknown[]) => getPhenotypeProfile(...args),
  getPhenotypeDiseases: (...args: unknown[]) => getPhenotypeDiseases(...args),
}));
// the graph's layout isn't under test here
vi.mock("@/pages/node/MechanismDag.vue", () => ({
  default: {
    name: "MechanismDag",
    props: ["nodes", "edges"],
    template: "<div class='dag' />",
  },
}));

const LIVER_ORGAN = {
  id: "UBERON:0002107",
  name: "liver",
  category: "biolink:GrossAnatomicalStructure",
};
const WILSON = {
  id: "MONDO:0010200",
  name: "Wilson disease",
  category: "biolink:Disease",
};

const lastOptions = (fn: typeof getPhenotypeDiseases) =>
  (fn.mock.calls.at(-1) as unknown[])[1] as Record<string, unknown>;

beforeEach(() => {
  getPhenotypeProfile.mockReset();
  getPhenotypeProfile.mockImplementation(async () => profile());
  getPhenotypeDiseases.mockReset();
  getPhenotypeDiseases.mockImplementation(async () => profile());
});

describe("PhenotypeProfileTable", () => {
  it("asks for a disease's phenotypes on a disease page", async () => {
    mount(PhenotypeProfileTable, { props: { node: WILSON } });
    await flushPromises();
    expect(getPhenotypeProfile).toHaveBeenCalledWith(
      "MONDO:0010200",
      expect.objectContaining({ offset: 0, dismechOnly: false }),
    );
    expect(getPhenotypeDiseases).not.toHaveBeenCalled();
  });

  it.each(["HP:0001392", "UPHENO:0002443", "UBERON:0002107", "GO:0008152"])(
    "asks for the diseases under %s on any other page",
    async (id) => {
      mount(PhenotypeProfileTable, {
        props: { node: { ...LIVER_ORGAN, id } },
      });
      await flushPromises();
      expect(getPhenotypeDiseases).toHaveBeenCalledWith(id, expect.anything());
      expect(getPhenotypeProfile).not.toHaveBeenCalled();
    },
  );

  it("starts with dismech-only rows shown when asked to", async () => {
    mount(PhenotypeProfileTable, {
      props: { node: WILSON, dismechOnly: true },
    });
    await flushPromises();
    expect(lastOptions(getPhenotypeProfile).dismechOnly).toBe(true);
  });

  it("sends the section's search, and refetches from the first page when it changes", async () => {
    getPhenotypeDiseases.mockImplementation(async () =>
      profile({
        total: 30,
        rows: Array.from({ length: 10 }, (_, i) =>
          row({ disease_id: `MONDO:${i}` }),
        ),
      }),
    );
    const wrapper = mount(PhenotypeProfileTable, {
      props: { node: LIVER_ORGAN, search: "" },
    });
    await flushPromises();
    expect(lastOptions(getPhenotypeDiseases).search).toBe("");

    // move off the first page, then search
    await wrapper.find("[aria-label='Go to next page']").trigger("click");
    await flushPromises();
    expect(lastOptions(getPhenotypeDiseases).offset).toBe(10);

    await wrapper.setProps({ search: "cirrhosis" });
    await flushPromises();
    expect(lastOptions(getPhenotypeDiseases)).toMatchObject({
      search: "cirrhosis",
      offset: 0,
    });
  });

  it("refetches with the dismech filters", async () => {
    getPhenotypeDiseases.mockImplementation(async () =>
      profile({ kg_total: 2, dismech_corroborated: 1, dismech_unmatched: 3 }),
    );
    const wrapper = mount(PhenotypeProfileTable, {
      props: { node: LIVER_ORGAN },
    });
    await flushPromises();
    const checkboxes = () => wrapper.findAll("input[type='checkbox']");
    await checkboxes()[0]!.setValue(true);
    await flushPromises();
    expect(lastOptions(getPhenotypeDiseases).corroboratedOnly).toBe(true);
    // the table re-renders while it refetches
    await checkboxes()[1]!.setValue(true);
    await flushPromises();
    expect(lastOptions(getPhenotypeDiseases).dismechOnly).toBe(true);
  });

  it("names the subclasses a disease is annotated with, matching ones first, and caps them", async () => {
    const terms = [
      "Hepatic fibrosis",
      "Hepatic steatosis",
      "Hepatomegaly",
      "Jaundice",
      "Cirrhosis",
    ];
    getPhenotypeDiseases.mockImplementationOnce(async () =>
      profile({
        rows: [
          row({
            observations: terms.map((label, i) => ({
              source: "infores:omim",
              phenotype: `HP:000000${i}`,
              phenotype_label: label,
              count: 1,
              total: 2,
            })),
          }),
        ],
      }),
    );
    const wrapper = mount(PhenotypeProfileTable, {
      props: { node: LIVER_ORGAN, search: "cirrh" },
    });
    await flushPromises();
    const text = wrapper.text();
    expect(text).toContain(
      "with Cirrhosis, Hepatic fibrosis, Hepatic steatosis and 2 more",
    );
    // frequencies name their term, three at most
    expect(text).toContain("1/2 (50%) (Hepatic fibrosis)");
    expect(text).toContain("and 2 more");
  });

  it("doesn't name the page's own term as a subclass", async () => {
    getPhenotypeDiseases.mockImplementationOnce(async () =>
      profile({
        rows: [
          row({
            observations: [
              {
                source: "infores:omim",
                phenotype: "HP:0001392",
                phenotype_label: "Abnormality of the liver",
                percentage: 40,
              },
            ],
          }),
        ],
      }),
    );
    const wrapper = mount(PhenotypeProfileTable, {
      props: { node: { ...LIVER_ORGAN, id: "HP:0001392" } },
    });
    await flushPromises();
    expect(wrapper.text()).not.toContain("with Abnormality");
    expect(wrapper.text()).toContain("OMIM 40%");
  });

  it("marks dismech corroboration and expands to its graph, evidence and feedback", async () => {
    getPhenotypeDiseases.mockImplementationOnce(async () =>
      profile({
        dismech_corroborated: 1,
        rows: [row({ dismech: [record()] })],
      }),
    );
    const wrapper = mount(PhenotypeProfileTable, {
      props: { node: LIVER_ORGAN },
    });
    await flushPromises();
    expect(wrapper.find(".chip.dismech").exists()).toBe(true);
    expect(wrapper.find(".badge.diagnostic").exists()).toBe(true);
    expect(wrapper.find(".detail").exists()).toBe(false);

    await wrapper.find("tbody button").trigger("click");
    expect(wrapper.find(".detail .dag").exists()).toBe(true);
    expect(wrapper.find(".detail").text()).toContain(
      "Dismech records the more specific",
    );
    expect(wrapper.find(".detail").text()).toContain("copper in the liver");
    expect(wrapper.find(".detail").text()).toContain("Report a problem");
  });

  it("says when a disease has phenotypes from dismech only", async () => {
    getPhenotypeProfile.mockImplementationOnce(async () =>
      profile({
        kg_total: 0,
        dismech_unmatched: 2,
        rows: [
          row({
            hpo_id: "HP:0001394",
            disease_id: undefined,
            sources: [],
            dismech_only: true,
            dismech: [record({ match: "dismech_only" })],
          }),
        ],
      }),
    );
    const wrapper = mount(PhenotypeProfileTable, {
      props: { node: WILSON, dismechOnly: true },
    });
    await flushPromises();
    expect(wrapper.text()).toContain("2 phenotypes from Dismech only");
    expect(wrapper.text()).toContain("Dismech Very frequent");
  });
});
