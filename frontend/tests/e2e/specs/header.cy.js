it("Header nav bar collapses on small screens", () => {
  /** setup */
  cy.visit("/");
  cy.viewport("iphone-5");

  /** get elements of interest */
  cy.get("header button").first().as("toggle");
  cy.get("nav a").first().as("nav");

  /** click toggle button and see if nav hides/shows */
  cy.get("@toggle").should("be.visible");
  cy.get("@nav").should("not.be.visible");
  cy.get("@toggle").trigger("click");
  cy.get("@nav").should("be.visible");
  cy.get("@toggle").trigger("click");
  cy.get("@nav").should("not.be.visible");
});
