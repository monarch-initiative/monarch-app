import { expect, test } from "vitest";
import { sleep } from "@/util/debug";
import { waitFor } from "@/util/dom";

test("Wait for works", async () => {
  sleep(100).then(() => document.body.append(document.createElement("span")));
  const span = await waitFor("span");
  expect(span).toBeInstanceOf(Element);
});
