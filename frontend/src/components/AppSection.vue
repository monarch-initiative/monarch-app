<!--
  section that spans width of page and contains, aligns, and evenly vertically
  spaces its contents. all page content should be contained within one of these.
-->

<template>
  <section class="section" :data-width="width" :data-design="design">
    <slot />
  </section>
</template>

<script setup lang="ts">
interface Props {
  /** width of section */
  width?: "full" | "medium" | "big";
  /** visual design */
  design?: "normal" | "fill";
}

withDefaults(defineProps<Props>(), { width: "medium", design: "normal" });
</script>

<style lang="scss" scoped>
.section {
  display: flex;
  align-items: center;
  flex-direction: column;
  gap: 40px;
  text-align: center;
  transition: background $fast;

  &[data-width="full"] {
    padding: 50px 40px;
  }

  &[data-width="medium"] {
    padding: 50px max(40px, calc((100% - $section) / 2));
  }

  &[data-width="big"] {
    padding: 50px max(40px, calc((100% - $section-big) / 2));
  }

  &[data-design="normal"] {
    &:nth-child(odd) {
      background: $white;
    }

    &:nth-child(even) {
      background: $off-white;
    }
  }

  &[data-design="fill"] {
    background: $theme-light;
  }

  &:last-of-type {
    flex-grow: 1;
  }
}
</style>
