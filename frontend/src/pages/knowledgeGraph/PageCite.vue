<template>
  <AppBreadcrumb />
  <PageTitle id="kg-cite" title="Citation Guide for Knowledge Graph & Tools" />
  <div class="container">
    <AppSection width="big" design="bare" class="citation">
      <AppHeading level="2">Acknowledgement</AppHeading>
      <p>
        If you use Monarch, please acknowledge us with a paragraph like the
        following:
      </p>
      <p class="content">
        <code>YOUR WORK</code> uses and displays data and algorithms from the
        Monarch Initiative. The Monarch Initiative
        (https://monarchinitiative.org) makes biomedical knowledge exploration
        more efficient and effective by providing tools for genotype-phenotype
        analysis, genomic diagnostics, and precision medicine across broad areas
        of disease.
      </p>
    </AppSection>

    <AppSection width="big" design="bare" class="citation">
      <AppHeading level="2">In Publications</AppHeading>
      <p>
        To cite the use of Monarch in publications, please use these two
        references:
      </p>
      <AppCitation
        class="content"
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
    <AppSection width="big" design="bare" class="citation">
      <AppHeading level="2">Data or Result</AppHeading>

      <p class="content">
        <span>
          Because most of the association content in Monarch comes from external
          sources, please cite the original database records (e.g.
          <b
            ><AppLink to="http://www.informatics.jax.org/accession/MGI:1915196"
              >MGI:1915196</AppLink
            ></b
          >) or the original publications (e.g. PMID:25605924) where possible. </span
        ><br />
        <span>
          The data in Monarch is constantly expanding and improving. The data is
          versioned with each database release, and archived database releases
          are available upon request. The evolution of individual records in
          Monarch is not currently tracked. More documentation about our
          identifiers can be found
          <AppLink
            to="https://github.com/monarch-initiative/dipper/blob/master/README.md#identifiers"
            >on GitHub</AppLink
          >.
        </span>
      </p>
    </AppSection>

    <!-- citing data -->
    <AppSection width="big" design="bare">
      <AppHeading level="2">Page or Algorithmic Results</AppHeading>
      <p>
        To link to a specific page or to algorithmic results presented on this
        website, please use the URL in your browser's address bar. For example,
        you would cite the prefixed identifier
        <AppLink to="/MONDO:0007523">MONDO:0007523</AppLink>
        as:
      </p>
      <p class="content">
        Ehlers-Danlos syndrome, hypermobility type.
        https://monarchinitiative.org/MONDO:0007523
      </p>
    </AppSection>
  </div>

  <!--contact-->
  <AppSection width="big" design="bare">
    <p class="info">
      If you have any questions, feel free to reach out to us at :
      <AppLink to="mailto:info@monarchinitiative.org"
        >info@monarchinitiative.org</AppLink
      >
    </p></AppSection
  >
</template>
<script setup lang="ts">
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import AppCitation from "@/components/AppCitation.vue";
import PageTitle from "@/components/PageTitle.vue";
</script>
<style lang="scss" scoped>
$wrap: 1000px;
.section.center[data-v-d078f057] {
  gap: 0.7em;
}

.section.big {
  padding-bottom: unset;
  @media (max-width: $wrap) {
    padding: 0 max(20px, (100% - 1200px) / 2);
  }
}
.content {
  padding: 1.3em;
  background: #a6ecf257;
  text-align: center;
}
.container {
  display: flex;
  flex-direction: column;
}

.info {
  padding: 1em;
}
</style>
