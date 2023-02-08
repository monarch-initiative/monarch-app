it("Datasets and ontologies populate", () => {
  /** setup */
  cy.visit("/sources");

  /** get example source accordion button */
  cy.contains("FlyBase").as("button");

  /** open accordion */
  cy.get("@button").trigger("click");

  /** get expanded content */
  cy.get("button[aria-expanded='true'] + .content").as("content");
  cy.get("@content").should("be.visible");

  /** check license link */
  cy.get("@content")
    .contains("License")
    .invoke("attr", "href")
    .should("eq", "http://reusabledata.org/flybase.html");

  /** check rdf link */
  cy.get("@content")
    .contains("RDF")
    .invoke("attr", "href")
    .should(
      "eq",
      "https://archive.monarchinitiative.org/202103/rdf/flybase.ttl"
    );

  /** check date */
  cy.get("@content").contains("2021-03-09");

  /** check image */
  cy.get("@content")
    .get("img")
    .invoke("attr", "src")
    .should("match", /flybase.*\.png/);

  /** check links */
  cy.get("@content").contains("fbrf_pmid_pmcid_doi_fb_2021_01.tsv.gz");
  cy.get("@content").contains("disease_model_annotations_fb_2021_01.tsv.gz");
  cy.get("@content").contains("fbal_to_fbgn_fb_FB2021_01.tsv.gz");
  cy.get("@content").contains("species.ab.gz");
});
