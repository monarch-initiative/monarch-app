<!--
  about overview page

  comprehensive diagram of monarch "ecosystem": all related tools and resources
-->

<template>
  <AppSection>
    <AppHeading>Overview</AppHeading>
    <p>
      The Monarch Initiative is more than just this website, it is a whole
      ecosystem of related tools. This diagram illustrates the architecture of
      how it all fits together.
    </p>

    <p>
      The three primary data types in the Monarch KG are genes, diseases, and
      phenotypes. The image below details their entity (node) and link (edge)
      counts and the unifying ontologies by which the source data and ontologies
      are harmonized. Cross-species inference is accomplished via gene
      orthology, homology, and phenotype similarity. Content dissemination is
      via API, the Monarch UI, and within the clinical application Exomiser.
      Note that the figure expresses only a portion of the integrated ontologies
      in column C. For a comprehensive list see PHENIO documentation (linked
      below).
    </p>

    <figure>
      <img
        src="@/assets/architecture.png"
        alt="Diagram of Monarch infrastructure, described below."
      />
      <figcaption>
        <strong> Data harmonization within the Monarch KG. </strong>
        (A) Data types and counts. (B, C, D) Data sources, ontologies, and
        knowledge graphs. (E) Cross-species inference. (F) Content dissemination
        <br />
        (Column D acronyms) GO: Gene Ontology; BP: Biological Process; MF:
        Molecular Function; CC: Cellular Component
      </figcaption>
    </figure>

    <hr />

    <p>
      Documentation, licensing, and other information for each piece in the
      Monarch architecture can be found on GitHub, Google, and elsewhere:
    </p>

    <AppFlex>
      <AppButton
        to="https://github.com/monarch-initiative"
        text="Monarch Initiative on GitHub"
        icon="github"
      />
      <AppButton
        to="https://github.com/monarch-initiative/phenio/"
        text="Phenio on GitHub"
        icon="github"
      />
    </AppFlex>
  </AppSection>
</template>
