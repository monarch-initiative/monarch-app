<!--
  about cite page
  
  info on how to cite and acknowledge monarch
-->

<!-- eslint-disable max-len -->
<template>
  <AppSection>
    <AppHeading>Cite</AppHeading>
  </AppSection>

  <!-- general acknowledgement -->
  <AppSection>
    <AppHeading>Acknowledgement</AppHeading>
    <p>
      If you use Monarch, please acknowledge us with a paragraph like the
      following:
    </p>
    <blockquote>
      <code>YOUR WORK</code> uses and displays data and algorithms from the
      Monarch Initiative. The Monarch Initiative (https://monarchinitiative.org)
      makes biomedical knowledge exploration more efficient and effective by
      providing tools for genotype-phenotype analysis, genomic diagnostics, and
      precision medicine across broad areas of disease.
    </blockquote>
  </AppSection>

  <!-- typical citing -->
  <AppSection>
    <AppHeading>In Publications</AppHeading>
    <p>
      To cite the use of Monarch in publications, please use these two
      references:
    </p>
    <AppCitation
      title="The Monarch Initiative in 2024: an analytic platform integrating phenotypes, genes and diseases across species"
      authors="Putman et al."
      :details="[
        'Nucleic Acids Research',
        '2024 Jan 5; Volume 52, Issue D1: D938–D949. Published online 2023, November 24.',
        '10.1093/nar/gkad1082',
      ]"
    />
  </AppSection>

  <!-- citing data -->
  <AppSection>
    <AppHeading>Data or Result</AppHeading>
    <p>
      Because most of the association content in Monarch comes from external
      sources, please cite the original database records (e.g.
      <AppLink to="http://www.informatics.jax.org/accession/MGI:1915196"
        >MGI:1915196</AppLink
      >) or the original publications (e.g. PMID:25605924) where possible.
    </p>
    <p>
      The data in Monarch is constantly expanding and improving. The data is
      versioned with each database release, and archived database releases are
      available upon request. The evolution of individual records in Monarch is
      not currently tracked. More documentation about our identifiers can be
      found
      <AppLink
        to="https://github.com/monarch-initiative/dipper/blob/master/README.md#identifiers"
        >on GitHub</AppLink
      >.
    </p>
  </AppSection>

  <!-- citing pages -->
  <AppSection>
    <AppHeading>Page or Algorithmic Results</AppHeading>
    <p>
      To link to a specific page or to algorithmic results presented on this
      website, please use the URL in your browser's address bar. For example,
      you would cite the prefixed identifier
      <AppLink to="/MONDO:0007523">MONDO:0007523</AppLink>
      as:
    </p>
    <blockquote>
      Ehlers-Danlos syndrome, hypermobility type.
      https://monarchinitiative.org/MONDO:0007523
    </blockquote>
  </AppSection>
</template>

<script setup lang="ts">
import AppCitation from "@/components/AppCitation.vue";
</script>
