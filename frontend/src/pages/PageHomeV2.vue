<template>
  <AppBreadcrumb />
  <PageTitle id="page-home" title="Welcome to Monarch Initiative" />
  <AppSection width="big" design="bare">
    <p>
      The Monarch Initiative is an international consortium that leads key
      global standards and semantic data integration technologies. Monarch
      resources and integrated data are foundational to many downstream
      applications. We collaborate with stakeholders to continuously improve the
      platform, which is composed of multiple open-source, open-access
      components. Our mission is to enhance data utility, accessibility, and
      transparency to improve rare disease diagnosis and treatment.
    </p>
    <section class="grid">
      <div class="card purple">
        <div class="title">KG</div>
        <div class="subtitle">Visual Representation</div>
      </div>
      <div class="card yellow">
        <div class="title">Ontologies</div>
        <div class="subtitle">Visual Representation</div>
      </div>
      <div class="card pink">
        <div class="title">Technology & Tools...</div>
      </div>
      <div class="card cyan">
        <div class="title">Registries</div>
        <div class="subtitle">&Hubs</div>
      </div>
    </section>
  </AppSection>
</template>

<script setup lang="ts">
import AppBreadcrumb from "@/components/AppBreadcrumb.vue";
import PageTitle from "@/components/ThePageTitle.vue";
</script>

<style lang="scss" scoped>
.section.center {
  gap: 2em;
}
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  width: 100%;
  padding: 1rem;
  gap: 1rem;
}

.card {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 10em;
  padding: 2rem 1rem;
  border-radius: 10px;
  color: #222;
  font-weight: 500;
  font-size: 1.5rem;
  text-align: center;
}

.card .title {
  margin-bottom: 0.3em;
  font-weight: 600;
}

.card .subtitle {
  font-weight: 400;
  font-size: 1.2rem;
}

.purple {
  background: #e3d8fb;
}

.yellow {
  background: #fef0c0;
}

.pink {
  background: #fbd0cc;
}

.cyan {
  background: #d7f8f8;
}
</style>
