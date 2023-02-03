it("Table of contents works", () => {
  cy.visit("/disease/MONDO:0007947");

  /** toggle button exists */
  cy.get(".toc")
    .invoke("attr", "aria-label")
    .should("include", "table of contents");

  /** starts closed (due to small screen size) */
  cy.get(".toc button")
    .invoke("attr", "aria-expanded")
    .should("equal", "false");

  /** click button to open */
  cy.get(".toc").trigger("click");
  cy.get(".toc button").invoke("attr", "aria-expanded").should("equal", "true");

  /** click off to close (with small screen size) */
  cy.get("body").click(500, 500);
  cy.get(".toc button")
    .invoke("attr", "aria-expanded")
    .should("equal", "false");

  /** open again and check contents */
  cy.get(".toc").trigger("click");
  cy.contains(".toc", "Overview");
  cy.contains(".toc", "Hierarchy");
  cy.contains(".toc", "Associations");

  /** check if solo selection mode works */
  cy.get(
    ".toc .checkbox"
  ).click(); /** cypress click function needed here for some reason */
  cy.get("main").contains("Overview").should("be.visible");
  cy.get("main").contains("Hierarchy").should("not.be.visible");
  cy.get("main").contains("Associations").should("not.be.visible");
  cy.get(".toc .checkbox").click();
  cy.get("main").contains("Hierarchy").should("be.visible");
  cy.get("main").contains("Associations").should("be.visible");
});

it("Title info shows", () => {
  cy.visit("/disease/MONDO:0007947");

  /** text info in top section */
  cy.contains("Marfan syndrome");
  cy.contains("Disease");
  cy.contains("MONDO:0007947");
});

it("Overview items show", () => {
  cy.visit("/disease/MONDO:0007947");

  /** check for synonyms and description */
  cy.contains("MFS1");
  cy.contains("Marfan syndrome type 1");
  cy.contains("Marfan syndrome is a disorder of the connective tissue");
});

it("Details items show", () => {
  cy.visit("/disease/MONDO:0007947");

  /** check iri, heritability, external references, etc. */
  cy.contains("MONDO_0007947");
  cy.contains("Autosomal dominant inheritance");
  cy.contains("NCIT:C34807");
  cy.contains("UMLS:C0024796");
});

it("Hierarchy items show", () => {
  cy.visit("/disease/MONDO:0007947");

  /** check super/equiv/sub classes */
  cy.contains("syndromic myopia");
  cy.contains("connective tissue disease with eye involvement");
  cy.contains("lens position anomaly");
  cy.contains("SCTID:19346006");
  cy.contains("NCIT:C34807");
});

it("Gene specific info shows", () => {
  cy.visit("/gene/MONDO:0007947");

  /** check symbol, etc. */
  cy.contains("Gene");
  cy.contains("Symbol");
  cy.contains("CDK2");
});

it("Publication specific info shows", () => {
  cy.visit("/publication/MONDO:0007947");

  /** check author, description, etc. */
  cy.contains("Publication");
  cy.contains("Dimorphic effects of transforming growth factor-β signaling");
  cy.contains("Cook JR");
  cy.contains("Ramirez F");
  cy.contains("1. Arterioscler Thromb Vasc Biol. 2015 Apr;35(4):911-7.");
});

it("Summary association info shows", () => {
  cy.visit("/disease/MONDO:0007947");

  /** check node, relation, target node */
  cy.get(".result").contains("Marfan syndrome");
  cy.get(".result").contains(/5 piece.*supporting evidence/);
  cy.get(".result")
    .contains("Has Phenotype")
    .invoke("attr", "href")
    .should("equal", "http://purl.obolibrary.org/obo/RO_0002200");
  cy.get(".result")
    .contains("Dural ectasia")
    .invoke("attr", "href")
    .should("equal", "/phenotype/HP:0100775");
});

it("Table association info shows", () => {
  cy.visit("/disease/MONDO:0007947");

  /** check node, relation, target node */
  cy.contains("Table").trigger("click");
  cy.contains("tr", "Marfan syndrome");
  cy.contains("tr", "Has Phenotype")
    .contains("Has Phenotype")
    .invoke("attr", "href")
    .should("equal", "http://purl.obolibrary.org/obo/RO_0002200");
  cy.contains("tr", "Dural ectasia")
    .contains("Dural ectasia")
    .invoke("attr", "href")
    .should("equal", "/phenotype/HP:0100775");
});

it("Association mode switching works", () => {
  cy.visit("/disease/MONDO:0007947");

  cy.url().should("include", "associations=phenotype");

  /** switch to table mode and variant associations */
  cy.contains("Table").trigger("click");
  cy.contains("button", "Phenotypes").trigger("click");
  cy.contains("[role='option'] > *", "Variants").trigger("click");
  cy.contains("th", "Variant");

  /** url updated with selected associations type */
  cy.url().should("include", "associations=variant");
});

it("Association table has extra metadata columns", () => {
  cy.visit("/disease/MONDO:0007947");

  /** switch to table mode */
  cy.contains("Table").trigger("click");

  /** look for phenotype frequency metadata column */
  cy.contains("tr", "Frequent")
    .contains("Frequent")
    .invoke("attr", "href")
    .should("equal", "http://purl.obolibrary.org/obo/HP_0040282");

  /** get association category select */
  cy.contains("button", "Phenotypes").as("category");

  /** switch to variant associations and look for taxon metadata column */
  cy.get("@category").trigger("click");
  cy.contains("[role='option'] > *", "Variants").trigger("click");
  cy.contains("td", "Mus musculus");
  cy.contains("th", "Taxon").find("button").trigger("click");
  cy.get("[role='listbox']").contains("Homo Sapiens");
  cy.get("[role='listbox']").contains("Mus Musculus");

  /**
   * switch to publication associations and look for author/year/etc. metadata
   * column
   */
  cy.get("@category").trigger("click");
  cy.contains("[role='option'] > *", "Publications").trigger("click");
  cy.contains("Author");
  cy.contains("Year");
  cy.contains("Publisher");
});

it("Evidence summary viewer works", () => {
  cy.visit("/disease/MONDO:0007947");

  /** click first evidence button (in first association in summary mode) */
  cy.contains("button", "Evidence").trigger("click");

  /** get evidence section */
  cy.get("#evidence").parent().as("evidence");

  /** check for evidence heading text */
  cy.get("@evidence").contains("has phenotype");
  cy.get("@evidence").contains("Dural ectasia");

  /** check high level evidence counts */
  cy.contains("Evidence codes").next().contains("2");
  cy.contains("Sources").next().contains("1");
  cy.contains("Publications").next().contains("3");

  /** check high level evidence links */
  cy.contains("experimental evidence used in manual assertion")
    .invoke("attr", "href")
    .should("equal", "http://purl.obolibrary.org/obo/ECO_0000269");
  cy.contains("https://archive.monarchinitiative.org/#hpoa")
    .invoke("attr", "href")
    .should("equal", "https://archive.monarchinitiative.org/#hpoa");
  cy.contains("PMID:10489951")
    .invoke("attr", "href")
    .should("equal", "http://www.ncbi.nlm.nih.gov/pubmed/10489951");
});

it("Evidence table viewer works", () => {
  cy.visit("/disease/MONDO:0007947");

  /** go to first association evidence and switch to table mode */
  cy.contains("button", "Evidence").click();
  cy.get("#evidence").parent().contains("table").trigger("click");

  /** check for all evidence columns */
  cy.contains("Subject");
  cy.contains("Relation");
  cy.contains("Object");
  cy.contains("Evidence Codes");
  cy.contains("Publications");
  cy.contains("Sources");
  cy.contains("References");

  /** check links in cells */
  cy.contains("experimental evidence used in manual assertion")
    .invoke("attr", "href")
    .should("equal", "http://purl.obolibrary.org/obo/ECO_0000269");
  cy.contains("#hpoa")
    .invoke("attr", "href")
    .should("equal", "https://archive.monarchinitiative.org/#hpoa");
  cy.contains("PMID:10489951")
    .invoke("attr", "href")
    .should("equal", "http://www.ncbi.nlm.nih.gov/pubmed/10489951");

  /** check that all publications show on hover */
  cy.contains("and 2 more").trigger("mouseenter");
  cy.contains(/PMID:3189335.*Marfan syndrome/);
});

it("Breadcrumbs section works", () => {
  cy.visit("/disease/MONDO:0007947");

  /**
   * visit chain of nodes. include clicking on both association links and
   * hierarchy item links
   */
  cy.contains("Dural ectasia").click();
  cy.contains("Cachexia").click();
  cy.contains("syndromic myopia").click();
  cy.contains("High, narrow palate").click();
  cy.contains("Genu recurvatum").click();

  /** get breadcrumbs flex container */
  cy.get("#breadcrumbs ~ .flex").as("breadcrumbs");

  /** util func to get inner text of breadcrumbs */
  const getInnerText = (els) => els[0].innerText.split(/\s+/).join(" ");

  /** full breadcrumbs string */
  cy.get("@breadcrumbs")
    .then(getInnerText)
    .should(
      "eq",
      "Marfan syndrome Has Phenotype Dural ectasia Has Phenotype Cachexia Is Super Class Of syndromic myopia Has Phenotype High, narrow palate Has Phenotype Genu recurvatum"
    );

  /** check back button works (doesn't mess up or clear breadcrumbs) */
  cy.go(-4);
  cy.wait(100);

  /** check breadcrumbs string */
  cy.get("@breadcrumbs")
    .then(getInnerText)
    .should("eq", "Marfan syndrome Has Phenotype Dural ectasia");

  /** check forward button (after back) works */
  cy.go(3);
  cy.wait(100);

  /** check reload in place works */
  cy.reload();
  cy.wait(100);

  /** check breadcrumbs string */
  cy.get("@breadcrumbs")
    .then(getInnerText)
    .should(
      "eq",
      "Marfan syndrome Has Phenotype Dural ectasia Has Phenotype Cachexia Is Super Class Of syndromic myopia Has Phenotype High, narrow palate"
    );

  /** click on node within breadcrumbs. should behave just like back button. */
  cy.get("@breadcrumbs").contains("Dural ectasia").click();
  cy.wait(100);
  cy.get("@breadcrumbs")
    .then(getInnerText)
    .should("eq", "Marfan syndrome Has Phenotype Dural ectasia");

  /** check clear button works */
  cy.contains("clear").click();
  cy.get("#breadcrumbs").should("not.exist");
});
