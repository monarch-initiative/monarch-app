import { expect, test } from "@playwright/test";

test("Datasets and ontologies populate", async ({ page }) => {
  /** setup */
  await page.goto("/sources");

  /** get example source accordion button */
  const button = page.getByText(/FlyBase/i).first();

  /** open accordion */
  await button.click();

  /** get expanded content */
  const content = page.locator("button[aria-expanded='true'] + .content");
  await expect(content).toBeVisible();

  /** check license link */
  await expect(
    content
      .getByRole("link")
      .filter({ hasText: /License/i })
      .first(),
  ).toHaveAttribute("href", "http://reusabledata.org/flybase.html");

  /** check rdf link */
  await expect(
    content.getByRole("link").filter({ hasText: /RDF/i }).first(),
  ).toHaveAttribute(
    "href",
    "https://archive.monarchinitiative.org/202103/rdf/flybase.ttl",
  );

  /** check date */
  await expect(content.getByText(/2021-03-09/i).first()).toBeVisible();

  /** check image */
  await expect(page.locator("img")).toHaveAttribute("src", /flybase.*\.png/i);

  /** check links */
  await expect(
    content.getByText(/fbrf_pmid_pmcid_doi_fb_2021_01\.tsv\.gz/i).first(),
  ).toBeVisible();
  await expect(
    content.getByText(/disease_model_annotations_fb_2021_01\.tsv\.gz/i).first(),
  ).toBeVisible();
  await expect(
    content.getByText(/fbal_to_fbgn_fb_FB2021_01\.tsv\.gz/i).first(),
  ).toBeVisible();
  await expect(content.getByText(/species\.ab\.gz/i).first()).toBeVisible();
});
