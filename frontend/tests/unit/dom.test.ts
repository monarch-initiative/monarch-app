import { waitFor } from "@/util/dom";
import { sleep } from "@/util/debug";

test("Wait for works", async () => {
  sleep(100).then(() => document.body.append(document.createElement("span")));
  const span = await waitFor("span");
  expect(span).toBeInstanceOf(Element);
});
