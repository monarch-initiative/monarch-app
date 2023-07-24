<!--
  grid container for multiple AppDetail components
-->

<template>
  <div class="details">
    <slot />
  </div>
</template>

<style lang="scss" scoped>
.details {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  width: 100%;
  gap: 30px;
}
</style>
