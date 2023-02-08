import example from "@/views/explore/text-annotator.json";

it("Basic search results show", () => {
  cy.visit("/explore#text-annotator");

  /** paste example text */
  cy.get("textarea").focus();
  cy.get("textarea").type(example.content.slice(0, 100));
  cy.get("textarea").blur();

  /** look for plain text result */
  cy.contains("Lewis (1978) found 7").should("exist");

  /** find first annotation and hover */
  cy.contains("affected").trigger("mouseenter");

  /** look for links and text in tooltip */
  cy.contains("HP:0032320")
    .invoke("attr", "href")
    .should("includes", "HP:0032320");
  cy.contains("acts upstream of or within").should("exist");
});
