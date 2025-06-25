<template>
  <div class="hero-tool-links">
    <h3 class="hero-tools-label">Explore knowledge graph tools:</h3>
    <AppLink to="/search-phenotypes">Phenotype Search</AppLink>
    <span>|</span>
    <AppLink to="/text-annotator">Text Annotator</AppLink>
  </div>
</template>

<script setup lang="ts">
  // No logic required right now
</script>

<style scoped lang="scss">
  .hero-tool-links {
    display: flex;
    flex-wrap: nowrap;

    margin-top: 1.8rem;
    gap: 0.75rem;
    font-size: 1.1em;
    white-space: nowrap;
    a {
      color: #007c8a;
      font-weight: 500;
      text-decoration: none;

      &:hover {
        text-decoration: underline;
      }
    }

    span {
      color: #aaa;
    }
    h3 {
      padding: 0;
    }
  }
  .hero-tools-label {
    color: rgb(90, 95, 95);
    font-weight: 500;
    text-align: center;
  }
</style>
