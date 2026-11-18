/**
 * which table a node page's association section uses when the api serves
 * dismech, and what the section hands it. the dismech tables replace the stock
 * (solr) table, so the section's own controls have to reach them.
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises } from "@vue/test-utils";
import type { Node } from "@/api/model";
import router from "@/router";
import { mount } from "./setup";

const getDismechStatus = vi.fn(async () => ({ release: "v0.1.47" }));
const getPhenotypeProfile = vi.fn<
  unknown[],
  Promise<{ kg_total: number; dismech_unmatched: number }>
>(async () => ({
  kg_total: 5,
  dismech_unmatched: 2,
}));

vi.mock("@/api/dismech", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/api/dismech")>()),
  getDismechStatus: () => getDismechStatus(),
  getPhenotypeProfile: (...args: unknown[]) => getPhenotypeProfile(...args),
}));

/** each table as a marker carrying its props */
const stub = (name: string) => ({
  default: {
    name,
    props: ["node", "category", "direct", "search", "kind", "dismechOnly"],
    template: `<div class="${name}" :data-search="search" :data-kind="kind" :data-dismech-only="dismechOnly" />`,
  },
});
// like the real table, reports its direct/all totals, which pick a disease's default tab
vi.mock("@/pages/node/AssociationsTable.vue", () => ({
  default: {
    ...stub("AssociationsTable").default,
    emits: ["totals"],
    mounted(this: { $emit: (e: string, p: unknown) => void }) {
      this.$emit("totals", { direct: 5, all: 10 });
    },
  },
}));
vi.mock("@/pages/node/PhenotypeProfileTable.vue", () =>
  stub("PhenotypeProfileTable"),
);
vi.mock("@/pages/node/GeneDiseaseTable.vue", () => stub("GeneDiseaseTable"));
vi.mock("@/pages/node/SectionPathograph.vue", () => stub("SectionPathograph"));
vi.mock("@/pages/node/SectionTermDiseases.vue", () =>
  stub("SectionTermDiseases"),
);
vi.mock("@/pages/node/SectionCasePhenotypeGrid.vue", () =>
  stub("SectionCasePhenotypeGrid"),
);

const D2P = "biolink:DiseaseToPhenotypicFeatureAssociation";
const CAUSAL = "biolink:CausalGeneToDiseaseAssociation";

const node = (id: string, category: string, sections: string[]): Node =>
  ({
    id,
    name: id,
    category,
    association_counts: sections.map((s) => ({
      key: s,
      category: s,
      label: s,
      count: 10,
      count_with_orthologs: 10,
    })),
  }) as unknown as Node;

/** dismech availability is asked once per page load, so each test loads afresh */
const mountSection = async (n: Node) => {
  vi.resetModules();
  const { default: SectionAssociations } =
    await import("@/pages/node/SectionAssociations.vue");
  const wrapper = mount(SectionAssociations, { props: { node: n } });
  await flushPromises();
  return wrapper;
};

beforeEach(async () => {
  getDismechStatus.mockReset();
  getDismechStatus.mockImplementation(async () => ({ release: "v0.1.47" }));
  getPhenotypeProfile.mockClear();
  await router.push("/");
});

describe("SectionAssociations with dismech", () => {
  it.each([
    ["HP:0001392", "biolink:PhenotypicFeature"],
    ["UPHENO:0002443", "biolink:PhenotypicFeature"],
    ["UBERON:0002107", "biolink:GrossAnatomicalStructure"],
    ["GO:0008152", "biolink:BiologicalProcess"],
  ])("uses the collapsed disease table on %s", async (id, category) => {
    const wrapper = await mountSection(node(id, category, [D2P]));
    expect(wrapper.find(".PhenotypeProfileTable").exists()).toBe(true);
    expect(wrapper.find(".AssociationsTable").exists()).toBe(false);
  });

  it("uses the collapsed phenotype table on a disease's direct tab", async () => {
    const wrapper = await mountSection(
      node("MONDO:0010200", "biolink:Disease", [D2P]),
    );
    expect(wrapper.find(".PhenotypeProfileTable").exists()).toBe(true);
  });

  it("uses the gene-disease table on gene pages, in the section's category", async () => {
    const wrapper = await mountSection(
      node("HGNC:870", "biolink:Gene", [CAUSAL]),
    );
    expect(wrapper.find(".GeneDiseaseTable").attributes("data-kind")).toBe(
      "causal",
    );
  });

  it("passes the section's search box to the dismech tables", async () => {
    const wrapper = await mountSection(
      node("UBERON:0002107", "biolink:GrossAnatomicalStructure", [D2P]),
    );
    const box = wrapper.find("input[placeholder='Search table data...']");
    await box.setValue("cirrhosis");
    await box.trigger("change");
    await flushPromises();
    expect(
      wrapper.find(".PhenotypeProfileTable").attributes("data-search"),
    ).toBe("cirrhosis");
  });

  it("falls back to the stock table when the api serves no dismech", async () => {
    getDismechStatus.mockImplementation(async () => {
      throw new Error("404");
    });
    const wrapper = await mountSection(
      node("UBERON:0002107", "biolink:GrossAnatomicalStructure", [D2P]),
    );
    expect(wrapper.find(".AssociationsTable").exists()).toBe(true);
    expect(wrapper.find(".PhenotypeProfileTable").exists()).toBe(false);
  });

  it("falls back to the stock table with ?dismech=0", async () => {
    await router.push("/?dismech=0");
    const wrapper = await mountSection(
      node("UBERON:0002107", "biolink:GrossAnatomicalStructure", [D2P]),
    );
    expect(wrapper.find(".AssociationsTable").exists()).toBe(true);
  });

  it("adds a dismech phenotype section for a disease with no KG phenotypes", async () => {
    getPhenotypeProfile.mockImplementation(async () => ({
      kg_total: 0,
      dismech_unmatched: 4,
    }));
    const wrapper = await mountSection(
      node("MONDO:0100233", "biolink:Disease", [CAUSAL]),
    );
    const table = wrapper.find(".PhenotypeProfileTable");
    expect(table.exists()).toBe(true);
    expect(table.attributes("data-dismech-only")).toBe("true");
  });
});
