<template>
  <AppBreadcrumb />
  <PageTitle id="our-story" title="Our Story" />

  <AppSection width="big" design="bare">
    <img class="story-image" src="@/assets/our-story.png" alt="timeline" />

    <!-- Headline -->
    <div class="headline">
      <p>Innovating with Purpose:</p>
      <p>Translating Data into,</p>
      <p>Breakthroughs for Rare Disease.</p>
    </div>
    <hr class="section-divider" />

    <!-- Body Text -->
    <div class="body-text">
      <article class="section">
        <h2>Overview</h2>
        <p>
          The Monarch Initiative is an international consortium that leads key
          global standards and semantic data integration technologies. Monarch
          resources and integrated data are foundational to many downstream
          applications. We collaborate with stakeholders to continuously improve
          the platform, which is composed of multiple open-source, open-access
          components. Our mission is to enhance data utility, accessibility, and
          transparency to improve rare disease diagnosis and treatment.
        </p>
      </article>

      <article class="section">
        <h2>Mission Statement</h2>
        <p>
          The Monarch Initiative integrates and interprets biomedical data to
          advance precision medicine and diagnostics. By integrating knowledge
          using ontologies and AI, we promote an open ecosystem of multi-species
          data and standards to accelerate rare disease diagnosis and care.
        </p>
      </article>

      <article class="section">
        <h2>Core Values</h2>
        <ul>
          <li>Open Science Ecosystem</li>
          <li>Advancing Diagnosis for Rare Disease Patients</li>
          <li>Harnessing Multi-species Data</li>
          <li>Translational Data Standardization</li>
          <li>Ontology-based Harmonization</li>
        </ul>
      </article>

      <article class="section">
        <h2>Impact</h2>
        <p>
          The Monarch Initiative enables cross-species integration of biomedical
          data, supporting translational research and phenotype-driven
          diagnostics. Our ontologies, like the Mondo Disease Ontology,
          standardize genotype-phenotype data, aiding both clinical and research
          communities. Monarch contributes to global initiatives such as GA4GH
          and WHO to shape best practices for data interoperability and patient
          care.
        </p>
      </article>

      <article class="section">
        <h2>Join Us!</h2>
        <p>
          We invite scientists, engineers, clinicians, patients, and advocates
          to join our community in advancing rare disease diagnosis and
          treatment. Connect with us via the Community dropdown at the top of
          this page, or email
          <a href="mailto:info@monarchinitiative.org"
            >info@monarchinitiative.org</a
          >.
        </p>
      </article>
    </div>
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
.section.center {
  gap: 10px;
}

.headline {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #767b3c;
  font-size: 1.1rem;
  text-align: center;
}

.body-text {
  color: #333;
  font-size: 1rem;
  line-height: 1.7;
}

.body-text p {
  margin-bottom: 1rem;
}

.story-image {
  display: block;
  width: 100%;
  max-width: 840px;
  margin: 0 auto 5rem;
  border-radius: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.about-monarch {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem 1rem;
  line-height: 1.6;
  font-family: sans-serif;
}

.section {
  margin-bottom: 2rem;
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

a {
  color: #007acc;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

hr.section-divider {
  width: 50%;
  height: 2px;
  border: none;
  background-color: #656e1f;
}
</style>
