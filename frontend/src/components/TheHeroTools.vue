<template>
  <hr />
  <div class="hero-tool-links">
    <AppLink to="/search-phenotypes" class="link"
      >Phenotype Similarity Tools</AppLink
    >
    <!-- <span>|</span> -->
    <AppLink to="/text-annotator" class="link">Text Annotator</AppLink>
    <AppLink to="https://openscientist.io" class="link os-link">
      <OpenScientistLogo class="os-logo" />
      Open Scientist
    </AppLink>
  </div>
</template>

<script setup lang="ts">
import OpenScientistLogo from "@/assets/openscientist-logo.svg";
</script>

<style scoped lang="scss">
$wrap: 1000px;
.hero-tool-links {
  display: flex;

  display: flex;
  flex: 0 0 100%;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 1.1em;
  white-space: normal;
  .link {
    padding: 0.8em;
    border-radius: 0.2em;
    background-color: $theme;
    color: $white;
    font-size: 0.8em;
    @media (max-width: $wrap) {
      background-color: $white;
      color: $theme;
    }
  }

  .os-link {
    display: inline-flex;
    align-items: center;
    gap: 0.45em;
  }

  /* white badge keeps the multi-color logo legible on the teal button */
  .os-logo {
    box-sizing: border-box;
    width: 1.5em;
    height: 1.5em;
    padding: 0.15em;
    border-radius: 50%;
    background-color: $white;
  }

  a {
    font-weight: 500;
    text-decoration: none;

    @media (max-width: $wrap) {
      color: $white;
    }
    &:hover {
      background-color: $theme-light;
      color: $black;
    }
  }

  span {
    color: #aaa;
  }

  @media (max-width: $wrap) {
    flex-wrap: wrap;
    margin-top: 0.8rem;

    font-size: 0.9em;
    white-space: wrap;
  }

  h3 {
    padding: 0;
    @media (max-width: $wrap) {
      color: $white;
    }
  }
}

@media (max-width: $wrap) {
  hr {
    display: none;
  }
}
</style>
