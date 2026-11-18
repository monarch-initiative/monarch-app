import { beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises } from "@vue/test-utils";
import type { GeneDiseaseProfile } from "@/api/dismech";
import GeneDiseaseTable from "@/pages/node/GeneDiseaseTable.vue";
import { mount } from "./setup";

const profile = (
  over: Partial<GeneDiseaseProfile> = {},
): GeneDiseaseProfile => ({
  id: "HGNC:870",
  release: "v0.1.47",
  kind: "causal",
  total: 1,
  rows: [
    {
      disease_id: "MONDO:0010200",
      label: "Wilson disease",
      sources: ["infores:omim"],
      observations: [
        {
          source: "infores:omim",
          predicate: "biolink:causes",
          record: "OMIM:277900",
        },
      ],
      dismech: [],
      dismech_only: false,
    },
  ],
  dismech_available: true,
  kg_total: 1,
  dismech_corroborated: 0,
  dismech_unmatched: 0,
  mechanism_nodes: {},
  ...over,
});

const getGeneDiseaseProfile = vi.fn<
  unknown[],
  Promise<ReturnType<typeof profile>>
>(async () => profile());

vi.mock("@/api/dismech", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/api/dismech")>()),
  getGeneDiseaseProfile: (...args: unknown[]) => getGeneDiseaseProfile(...args),
}));
vi.mock("@/pages/node/MechanismDag.vue", () => ({
  default: { name: "MechanismDag", template: "<div class='dag' />" },
}));

const ATP7B = { id: "HGNC:870", name: "ATP7B", category: "biolink:Gene" };

const lastCall = () => getGeneDiseaseProfile.mock.calls.at(-1) as unknown[];

beforeEach(() => {
  getGeneDiseaseProfile.mockReset();
  getGeneDiseaseProfile.mockImplementation(async () => profile());
});

describe("GeneDiseaseTable", () => {
  it("asks for the node's pairs in the section's category", async () => {
    const wrapper = mount(GeneDiseaseTable, {
      props: { node: ATP7B, kind: "correlated" },
    });
    await flushPromises();
    expect(lastCall().slice(0, 2)).toEqual(["HGNC:870", "correlated"]);
    expect(wrapper.text()).toContain("Wilson disease");
  });

  it("sends the section's search, and refetches from the first page when it changes", async () => {
    const wrapper = mount(GeneDiseaseTable, {
      props: { node: ATP7B, kind: "causal", search: "" },
    });
    await flushPromises();
    await wrapper.setProps({ search: "wilson" });
    await flushPromises();
    expect(lastCall()[2]).toMatchObject({ search: "wilson", offset: 0 });
  });
});
