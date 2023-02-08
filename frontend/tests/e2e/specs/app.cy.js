it("App renders", () => {
  cy.visit("/");
  cy.get("#app").should("not.be.empty");
});
