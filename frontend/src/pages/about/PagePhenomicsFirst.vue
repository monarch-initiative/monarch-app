<!-- 
    Overview page for Phenomics First
 -->

<template>
  <AppSection>
    <AppHeading>Phenomics First</AppHeading>

    <p>
      Understanding genomic variation is key to precision medicine; however,
      despite the ease of sequencing, clinical interpretation is still thwarted
      because available variant-phenotype association data is complex,
      heterogeneous, and disaggregated across sources. Moreover, this evidence
      is sometimes incomplete, conflicting, and erroneous. Consequently,
      clinicians face long lists of candidate diseases, genes, and countless
      variants of unknown significance. Indeed, the efficiency and affordability
      of sequencing data has shifted the bottleneck to interpretation, based
      largely on these phenotype resources.
    </p>
    <p>
      The Monarch Initiative is developing a community Phenomics-First Resource
      (PFR) to advance the emerging field of phenomics; its initial focus will
      be improving the phenotype data that supports variant prioritization in
      genetic disease diagnosis. Our approach is modeled on the Gene Ontology
      (GO). GO is the standard for describing gene function, and it benefits
      from active community use and development. The PFR will provide an
      overarching complementary solution for phenotypes—the higher-level
      outcomes of gene function/dysfunction. Our approach acknowledges the
      complexity of phenomics: currently, curated phenotype data is scattered
      across multiple databases with different standards (exchange formats,
      database schemas, and ontologies). More than 100 organizations curate
      human diseases and their attributes (phenotypes, genes, variants,
      frequency, treatments, etc.); dozens more curate model organism
      phenotypes.
    </p>
    <p>
      The PFR will provide a framework to fundamentally advance and simplify
      computational approaches for interpreting human genome variation. We are
      the creators of the Human Phenotype Ontology which has been the
      cornerstone of our pioneering work in data integration. We will leverage
      this to align phenotype ontologies and clinical terminologies, bringing
      major model species and clinical domains into the PFR, which we will
      refine through continual community partnership. We propose the following
      interlinked approaches that will provide a dynamic suite of
      community-developed knowledge resources to revolutionize variant
      interpretation applications and drive precision medicine.
    </p>
  </AppSection>

  <AppSection design="fill">
    <AppHeading>Phenomics First Goals</AppHeading>

    <p>
      The Phenomics First Resource comprises 3 major sub-components which are
      integrated into a common platform to transform variant interpretation and
      drive precision medicine.
    </p>
    <ul>
      <li>
        Create a community-driven framework of interoperable phenotype
        definitions:
        <br />
        <strong>The Unified Phenotype Ontology (uPheno)</strong>
      </li>
      <li>
        Harmonize human disease definitions:
        <br />
        <strong>The Mondo Disease Ontology</strong>
      </li>
      <li>
        Create a community-wide phenotype exchange standard:
        <br />
        <strong>Phenopackets</strong>
      </li>
    </ul>
  </AppSection>

  <AppSection>
    <figure>
      <img
        src="@/assets/phenomics-first-resource.png"
        alt="Phenomics First Resource Overview"
      />
      <figcaption>
        The
        <AppLink to="https://hpo.jax.org" target="__blank"
          >The Phenomics First Project</AppLink
        >
        (HPO) provides a standardized vocabulary of phenotypic abnormalities
        encountered in human disease.
        <AppLink to="https://pubmed.ncbi.nlm.nih.gov/30476213/" target="__blank"
          >More about HPO...</AppLink
        >
      </figcaption>
    </figure>

    <figure>
      <img
        src="@/assets/phenopackets-ecosystem.png"
        alt="Phenopackets Ecosystem"
      />
      <figcaption>
        <AppLink to="http://phenopackets.org/" target="__blank"
          >Phenopackets</AppLink
        >
        is a standard exchange format for phenotypes and environmental factors.
        This packet of phenotype data can be used anywhere, and can be written
        by anyone. This work is being done in collaboration with the
        <AppLink to="https://www.ga4gh.org/" target="__blank"
          >Global Alliance for Genomics and Health (GA4GH)</AppLink
        >.
      </figcaption>
    </figure>
  </AppSection>

  <AppSection>
    <AppHeading>The Unified Phenotype Ontology (uPheno)</AppHeading>

    <p>
      The Unified Phenotype Ontology (uPheno) is an effort led by the Monarch
      Initiative to integrate phenotype terminologies across species. uPheno has
      to major components: an OWL ontology that imports and deeply integrates
      phenotype ontologies from a variety of species, including Human and
      several major model organisms (such as Drosophila, Zebrafish, Xenopus, C.
      elegans, and Mouse), and a library of phenotype ontology term templates
      that are developed by the
      <AppLink
        to="https://github.com/obophenotype/upheno/wiki/Phenotype-Ontologies-Reconciliation-Effort"
        >Phenotype Ontologies Reconciliation Effort</AppLink
      >.
    </p>
  </AppSection>

  <AppSection>
    <AppHeading>The Mondo Disease Ontology (Mondo)</AppHeading>
    <p>
      The Mondo Disease Ontology (Mondo) aims to harmonize disease definitions
      across the world. It is a semi-automatically constructed ontology that
      merges in multiple disease resources to yield a coherent merged ontology.
      Original versions of Mondo were constructed entirely automatically and
      used the IDs of source databases and ontologies. Later, additional
      manually curated cross-ontology axioms were added, and a native Mondo ID
      system was used to avoid confusion with source databases.
    </p>
    <p>
      You can find more information
      <AppLink to="https://mondo.readthedocs.io/en/latest/" target="__blank"
        >here</AppLink
      >.
    </p>
  </AppSection>

  <AppSection>
    <AppHeading>Phenopackets</AppHeading>
    <p>
      Phenopackets are an open standard for sharing disease and phenotype
      information, with the aim of improving our ability to understand,
      diagnose, and treat both rare and common diseases. A Phenopacket links
      detailed phenotype descriptions with disease, patient, and genetic
      information, enabling clinicians, biologists, and disease and drug
      researchers to build more complete models of disease. The standard is
      designed to encourage wide adoption and synergy between the people,
      organizations and systems that comprise the joint effort to address human
      disease and biological understanding.
    </p>
    <p>
      You can find more information
      <AppLink to="http://phenopackets.org/" target="__blank">here</AppLink>.
    </p>
  </AppSection>
</template>
