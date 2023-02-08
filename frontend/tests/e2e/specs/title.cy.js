it("Document title updates on navigation", () => {
  /** pages to test */
  const pages = ["explore", "about", "help"];

  /** visit each page and check doc title */
  for (const page of pages) {
    cy.visit("/" + page);
    cy.title().should(($title) => {
      const title = $title.toLowerCase();
      expect(title).to.contain("monarch");
      expect(title).to.contain(page);
    });
  }
});
