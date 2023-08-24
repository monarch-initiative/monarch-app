<!--
  section that spans width of page and contains, aligns, and evenly vertically
  spaces its contents. all page content should be contained within one of these.
-->

<template>
  <section :class="['section', width, design]">
    <slot />
  </section>
</template>

<script setup lang="ts">
type Props = {
  /** width of section */
  width?: "full" | "medium" | "big";
  /** visual design */
  design?: "normal" | "fill";
};

withDefaults(defineProps<Props>(), { width: "medium", design: "normal" });

type Slots = {
  default: () => unknown;
};

defineSlots<Slots>();
</script>

<style lang="scss" scoped>
.section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 40px;
  text-align: center;
  transition: background $fast;

  &.full {
    padding: 50px 40px;
  }

  &.medium {
    padding: 50px max(40px, calc((100% - $section) / 2));
  }

  &.big {
    padding: 50px max(40px, calc((100% - $section-big) / 2));
  }

  &.normal {
    &:nth-child(odd) {
      background: $white;
    }

    &:nth-child(even) {
      background: $off-white;
    }
  }

  &.fill {
    background: $theme-light;
  }

  &:last-of-type {
    flex-grow: 1;
  }
}
</style>
