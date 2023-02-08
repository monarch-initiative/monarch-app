import { isExternal } from "@/util/url";

test("Url funcs work", () => {
  expect(isExternal("mailto:jane@smith.org")).toBe(true);
  expect(isExternal("https://monarch.com")).toBe(true);
  expect(isExternal("https://archive.monarchinitiative.org")).toBe(false);
});
