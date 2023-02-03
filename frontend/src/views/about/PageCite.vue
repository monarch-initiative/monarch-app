<!--
  about cite page

  info on how to cite and acknowledge monarch
-->

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
      title="Navigating the Phenotype Frontier: The Monarch Initiative"
      authors="McMurry et al."
      :details="[
        'GENETICS',
        'August 1, 2016 vol. 203 no. 4 1491-1495',
        '10.1534/genetics.116.188870',
      ]"
    />
    <AppCitation
      title="The Monarch Initiative in 2019: an integrative data and analytic platform connecting phenotypes to genotypes across species"
      authors="Shefchek et al."
      :details="[
        'Nucleic Acids Res.',
        '2020 Jan 8; 48 (Database issue): D704–D715. Published online 2019 Nov 08.',
        '10.1093/nar/gkz997',
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
      <AppLink to="/disease/OMIM:154700">OMIM:154700</AppLink>
      as:
    </p>
    <blockquote>
      Monarch Consortium. Accessed 2016-09-22. Marfan Syndrome.
      https://monarchinitiative.org/OMIM:154700
    </blockquote>
  </AppSection>
</template>

<script setup lang="ts">
import AppCitation from "@/components/AppCitation.vue";
</script>
