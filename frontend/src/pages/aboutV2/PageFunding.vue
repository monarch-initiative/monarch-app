<template>
  <AppBreadcrumb />
  <ThePageTitle id="funding-grants" title="Funding & Grants" />

  <AppSection design="bare" width="big" class="container">
    <p class="page-description">
      The Monarch Initiative is supported by a range of federal funding programs
      that enable our research and infrastructure development. Below is a list
      of current grants and project awards that contribute to our mission of
      advancing phenomics, genomics, and data integration across species.
    </p>
    <ul class="grants-list">
      <li>
        <strong>OFFICE OF THE DIRECTOR, NATIONAL INSTITUTES OF HEALTH</strong
        ><br />
        <AppLink to="https://reporter.nih.gov/project-details/10173498">
          The Monarch Initiative: Linking diseases to model organism resources </AppLink
        ><br />
        Grant ID: 2R24OD011883-10A1
      </li>

      <li>
        <strong
          >NATIONAL HUMAN GENOME RESEARCH INSTITUTE, Center of Excellence in
          Genome Sciences</strong
        ><br />
        <AppLink to="https://reporter.nih.gov/project-details/10448140">
          A phenomics-first resource for interpretation of variants </AppLink
        ><br />
        Grant ID: 7RM1HG010860-02
      </li>

      <li>
        <strong>NATIONAL HUMAN GENOME RESEARCH INSTITUTE</strong><br />
        <AppLink to="https://reporter.nih.gov/project-details/10269338">
          The Human Phenotype Ontology: Accelerating Computational Integration
          of Clinical Data for Genomics </AppLink
        ><br />
        Grant ID: 1U24HG011449-01A1
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
</style>
