<template>
  <AppBreadcrumb />
  <PageTitle id="our-story" title="Our Story" />
  <p class="tagline">
    Innovating with Purpose: Translating Data into, Breakthroughs for Rare
    Disease.
  </p>
  <AppSection width="big" class="our-story">
    <AppHeading class="fullWidthHeader"> Overview </AppHeading>
    <p>
      The Monarch Initiative is an international consortium that leads key
      global standards and semantic data integration technologies. Monarch
      resources and integrated data are foundational to many downstream
      applications. We collaborate with stakeholders to continuously improve the
      platform, which is composed of multiple open-source, open-access
      components. Our mission is to enhance data utility, accessibility, and
      transparency to improve rare disease diagnosis and treatment.
    </p>
  </AppSection>

  <AppSection width="big">
    <AppHeading class="fullWidthHeader"> Mission Statement </AppHeading>
    <p>
      The Monarch Initiative integrates and interprets biomedical data to
      advance precision medicine and diagnostics. By integrating knowledge using
      ontologies and AI, we promote an open ecosystem of multi-species data and
      standards to accelerate rare disease diagnosis and care.
    </p>
  </AppSection>

  <AppSection width="big">
    <AppHeading class="fullWidthHeader"> Core Values </AppHeading>
    <div class="core-values-wrapper">
      <ul class="column">
        <li>Open Science Ecosystem</li>
        <li>Advancing Diagnosis for Rare Disease Patients</li>
        <li>Harnessing Multi-species Data</li>
      </ul>
      <ul class="column">
        <li>Translational Data Standardization</li>
        <li>Ontology-based Harmonization</li>
      </ul>
    </div>
  </AppSection>

  <AppSection width="big">
    <AppHeading class="fullWidthHeader"> Impact </AppHeading>
    <p>
      The Monarch Initiative enables cross-species integration of biomedical
      data, supporting translational research and phenotype-driven diagnostics.
      Our ontologies, like the Mondo Disease Ontology, standardize
      genotype-phenotype data, aiding both clinical and research communities.
      Monarch contributes to global initiatives such as GA4GH and WHO to shape
      best practices for data interoperability and patient care.
    </p>
  </AppSection>

  <AppSection width="big">
    <AppHeading class="fullWidthHeader"> Join Us! </AppHeading>
    <p>
      We invite scientists, engineers, clinicians, patients, and advocates to
      join our community in advancing rare disease diagnosis and treatment.
      Connect with us via the Community dropdown at the top of this page, or
      email
      <a href="mailto:info@monarchinitiative.org">info@monarchinitiative.org</a
      >.
    </p>
  </AppSection>
</template>
<script setup lang="ts">
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import PageTitle from "@/components/ThePageTitle.vue";

defineProps<{
  imageSrc: string;
}>();
</script>
<style lang="scss" scoped>
$wrap: 1000px;

.section.big {
  padding-top: unset;
}

.section.center {
  gap: 1em;

  @media (max-width: $wrap) {
    gap: 1.5em;
  }
}

.our-story {
  margin-top: 0.7em;
  @media (max-width: $wrap) {
    padding-top: 0.7em;
  }
}

.fullWidthHeader {
  width: 100%;
  padding: 0.4em 0.5em;
  background-color: #d3e6eb;
  color: black;
  text-align: left;
}

h2 {
  margin-bottom: 0.5rem;
  color: #2c3e50;
  font-size: 1.4rem;
}

ul {
  padding-left: 1.5rem;
  list-style-type: disc;
}

.tagline {
  position: relative;
  max-width: 800px;
  margin: 0.5em auto 1em auto;
  padding: 0 1rem;
  font-weight: 500;
  font-size: 1.1rem;
  text-align: center;

  @media (max-width: $wrap) {
    margin: 0;
  }
}

.core-values-wrapper {
  display: flex;
  justify-content: start;
  width: 100%;

  @media (max-width: 768px) {
    flex-direction: column;
  }
}

.column {
  padding-left: 1.5rem;
  list-style: none;

  li {
    position: relative;
    margin-bottom: 1rem;
    padding-left: 2rem;

    @media (max-width: 768px) {
      margin-bottom: 0.1rem;
    }

    &::before {
      position: absolute;
      left: 0;
      content: "→";
      color: #0b7285;
      font-weight: bold;
    }
  }
}
</style>
