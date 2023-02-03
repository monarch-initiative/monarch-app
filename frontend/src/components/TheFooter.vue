<!--
  footer at bottom of every page
-->

<template>
  <footer class="footer">
    <div class="social">
      <AppLink v-tooltip="'Medium'" to="https://medium.com/@MonarchInit">
        <AppIcon icon="medium" />
      </AppLink>
      <AppLink v-tooltip="'GitHub'" to="https://github.com/monarch-initiative">
        <AppIcon icon="github" />
      </AppLink>
      <AppLink v-tooltip="'Twitter'" to="https://twitter.com/MonarchInit">
        <AppIcon icon="twitter" />
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
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: $theme-dark;
  color: $white;
  font-size: 0.9rem;
  z-index: 10;
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
  font-size: 1.1rem;
  gap: 10px;
}

.social a {
  padding: 5px;
}

.license {
  text-align: center;
  line-height: $spacing;
}

@media (max-width: $wrap) {
  footer {
    flex-direction: column;
    gap: 10px;
  }
}
</style>
