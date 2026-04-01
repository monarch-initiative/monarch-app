<template>
  <AppBreadcrumb />
  <PageTitle id="kg-cite" title="Citation Guide for Knowledge Graph & Tools" />
  <div class="container">
    <AppSection width="big" class="citation">
      <AppHeading :level="2">Acknowledgement</AppHeading>
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

    <AppSection width="big" class="citation">
      <AppHeading :level="2">In Publications</AppHeading>
      <p>
        To cite the use of Monarch in publications, please use this reference:
      </p>
      <p class="content">
        Tim E Putman, Kevin Schaper, Nicolas Matentzoglu, Vincent P Rubinetti,
        Faisal S Alquaddoomi, Corey Cox, J Harry Caufield, Glass Elsarboukh,
        Sarah Gehrke, Harshad Hegde, Justin T Reese, Ian Braun, Richard M
        Bruskiewich, Luca Cappelletti, Seth Carbon, Anita R Caron, Lauren E
        Chan, Christopher G Chute, Katherina G Cortes, Vinícius De Souza,
        Tommaso Fontana, Nomi L Harris, Emily L Hartley, Eric Hurwitz, Julius O
        B Jacobsen, Madan Krishnamurthy, Bryan J Laraway, James A McLaughlin,
        Julie A McMurry, Sierra A T Moxon, Kathleen R Mullen, Shawn T O’Neil,
        Kent A Shefchek, Ray Stefancsik, Sabrina Toro, Nicole A Vasilevsky,
        Ramona L Walls, Patricia L Whetzel, David Osumi-Sutherland, Damian
        Smedley, Peter N Robinson, Christopher J Mungall, Melissa A Haendel,
        Monica C Munoz-Torres, The Monarch Initiative in 2024: an analytic
        platform integrating phenotypes, genes and diseases across species,
        Nucleic Acids Research, Volume 52, Issue D1, 5 January 2024, Pages
        D938–D949,
        <AppLink to="https://doi.org/10.1093/nar/gkad1082"
          >https://doi.org/10.1093/nar/gkad1082</AppLink
        >.
      </p>
    </AppSection>

    <!-- citing data -->
    <AppSection width="big" class="citation">
      <AppHeading :level="2">Data or Result</AppHeading>

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
    <AppSection width="big">
      <AppHeading :level="2">Page or Algorithmic Results</AppHeading>
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
  <AppSection width="big">
    <p class="info">
      If you have any questions, feel free to reach out to us at :
      <AppLink to="mailto:info@monarchinitiative.org" :no-icon="true"
        >info@monarchinitiative.org</AppLink
      >
    </p>
    <p class="license-note">
      Monarch Initiative 2025 — Released under the
      <AppLink :no-icon="true" to="https://opensource.org/licenses/BSD-3-Clause"
        >BSD 3-Clause License</AppLink
      >.
    </p>
  </AppSection>
</template>
<script setup lang="ts">
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import PageTitle from "@/components/ThePageTitle.vue";
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
p {
  text-align: left;
}
.license-note {
  margin-bottom: 1em;
  color: #444;
  font-size: 0.9em;
  text-align: center;
}
</style>
