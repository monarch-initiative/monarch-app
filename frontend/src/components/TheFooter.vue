<!--
  footer at bottom of every page
-->

<template>
  <footer class="footer">
    <div class="social">
      <AppLink v-tooltip="'Subscribe'"
        to="https://groups.google.com/g/monarch-friends/"
      >
        <AppIcon icon="envelope" />
      </AppLink>
      <AppLink v-tooltip="'Medium'" to="https://medium.com/@MonarchInit">
        <AppIcon icon="medium" />
      </AppLink>
      <AppLink v-tooltip="'GitHub'" to="https://github.com/monarch-initiative">
        <AppIcon icon="github" />
      </AppLink>
      <AppLink
        v-tooltip="'YouTube'"
        to="https://www.youtube.com/@monarchinitiative"
      >
        <AppIcon icon="youtube" />
      </AppLink>
      <AppLink
        v-tooltip="'LinkedIn'"
        to="https://www.linkedin.com/company/the-monarch-initiative"
      >
        <AppIcon icon="linkedin" />
      </AppLink>
    </div>
    <div class="license">
      <span>Monarch Intiative {{ new Date().getFullYear() }}</span>
      <span>&nbsp; · &nbsp;</span>
      <AppLink to="/terms" class="license">BSD-3</AppLink>
    </div>
  </footer>
</template>

<style lang="scss" scoped>
$wrap: 500px;

.footer {
  display: flex;
  z-index: 1010;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  background: $theme;
  color: $white;
  font-size: 0.9rem;
}

a {
  color: $white;
  transition: opacity $fast;

  &:hover {
    opacity: 0.5;
  }
}

.social {
  display: flex;
  gap: 10px;
  font-size: 1.1rem;
}

.social a {
  padding: 5px;
}

.license {
  line-height: $spacing;
  text-align: center;
}

@media (max-width: $wrap) {
  footer {
    flex-direction: column;
    gap: 10px;
  }
}
</style>
