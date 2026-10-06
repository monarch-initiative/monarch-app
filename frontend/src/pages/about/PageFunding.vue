<template>
  <AppBreadcrumb />
  <ThePageTitle id="funding-grants" title="Funding & Grants" />

  <AppSection width="big" class="container">
    <p class="page-description">
      The Monarch Initiative is supported by a range of funding programs that
      enable our research and infrastructure development. Below is a list of
      past and current grants and project awards that contribute to our mission
      of advancing phenomics, genomics, and data integration across species.
    </p>
    <ul class="grants-list">
      <li>
        <strong>
          <AppLink
            to="https://reporter.nih.gov/search/ssAczJr_iE6nByTl22-2Gw/project-details/11421760"
          >
            An AI-powered informatics resource for accelerating NAM research
          </AppLink> </strong
        ><br />
        Office of the Director, National Institutes of Health<br />
        Grant ID: 1R24OD042574
      </li>

      <li>
        <strong>
          <AppLink
            to="https://reporter.nih.gov/search/zv2wiuh1qUe5MzDhRrqcfw/project-details/11265858"
          >
            An explainable AI platform integrating diverse data for enhancing
            rigor, reproducibility, and translatability of animal research
          </AppLink> </strong
        ><br />
        Office of the Director, National Institutes of Health<br />
        Grant ID: 1R24OD039947
      </li>

      <li>
        <strong>
          <AppLink
            to="https://reporter.nih.gov/search/9haLesDQ7kmHdSc_vyBJsw/project-details/11265403"
          >
            Mondo: A community consensus knowledgebase for computational disease
            definitions
          </AppLink> </strong
        ><br />
        National Human Genome Research Institute<br />
        Grant ID: 1U24HG014770
      </li>

      <li>
        <strong>
          Are all diseases n-of-1? Meaningful classification and
          characterization within and across rare diseases </strong
        ><br />
        Chan Zuckerberg Initiative<br />
        Grant ID: DAF2025-367759
      </li>

      <li>
        <strong>LinkML: an open data modeling framework</strong><br />
        Wellcome Trust<br />
        Grant ID: 313291/Z/24/Z
      </li>

      <li>
        <strong>
          <AppLink
            to="https://reporter.nih.gov/search/rGHPmb-5YkCYcrKTFLK0Sw/project-details/10843159"
          >
            Increasing the Yield and Utility of Pediatric Genomic Medicine with
            Exomiser
          </AppLink> </strong
        ><br />
        Eunice Kennedy Shriver National Institute of Child Health and Human
        Development<br />
        Grant ID: 5R01HD103805
      </li>

      <li>
        <strong>
          <AppLink to="https://reporter.nih.gov/project-details/10173498">
            The Monarch Initiative: Linking diseases to model organism resources
          </AppLink> </strong
        ><span class="past-badge">Past Funding</span><br />
        Office of the Director, National Institutes of Health<br />
        Grant ID: 2R24OD011883
      </li>

      <li>
        <strong>
          <AppLink to="https://reporter.nih.gov/project-details/10448140">
            A phenomics-first resource for interpretation of variants
          </AppLink> </strong
        ><span class="past-badge">Past Funding</span><br />
        National Human Genome Research Institute, Center of Excellence in Genome
        Sciences<br />
        Grant ID: 7RM1HG010860
      </li>

      <li>
        <strong>
          <AppLink to="https://reporter.nih.gov/project-details/10269338">
            The Human Phenotype Ontology: Accelerating Computational Integration
            of Clinical Data for Genomics
          </AppLink> </strong
        ><span class="past-badge">Past Funding</span><br />
        National Human Genome Research Institute<br />
        Grant ID: 1U24HG011449
      </li>
    </ul>
  </AppSection>
</template>

<script setup lang="ts">
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import AppLink from "@/components/AppLink.vue";
import ThePageTitle from "@/components/ThePageTitle.vue";
</script>

<style scoped>
.grants-list {
  padding-left: 1.5rem;
  line-height: 1.8;
  list-style-type: disc;
}

.grants-list li {
  margin-bottom: 1.5rem;
}

.page-description {
  color: #444;
  font-size: 1rem;
  line-height: 1.6;
}

.past-badge {
  margin-left: 0.5rem;
  padding: 0.1rem 0.5rem;
  border-radius: 5px;
  background: #eeeeee;
  color: #404040;
  font-size: 0.8rem;
  white-space: nowrap;
}
</style>
