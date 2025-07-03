<template>
  <hr />
  <div class="hero-tool-links">
    <p class="hero-tools-label">Knowledge Graph Tools:</p>
    <AppLink to="/search-phenotypes">Phenotype Similarity Tools</AppLink>
    <span>|</span>
    <AppLink to="/text-annotator">Text Annotator</AppLink>
  </div>
</template>

<style scoped lang="scss">
$wrap: 1120px;
.hero-tool-links {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.1em;
  white-space: nowrap;

  @media (max-width: $wrap) {
    flex-wrap: wrap;
    margin-top: 0.8rem;
    color: $white;
    font-size: 0.9em;
    white-space: wrap;
  }
  a {
    color: #007c8a;
    font-weight: 500;
    text-decoration: none;

    @media (max-width: $wrap) {
      color: $white;
    }
    &:hover {
      text-decoration: underline;
    }
  }

  span {
    color: #aaa;
  }
  h3 {
    padding: 0;

    @media (max-width: $wrap) {
      color: $white;
    }
  }
}
.hero-tools-label {
  font-weight: 500;
  text-align: center;
  @media (max-width: $wrap) {
    color: $white;
  }
}
</style>
