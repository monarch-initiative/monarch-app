<!--
  about landing page
-->

<template>
  <!-- brief overview -->
  <AppSection>
    <AppHeading>About</AppHeading>
    <p>
      The Monarch Initiative is an extensive knowledge graph and ecosystem of
      tools made for the benefit of clinicians, researchers, and scientists. The
      knowledge graph consists of millions of entities &ndash; genes, diseases,
      phenotypes, and many more &ndash; imported from dozens of sources.
    </p>
  </AppSection>

  <!-- main links to sub pages -->
  <AppSection>
    <AppFlex gap="big">
      <AppTile
        to="/overview"
        icon="cogs"
        title="Overview"
        subtitle="How all the pieces of Monarch fit together"
      />
      <AppTile
        to="https://github.com/biolink/biolink-api"
        icon="code"
        title="API"
        subtitle="The API behind this website, BioLink"
      />
      <AppTile
        to="/sources"
        icon="database"
        title="Sources"
        subtitle="Datasets, ontologies, and downloads"
      />
      <AppTile
        to="/cite"
        icon="feather-alt"
        title="Cite"
        subtitle="How to cite and attribute Monarch"
      />
      <AppTile
        to="/team"
        icon="users"
        title="Team"
        subtitle="The people behind Monarch"
      />
      <AppTile
        to="/publications"
        icon="newspaper"
        title="Publications"
        subtitle="Monarch-related published works"
      />
      <AppTile
        to="/terms"
        icon="balance-scale"
        title="Terms of Use"
        subtitle="Disclaimers and agreements"
      />
    </AppFlex>
  </AppSection>

  <!-- mission statement -->
  <AppSection>
    <AppHeading>More about us</AppHeading>
    <AppHeading>Our Vision:</AppHeading>
    <ol>
      <li>
        Connect cross-species gene, genotype, variant, disease, and phenotype
        data
      </li>
      <li>Provide a portal for exploration of phenotype-based similarity</li>
      <li>
        Facilitate identification of animal models of human disease through
        phenotypic similarity
      </li>
      <li>Enable quantitative comparison of cross-species phenotypes</li>
      <li>Develop embeddable widgets for data exploration</li>
      <li>Influence genotype and phenotype reporting standards</li>
      <li>Improve ontologies to better curate genotype-phenotype data</li>
    </ol>

    <p>
      The Monarch Initiative is an integrative data and analytic platform
      connecting phenotypes to genotypes across species, bridging basic and
      applied research with semantics-based analysis. The correlation of
      phenotypic outcomes and disease with genetic variation and environmental
      factors is a core pursuit in biology and biomedicine. We have created or
      currently contribute to many essential bio-ontologies that together enable
      sophisticated and semantically integrated computational analysis across
      gene, genotype, variant, disease, and phenotype data. We have developed
      algorithms and tools that are in use by multiple communities for tasks
      including the identification of animal models of human disease through
      phenotypic similarity, phenotype-driven computational support for
      differential diagnostics, and translational research.
    </p>

    <p>
      We lead the development of the
      <AppLink to="https://hpo.jax.org/">Human Phenotype Ontology</AppLink>,
      which is used across the world for genomic diagnostics in genetic disease
      and other areas. We are a Driver Project for the
      <AppLink to="https://www.ga4gh.org/"
        >Global Alliance for Genomics and Health</AppLink
      >
      (GA4GH), and are major contributors to the development of genomics
      standards within GA4GH. Additionally, we have developed
      <AppLink to="http://obofoundry.org/ontology/mondo.html">Mondo</AppLink>, a
      unified disease ontology that represents the most comprehensive
      integration of disease entities ever achieved.
    </p>
  </AppSection>
</template>
