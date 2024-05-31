import { readFileSync } from "fs";
import { join } from "path";
import { expect, test } from "vitest";
import { processMulticompareResponse } from "@/api/phenotype-explorer";

test("processMulticompareResponse works", async () => {
  // Load the data from the JSON file
  const data = JSON.parse(
    readFileSync(
      join(__dirname, "../fixtures/phenotype-explorer-multi-compare.json"),
      "utf-8",
    ),
  );

  const request = JSON.parse(
    readFileSync(
      join(
        __dirname,
        "../fixtures/phenotype-explorer-multi-compare-request.json",
      ),
      "utf-8",
    ),
  );

  // Call the processMulticompareResponse function with the test data
  const result = processMulticompareResponse(
    data,
    request.subjects,
    request.object_sets,
  );

  // Add your assertions here
  // For example:
  expect(result.phenogrid.rows.length).eq(7);
  expect(result.phenogrid.cols.length).eq(2);
});
