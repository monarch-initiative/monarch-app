import { facetsToFilters, queryToParams } from "@/api/facets";

test("Facets to filters works", () => {
  expect(
    facetsToFilters({
      facetA: {
        entryA: 12,
        entryB: 34,
      },
      facetB: {
        entryA: 56,
        entryB: 78,
      },
    })
  ).toStrictEqual({
    facetA: [
      { id: "entryA", count: 12 },
      { id: "entryB", count: 34 },
    ],
    facetB: [
      { id: "entryA", count: 56 },
      { id: "entryB", count: 78 },
    ],
  });
});

test("Query to params works", async () => {
  expect(
    await queryToParams(
      {
        facetA: ["entryA", "entryB"],
      },
      {
        facetA: ["entryB"],
      }
    )
  ).toStrictEqual({ facetA: ["entryB"] });
  expect(
    await queryToParams(
      {
        facetA: ["entryA", "entryB"],
      },
      {
        facetA: ["entryA", "entryB"],
      }
    )
  ).toStrictEqual({});
  expect(
    await queryToParams(
      {
        facetA: ["entryA", "entryB"],
      },
      {
        facetA: [],
      }
    )
  ).toStrictEqual({});
  expect(
    await queryToParams(
      {
        taxon: ["mus musculus", "dummy taxon"],
      },
      {
        taxon: ["mus musculus"],
      }
    )
  ).toStrictEqual({ taxon: ["NCBITaxon:10090"] });
});
