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

    <img
      src="@/assets/architecture.png"
      alt="Diagram of Monarch infrastructure, described below."
    />

    <p>
      Structured and unstructured data sources are loaded into SciGraph via
      dipper (1), our data ingest pipeline. A variety of ontologies are
      processed in the Monarch Integration Layer and are also loaded into
      SciGraph, resulting in a combined knowledge and data graph (2). Data is
      disseminated via SciGraph Services, wrapped around by the BioLink API (3).
      This lightweight API makes few assumptions, acting as a data access layer
      for all of Monarch’s Services. Users can interrogate Monarch using our
      tools for text annotation, navigating the ontologies, and matching
      phenotype profiles (4).
    </p>

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
        to="https://github.com/SciGraph"
        text="SciGraph on GitHub"
        icon="github"
      />
      <AppButton
        to="https://github.com/biolink"
        text="BioLink on GitHub"
        icon="github"
      />
    </AppFlex>
  </AppSection>
</template>
