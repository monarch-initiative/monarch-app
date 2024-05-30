import { readFileSync } from "fs";
import { join } from "path";
import { expect, test } from "vitest";
import { processMulticompareResponse } from "@/api/phenotype-explorer";

test("processMulticompareResponse works", async () => {
  // Load the data from the JSON file
  const data = JSON.parse(
    readFileSync(
      join(__dirname, "../fixtures/phenotype-explorer-multicompare-tiny.json"),
      "utf-8",
    ),
  );

  // Define the subjects and objectSets for the test
  const subjects = ["XPO:0103336"];
  const objectSets = [
    {
      id: "myset:01",
      label: "set01",
      phenotypes: ["ZP:0000043"],
    },
  ];

  // Call the processMulticompareResponse function with the test data
  const result = processMulticompareResponse(data, subjects, objectSets);

  // Add your assertions here
  // For example:
  expect(result.phenogrid.rows.length).eq(1);
  expect(result.phenogrid.cols.length).eq(1);
});
