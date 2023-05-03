import { expect, test } from "@playwright/test";

test("Table of contents works", async ({ page }) => {
  await page.goto("/disease/MONDO:0007947");
  await page.setViewportSize({ width: 800, height: 1000 });

  /** toggle button exists */
  await expect(page.locator(".toc")).toHaveAttribute(
    "aria-label",
    /table of contents/i
  );

  /** starts closed (due to small screen size) */
  await expect(page.locator(".toc button")).toHaveAttribute(
    "aria-expanded",
    "false"
  );

  /** click button to open */
  await page.locator(".toc").click();
  await expect(page.locator(".toc button")).toHaveAttribute(
    "aria-expanded",
    "true"
  );

  /** click off to close (with small screen size) */
  await page.locator("body").click({ position: { x: 500, y: 500 } });
  await expect(page.locator(".toc button")).toHaveAttribute(
    "aria-expanded",
    "false"
  );

  /** open again and check contents */
  await page.locator(".toc").click();
  await expect(
    page.locator(".toc", { hasText: /Overview/i }).first()
  ).toBeVisible();
  await expect(
    page.locator(".toc", { hasText: /Hierarchy/i }).first()
  ).toBeVisible();
  await expect(
    page.locator(".toc", { hasText: /Associations/i }).first()
  ).toBeVisible();

  /** check if solo selection mode works */
  await page.locator(".toc .checkbox").click();
  await expect(
    page
      .locator("main")
      .getByText(/Overview/i)
      .first()
  ).toBeVisible();
  await expect(
    page
      .locator("main")
      .getByText(/Hierarchy/i)
      .first()
  ).not.toBeVisible();
  await expect(
    page
      .locator("main")
      .getByText(/Associations/i)
      .first()
  ).not.toBeVisible();
  await page.locator(".toc .checkbox").click();
  await expect(
    page
      .locator("main")
      .getByText(/Hierarchy/i)
      .first()
  ).toBeVisible();
  await expect(
    page
      .locator("main")
      .getByText(/Associations/i)
      .first()
  ).toBeVisible();
});

test("Title info shows", async ({ page }) => {
  await page.goto("/disease/MONDO:0007947");

  /** text info in top section */
  await expect(page.getByText(/Marfan syndrome/i).first()).toBeVisible();
  await expect(page.getByText(/Disease/i).first()).toBeVisible();
  await expect(page.getByText(/MONDO:0007947/i).first()).toBeVisible();
});

test("Overview items show", async ({ page }) => {
  await page.goto("/disease/MONDO:0007947");

  /** check for synonyms and description */
  await expect(page.getByText(/MFS1/i).first()).toBeVisible();
  await expect(page.getByText(/Marfan syndrome type 1/i).first()).toBeVisible();
  await expect(
    page
      .getByText(/Marfan syndrome is a disorder of the connective tissue/i)
      .first()
  ).toBeVisible();
});

test("Details items show", async ({ page }) => {
  await page.goto("/disease/MONDO:0007947");

  /** check iri, heritability, external references, etc. */
  await expect(page.getByText(/MONDO_0007947/i).first()).toBeVisible();
  await expect(
    page.getByText(/Autosomal dominant inheritance/i).first()
  ).toBeVisible();
  await expect(page.getByText(/NCIT:C34807/i).first()).toBeVisible();
  await expect(page.getByText(/UMLS:C0024796/i).first()).toBeVisible();
});

test("Hierarchy items show", async ({ page }) => {
  await page.goto("/disease/MONDO:0007947");

  /** check super/equiv/sub classes */
  await expect(page.getByText(/syndromic myopia/i).first()).toBeVisible();
  await expect(
    page.getByText(/connective tissue disease with eye involvement/i).first()
  ).toBeVisible();
  await expect(page.getByText(/lens position anomaly/i).first()).toBeVisible();
  await expect(page.getByText(/SCTID:19346006/i).first()).toBeVisible();
  await expect(page.getByText(/NCIT:C34807/i).first()).toBeVisible();
});

test("Gene specific info shows", async ({ page }) => {
  await page.goto("/gene/MONDO:0007947");

  /** check symbol, etc. */
  await expect(page.getByText(/Gene/i).first()).toBeVisible();
  await expect(page.getByText(/Symbol/i).first()).toBeVisible();
  await expect(page.getByText(/CDK2/i).first()).toBeVisible();
});

test("Publication specific info shows", async ({ page }) => {
  await page.goto("/publication/MONDO:0007947");

  /** check author, description, etc. */
  await expect(page.getByText(/Publication/i).first()).toBeVisible();
  await expect(
    page
      .getByText(/Dimorphic effects of transforming growth factor-β signaling/i)
      .first()
  ).toBeVisible();
  await expect(page.getByText(/Cook JR/i).first()).toBeVisible();
  await expect(page.getByText(/Ramirez F/i).first()).toBeVisible();
  await expect(
    page
      .getByText(
        /1\. Arterioscler Thromb Vasc Biol\. 2015 Apr;35\(4\):911-7\./i
      )
      .first()
  ).toBeVisible();
});

test("Summary association info shows", async ({ page }) => {
  await page.goto("/disease/MONDO:0007947");

  /** check node, relation, target node */
  await expect(
    page
      .locator(".result")
      .getByText(/Marfan syndrome/i)
      .first()
  ).toBeVisible();
  await expect(
    page
      .locator(".result")
      .getByText(/5 piece.*supporting evidence/i)
      .first()
  ).toBeVisible();
  await expect(
    page
      .locator(".result")
      .getByText(/Has Phenotype/i)
      .first()
  ).toHaveAttribute("href", "http://purl.obolibrary.org/obo/RO_0002200");
  await expect(
    page
      .locator(".result")
      .getByText(/Dural ectasia/i)
      .first()
  ).toHaveAttribute("href", "/phenotype/HP:0100775");
});

test("Table association info shows", async ({ page }) => {
  await page.goto("/disease/MONDO:0007947");

  /** check node, relation, target node */
  await page.getByText(/Table/i).first().click();
  await expect(
    page.locator("tr", { hasText: /Marfan syndrome/ }).first()
  ).toBeVisible();
  await expect(
    page
      .locator("tr", { hasText: /Has Phenotype/ })
      .first()
      .getByText(/Has Phenotype/i)
      .first()
  ).toHaveAttribute("href", "http://purl.obolibrary.org/obo/RO_0002200");
  await expect(
    page
      .locator("tr", { hasText: /Dural ectasia/ })
      .first()
      .getByText(/Dural ectasia/i)
      .first()
  ).toHaveAttribute("href", "/phenotype/HP:0100775");
});

test("Association mode switching works", async ({ page }) => {
  await page.goto("/disease/MONDO:0007947");
  await expect(page).toHaveURL(/associations=phenotype/i);

  /** switch to table mode and variant associations */
  await page.getByText(/Table/i).first().click();
  await page
    .locator("button", { hasText: /Phenotypes/i })
    .first()
    .click();
  await page
    .getByRole("option")
    .filter({ hasText: /Variants/i })
    .first()
    .click();
  await expect(
    page.locator("th", { hasText: /Variant/i }).first()
  ).toBeVisible();

  /** url updated with selected associations type */
  await expect(page).toHaveURL(/associations=variant/i);
});

test("Association table has extra metadata columns", async ({ page }) => {
  await page.goto("/disease/MONDO:0007947");

  /** switch to table mode */
  await page.getByText(/Table/i).first().click();

  /** look for phenotype frequency metadata column */
  await expect(
    page
      .locator("tr", { hasText: /Frequent/ })
      .first()
      .getByText(/Frequent/i)
      .first()
  ).toHaveAttribute("href", "http://purl.obolibrary.org/obo/HP_0040282");

  /** switch to variant associations and look for taxon metadata column */
  await page
    .locator("button", { hasText: /Phenotypes/i })
    .first()
    .click();
  await page
    .getByRole("option")
    .filter({ hasText: /Variants/ })
    .first()
    .click();
  await expect(
    page.locator("td", { hasText: /Mus musculus/ }).first()
  ).toBeVisible();
  await page
    .locator("th", { hasText: /Taxon/ })
    .first()
    .locator("button")
    .click();
  await expect(
    page
      .getByRole("listbox")
      .filter({ hasText: /Homo Sapiens/i })
      .first()
  ).toBeVisible();
  await expect(
    page
      .getByRole("listbox")
      .filter({ hasText: /Mus Musculus/i })
      .first()
  ).toBeVisible();

  /**
   * switch to publication associations and look for author/year/etc. metadata
   * column
   */
  await page
    .locator("button", { hasText: /Variants/i })
    .first()
    .click();
  await page
    .getByRole("option")
    .filter({ hasText: /Publications/ })
    .first()
    .click();
  await expect(page.getByText(/Author/i).first()).toBeVisible();
  await expect(page.getByText(/Year/i).first()).toBeVisible();
  await expect(page.getByText(/Publisher/i).first()).toBeVisible();
});

test("Evidence summary viewer works", async ({ page }) => {
  await page.goto("/disease/MONDO:0007947");

  /** click first evidence button (in first association in summary mode) */
  await page
    .locator("button", { hasText: /Evidence/ })
    .first()
    .click();

  /** get evidence section */
  const evidence = page.locator("#evidence").locator("..");

  /** check for evidence heading text */
  await expect(evidence.getByText(/has phenotype/i).first()).toBeVisible();
  await expect(evidence.getByText(/Dural ectasia/i).first()).toBeVisible();

  /** check high level evidence counts */
  await expect(page.getByText(/Evidence codes.*2/i).first()).toBeVisible();
  await expect(page.getByText(/Sources.*1/i).first()).toBeVisible();
  await expect(page.getByText(/Publications.*3/i).first()).toBeVisible();

  /** check high level evidence links */
  await expect(
    page
      .getByRole("link")
      .filter({ hasText: /experimental evidence used in manual assertion/i })
      .first()
  ).toHaveAttribute("href", "http://purl.obolibrary.org/obo/ECO_0000269");
  await expect(
    page
      .getByRole("link")
      .filter({ hasText: /https:\/\/archive\.monarchinitiative\.org\/#hpoa/i })
      .first()
  ).toHaveAttribute("href", "https://archive.monarchinitiative.org/#hpoa");
  await expect(
    page
      .getByRole("link")
      .filter({ hasText: /PMID:10489951/i })
      .first()
  ).toHaveAttribute("href", "http://www.ncbi.nlm.nih.gov/pubmed/10489951");
});

test("Evidence table viewer works", async ({ page }) => {
  await page.goto("/disease/MONDO:0007947");

  /** go to first association evidence and switch to table mode */
  await page
    .locator("button", { hasText: /Evidence/ })
    .first()
    .click();
  await page
    .locator("#evidence")
    .locator("..")
    .getByText(/table/i)
    .first()
    .click();

  /** check for all evidence columns */
  await expect(page.getByText(/Subject/i).first()).toBeVisible();
  await expect(page.getByText(/Relation/i).first()).toBeVisible();
  await expect(page.getByText(/Object/i).first()).toBeVisible();
  await expect(page.getByText(/Evidence Codes/i).first()).toBeVisible();
  await expect(page.getByText(/Publications/i).first()).toBeVisible();
  await expect(page.getByText(/Sources/i).first()).toBeVisible();
  await expect(page.getByText(/References/i).first()).toBeVisible();

  /** check links in cells */
  await expect(
    page.getByText(/experimental evidence used in manual assertion/i).first()
  ).toHaveAttribute("href", "http://purl.obolibrary.org/obo/ECO_0000269");
  await expect(page.getByText(/#hpoa/i).first()).toHaveAttribute(
    "href",
    "https://archive.monarchinitiative.org/#hpoa"
  );
  await expect(page.getByText(/PMID:10489951/i).first()).toHaveAttribute(
    "href",
    "http://www.ncbi.nlm.nih.gov/pubmed/10489951"
  );

  /** check that all publications show on hover */
  await page
    .getByText(/and 2 more/i)
    .first()
    .dispatchEvent("mouseenter");
  await expect(
    page.getByText(/PMID:3189335.*Marfan syndrome/i).first()
  ).toBeVisible();
});

test("Breadcrumbs section works", async ({ page }) => {
  await page.goto("/disease/MONDO:0007947");

  /**
   * visit chain of nodes. include clicking on both association links and
   * hierarchy item links
   */
  const chain = [
    "Marfan syndrome",
    "Has Phenotype",
    "Dural ectasia",
    "Has Phenotype",
    "Cachexia",
    "Is Super Class Of",
    "syndromic myopia",
    "Has Phenotype",
    "High, narrow palate",
    "Has Phenotype",
    "Genu recurvatum",
  ];
  for (let n = 0; n < chain.length; n += 2)
    await page.getByText(new RegExp(chain[n], "i")).first().click();

  /** util func to get inner text of breadcrumbs */
  const checkBreadcrumbs = async (expectedArray: string[]) => {
    const items = await page
      .locator("#breadcrumbs ~ .flex > *")
      .allInnerTexts();
    for (const [index, actual] of Object.entries(items)) {
      const expected = expectedArray[Number(index)];
      await expect(actual).toMatch(new RegExp(expected, "i"));
    }
  };

  /** full breadcrumbs string */
  await checkBreadcrumbs(chain);

  /** check back button works (doesn't mess up or clear breadcrumbs) */
  await page.goBack();
  await page.goBack();
  await page.goBack();
  await page.goBack();

  /** get breadcrumbs string */
  await checkBreadcrumbs(chain.slice(0, 3));

  /** check forward button (after back) works */
  await page.goForward();
  await page.goForward();
  await page.goForward();

  /** check reload in place works */
  await page.reload();

  /** check breadcrumbs string */
  await checkBreadcrumbs(chain.slice(0, 9));

  /** click on node within breadcrumbs. should behave just like back button. */
  await page
    .locator("#breadcrumbs ~ .flex")
    .getByText(/Dural ectasia/i)
    .first()
    .click();
  await checkBreadcrumbs(chain.slice(0, 3));

  /** check clear button works */
  await page.getByText(/clear/i).first().click();
  await expect(page.locator("#breadcrumbs")).not.toBeVisible();
});