<template>
  <hr />
  <div class="hero-tool-links">
    <AppLink to="/search-phenotypes" class="link"
      >Phenotype Similarity Tools</AppLink
    >
    <!-- <span>|</span> -->
    <AppLink to="/text-annotator" class="link">Text Annotator</AppLink>
  </div>
</template>

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
