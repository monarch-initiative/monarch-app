<!-- 
    Overview page for Phenomics First
 -->

<template>
  <AppSection>
    <AppHeading>Phenomics First</AppHeading>

    <div class="container-fluid monarch-view monarch-about-view">
      <div class="col-12">
        <p>
          Understanding genomic variation is key to precision medicine; however,
          despite the ease of sequencing, clinical interpretation is still
          thwarted because available variant-phenotype association data is
          complex, heterogeneous, and disaggregated across sources. Moreover,
          this evidence is sometimes incomplete, conflicting, and erroneous.
          Consequently, clinicians face long lists of candidate diseases, genes,
          and countless variants of unknown significance. Indeed, the efficiency
          and affordability of sequencing data has shifted the bottleneck to
          interpretation, based largely on these phenotype resources.
          <br /><br />
          The Monarch Initiative is developing a community Phenomics-First
          Resource (PFR) to advance the emerging field of phenomics; its initial
          focus will be improving the phenotype data that supports variant
          prioritization in genetic disease diagnosis. Our approach is modeled
          on the Gene Ontology (GO). GO is the standard for describing gene
          function, and it benefits from active community use and development.
          The PFR will provide an overarching complementary solution for
          phenotypes—the higher-level outcomes of gene function/dysfunction. Our
          approach acknowledges the complexity of phenomics: currently, curated
          phenotype data is scattered across multiple databases with different
          standards (exchange formats, database schemas, and ontologies). More
          than 100 organizations curate human diseases and their attributes
          (phenotypes, genes, variants, frequency, treatments, etc.); dozens
          more curate model organism phenotypes. <br /><br />
          The PFR will provide a framework to fundamentally advance and simplify
          computational approaches for interpreting human genome variation. We
          are the creators of the Human Phenotype Ontology which has been the
          cornerstone of our pioneering work in data integration. We will
          leverage this to align phenotype ontologies and clinical
          terminologies, bringing major model species and clinical domains into
          the PFR, which we will refine through continual community partnership.
          We propose the following interlinked approaches that will provide a
          dynamic suite of community-developed knowledge resources to
          revolutionize variant interpretation applications and drive precision
          medicine.
        </p>
      </div>

      <div class="goals-banner offset-2 col-8">
        <h3 id="our-goals"><strong>Phenomics First Goals</strong></h3>
        <br />
        <p>
          The Phenomics First Resource comprises 3 major sub-components which
          are integrated into a common platform to transform variant
          interpretation and drive precision medicine.
        </p>
        <ul>
          <li>
            Create a community-driven framework of interoperable phenotype
            definitions: The Unified Phenotype Ontology (uPheno)
          </li>
          <li>
            Harmonize human disease definitions: the Mondo Disease Ontology
          </li>
          <li>
            Create a community-wide phenotype exchange standard: Phenopackets
          </li>
        </ul>
      </div>

      <div class="row">
        <div class="col-12 col-lg-6">
          <figure class="ecosystems">
            <img
              src="@/assets/pfr.png"
              alt="Phenomics First Resource Overview"
            />
            <figcaption>
              Fig 3. The
              <a href="https://hpo.jax.org" target="__blank"
                >The Phenomics First Project</a
              >
              (HPO) provides a standardized vocabulary of phenotypic
              abnormalities encountered in human disease.
              <a
                href="https://pubmed.ncbi.nlm.nih.gov/30476213/"
                target="__blank"
                >More about HPO...</a
              >
            </figcaption>
          </figure>
          <!-- </div>
        <div class="col-12 col-lg-6"> -->
          <figure class="ecosystems phenopackets">
            <img
              src="@/assets/phenopackets-ecosystem.png"
              alt="Phenopackets Ecosystem"
            />
            <figcaption>
              Fig 4.
              <a href="http://phenopackets.org/" target="__blank"
                >Phenopackets</a
              >
              is a standard exchange format for phenotypes and environmental
              factors. This packet of phenotype data can be used anywhere, and
              can be written by anyone. This work is being done in collaboration
              with the
              <a href="https://www.ga4gh.org/" target="__blank"
                >Global Alliance for Genomics and Health (GA4GH)</a
              >.
            </figcaption>
          </figure>
        </div>
      </div>

      <div>
        <h3>The Unified Phenotype Ontology (uPheno)</h3>
        <br />
        <p>
          The Unified Phenotype Ontology (uPheno) is an effort led by the
          Monarch Initiative to integrate phenotype terminologies across
          species. uPheno has to major components: an OWL ontology that imports
          and deeply integrates phenotype ontologies from a variety of species,
          including Human and several major model organisms (such as Drosophila,
          Zebrafish, Xenopus, C. elegans, and Mouse), and a library of phenotype
          ontology term templates that are developed by the
          <a
            href="https://github.com/obophenotype/upheno/wiki/Phenotype-Ontologies-Reconciliation-Effort"
            >Phenotype Ontologies Reconciliation Effort</a
          >.
        </p>
      </div>

      <div>
        <h3>The Mondo Disease Ontology (Mondo)</h3>
        <br />
        <p>Under construction.</p>
      </div>

      <div>
        <h3>Phenopackets</h3>
        <br />
        <p>Under construction.</p>
      </div>

      <div>
        <h3>The Phenomics First Resource</h3>
        <br />
        <p>Under construction.</p>
      </div>
    </div>
    <!-- end container -->
  </AppSection>
</template>

<script setup lang="ts">
import AppSection from "@/components/AppSection.vue";
</script>

<style lang="scss" scoped>
// @import "@/style/variables";

// variables
$monarch-bg-color: #2a4d69;
$monarch-button-color: #0b556b;
$grid-float-breakpoint: 600px;

.container-fluid.monarch-view.monarch-about-view {
  h1,
  h2,
  h3,
  h4,
  h5,
  h6 {
    clear: both;
  }

  .monarch-hr {
    border-top-width: 2px;
    border-top-color: $monarch-bg-color;
  }

  .goals-banner {
    height: auto;
    margin-top: 25px;
    padding: 20px;
    border-radius: 0.5rem;
    background-color: $monarch-bg-color;
    color: white;
    text-align: center;
  }
  figure {
    margin: 0 auto;
  }

  figure {
    display: table;

    &.ecosystems {
      img {
        max-width: 100%;
      }
      &.phenopackets img {
        max-width: 100%;
      }
    }
    img {
      width: 100%;
      height: auto;
      padding: 15px;
    }
  }

  figcaption {
    word-wrap: normal;
    display: table-caption;
    width: 80%;
    padding: 0 10px 5px;
    font-size: 12px;
    line-height: 16px;
    text-align: justify;
    caption-side: bottom;
  }

  table {
    margin: auto;
    text-align: center;
    td a img {
      max-width: 120px;
      margin: 5px;
    }

    @media (min-width: $grid-float-breakpoint) {
      td a img {
        max-width: 200px;
      }
    }
  }
}
</style>
