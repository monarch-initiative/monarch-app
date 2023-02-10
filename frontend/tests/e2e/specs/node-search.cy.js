it("Redirects to explore page from home page", () => {
  /** go to homepage and focus search box */
  cy.visit("/");
  cy.get("input").trigger("focus");
  cy.location().should((loc) => expect(loc.pathname).to.eq("/explore"));

  /** go to homepage and click one of tabs */
  cy.visit("/");
  cy.contains("Text Annotator").as("button").trigger("click");
  cy.location().should((loc) => expect(loc.pathname).to.eq("/explore"));
});

it("Recent/frequent results show", () => {
  cy.visit("/explore");

  /** dummy searches */
  const searches = [
    "abc def",
    "123",
    "123",
    "abc def",
    "123",
    "123",
    "abc def",
  ];

  /** go through dummy searches */
  for (const search of searches) {
    cy.get("input").type(search);
    /** dispatch textbox change event which triggers search and records it */
    cy.get("input").trigger("change");
    /** wait for results */
    cy.get("p.description", { timeout: 4000 }).should("be.visible");
    cy.get(".textbox button").trigger("click");
  }

  /** go to node page, which should also get added to search history */
  cy.visit("/disease/MONDO:12345");
  /** wait for page to load */
  cy.get("#overview", { timeout: 4000 }).should("be.visible");
  cy.visit("/explore");

  /** focus search box to show list of results */
  cy.get("input").trigger("focus", { force: true });

  /** recent */
  cy.get("[role='option']").eq(0).contains("marfan syndrome");
  cy.get("[role='option']").eq(1).contains("abc def");
  cy.get("[role='option']").eq(2).contains("123");

  /** frequent */
  cy.get("[role='option']").eq(3).contains("123");
  cy.get("[role='option']").eq(4).contains("abc def");
});

it("Autocomplete results show", () => {
  /** type something in search box for regular backend autocomplete results */
  cy.visit("/explore");
  cy.get("input").type("Marfan");
  cy.contains("Marfan and Marfan-related disorder");
});

it("Basic search results show", () => {
  cy.visit("/explore");
  cy.get("input").type("Marfan");
  cy.get("input").trigger("change");

  /** search result with link shows */
  cy.contains("neonatal Marfan syndrome").as("result");
  cy.get("@result")
    .invoke("attr", "href")
    .should("includes", "disease/MONDO:0017309");
});

it("Pagination works", () => {
  cy.visit("/explore");
  cy.get("input").type("Marfan");
  cy.get("input").trigger("change");

  /** pagination text, and click through to next page */
  cy.contains("1 to 10 of 61 results");
  cy.contains("button", /^2$/).trigger("click");
  cy.contains("11 to 20 of 61 results");
});

it("Filters show", () => {
  cy.visit("/explore");
  cy.get("input").type("Marfan");
  cy.get("input").trigger("change");

  /** filters show */
  /** actual filtering done by backend, so not much to test here */
  cy.contains("Category").trigger("click");
  cy.contains(/Disease*.25/).should("exist");
  cy.contains("Taxon").trigger("click");
  cy.contains(/Gallus Gallus*.1/).should("exist");
});
