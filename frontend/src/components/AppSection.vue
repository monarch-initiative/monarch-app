<!--
  section that spans width of page and contains, aligns, and evenly vertically
  spaces its contents. all page content should be contained within one of these.
-->

<template>
  <section :class="['section', width, design, alignment, { inset }]">
    <slot />
  </section>
</template>

<script setup lang="ts">
type Props = {
  /** width of section */
  width?: "full" | "medium" | "big";
  /** visual design */
  design?: "normal" | "fill" | "bare";
  alignment?: "left" | "center";
  inset?: boolean;
};

withDefaults(defineProps<Props>(), {
  width: "medium",
  design: "normal",
  alignment: "center",
  inset: false,
});

type Slots = {
  default: () => unknown;
};

defineSlots<Slots>();
</script>

<style lang="scss" scoped>
.section {
  display: flex;
  flex-direction: column;
  transition: background $fast;
  &.center {
    align-items: center;
    gap: 40px;
    text-align: center;
  }

  &.left {
    align-items: flex-start;
    gap: 20px;
    text-align: left;
  }

  &.full {
    padding: 30px 20px;
  }

  &.inset {
    padding: 30px 20px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  }

  &.left {
    margin: 10px 20px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  }

  &.medium {
    &.center {
      padding: 30px max(20px, calc((100% - $section) / 2));
    }
    &.left {
      padding: 5px 15px;
    }
  }

  &.big {
    padding: 30px 20px;
    //padding: 30px max(20px, calc((100% - $section-big) / 2));
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
