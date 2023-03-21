import * as api from "@/api";
import { postFeedback } from "@/api/feedback";
import { getSearchResults } from "@/api/node-search";
import { getTabulatedAssociations } from "@/api/node-associations";
import { getGene } from "@/api/genes";
import { getHierarchy } from "@/api/node-hierarchy";
import { getSummaries } from "@/api/publications";
import { compareSetToSet } from "@/api/phenotype-explorer";
import { getEntity } from "@/api/entity";
import { getHistoPheno } from "@/api/histo-pheno_NEW";

/**
 * tests for api functions. only test that request is constructed correctly,
 * (between starting function and making request). other steps adequately tested
 * via e2e, msw, and typescript. only test funcs that are non-trivial in this
 * step (i.e. not just taking a parameter and putting it in request url
 * string).
 */

const requestSpy = jest.spyOn(api, "request");

test("Post feedback requests correctly", async () => {
  await postFeedback("dummy title", "dummy body");
  expect(requestSpy.mock.lastCall[1]).toStrictEqual({
    title: "dummy title",
    body: "dummy body",
  });
  expect(requestSpy.mock.lastCall[2]).toStrictEqual({ method: "POST" });
});

test("Node search returns correctly", async () => {
  /** expected results */
  const result = {
    id: "MONDO:0017310",
    altIds: ["ORPHA:284993", "ORDO:284993", "Orphanet:284993", "UMLS:CN227112"],
    name: "Marfan and Marfan-related disorder",
    altNames: [],
    category: "disease",
    description: "",
    score: 108.652695,
    prefix: "MONDO",
    highlight:
      '<em class="hilite">Marfan</em> and <em class="hilite">Marfan</em>-related disorder',
  };

  const category = [
    {
      id: "disease",
      count: 25,
    },
    {
      id: "publication",
      count: 9,
    },
  ];

  const taxon = [
    {
      id: "Gallus gallus",
      count: 1,
    },
    {
      id: "Homo sapiens",
      count: 1,
    },
  ];

  const { count, results, facets } = await getSearchResults("marfan");
  expect(count).toEqual(61);
  expect(results).toContainEqual(result);
  expect(facets?.category).toEqual(expect.arrayContaining(category));
  expect(facets?.taxon).toEqual(expect.arrayContaining(taxon));
});

test("Get node associations requests correctly", async () => {
  await getTabulatedAssociations("MONDO:0007947", "disease", "gene");
  expect(requestSpy.mock.lastCall[0]).toContain(
    "/bioentity/disease/MONDO:0007947/genes"
  );
  expect(requestSpy.mock.lastCall[1]?.association_type).toBe("both");

  await getTabulatedAssociations(
    "MONDO:0007947",
    "disease",
    "correlated-gene",
    10,
    0,
    "",
    { id: "object", direction: "down" }
  );
  expect(requestSpy.mock.lastCall[1]?.sort).toBe("object desc");
  expect(requestSpy.mock.lastCall[1]?.association_type).toBe("non_causal");
});

test("Get gene requests correctly", async () => {
  await getGene("FlyBase:FBgn0029157");
  expect(requestSpy.mock.lastCall[1]?.q).toBe("flybase:FBgn0029157");
  expect(requestSpy.mock.lastCall[1]?.species).toBe("7227");
});

test("Get hierarchy requests correctly", async () => {
  await getHierarchy("dummy phenotype", "phenotype");
  expect(requestSpy.mock.lastCall[1]?.relationship_type).toContain(
    "subClassOf"
  );
  await getHierarchy("dummy gene", "gene");
  expect(requestSpy.mock.lastCall[1]?.relationship_type).toContain(
    "equivalentClass"
  );
});

test("Get publication requests correctly", async () => {
  await getSummaries(["PMID:123", "PMID:456"]);
  expect(requestSpy.mock.lastCall[1]?.id).toBe("123,456");
});

test("Phenotype explorer requests correctly", async () => {
  await compareSetToSet(
    ["HP:0004970", "HP:0004933", "HP:0004927"],
    ["HP:0004872", "HP:0012499", "HP:0002650"]
  );
  expect(JSON.parse(requestSpy.mock.lastCall[2]?.body as string)).toStrictEqual(
    {
      reference_ids: ["HP:0004970", "HP:0004933", "HP:0004927"],
      query_ids: [["HP:0004872", "HP:0012499", "HP:0002650"]],
      is_feature_set: true,
    }
  );

  await compareSetToSet(
    ["dummy phenotype", "HP:0004933", "HP:0004927"],
    ["HP:0004872", "HP:0012499", "HP:0002650"]
  );
  expect(
    JSON.parse(requestSpy.mock.lastCall[2]?.body as string).is_feature_set
  ).toBe(false);
});

test("Get entity requests correctly", async () => {
  await getEntity("MONDO:0007038");
  expect(requestSpy.mock.lastCall[0]?.split("/").slice(-1)[0]).toBe(
    "MONDO:0007038"
  );
});

test("Get entity returns correct fixture data", async () => {
  const entity = await getEntity("MONDO:0005439");
  expect(entity.id).toBe("MONDO:0005439");
  expect(entity.name).toBe("familial hypercholesterolemia");
  expect(entity.node_hierarchy?.super_classes?.length).toBe(2);
  expect(entity.node_hierarchy?.sub_classes?.length).toBe(5);
});

test("Get HistoPheno requests correctly", async () => {
  const histopheno = await getHistoPheno("MONDO:0020121");
  expect(histopheno.id).toBe("MONDO:0020121");
  expect(histopheno.items?.length).toBe(20);
  // expect(requestSpy.mock.lastCall[1]?.q).toBe("MONDO:0020121"); ?????? copilot suggestion
  }
);