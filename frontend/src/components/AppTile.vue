<!--
  big circular link button with text and sub text
-->

<template>
  <div class="tile" :data-design="design">
    <AppButton
      v-if="to"
      design="circle"
      :to="to"
      class="button"
      :icon="icon"
      :aria-label="title"
    />
    <AppIcon v-else-if="icon" class="icon" :icon="icon" />
    <div class="title">{{ title }}</div>
    <div v-if="subtitle" class="subtitle">{{ subtitle }}</div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  /** where to link to */
  to?: string;
  /** icon to show in button */
  icon: string;
  /** main text */
  title: string;
  /** secondary text */
  subtitle?: string;
  /** visual design */
  design?: "small" | "big";
}

withDefaults(defineProps<Props>(), { to: "", subtitle: "", design: "big" });
</script>

<style lang="scss" scoped>
.tile {
  display: inline-flex;
  align-items: center;
  flex-direction: column;
  gap: 15px;
  width: 200px;
}

.button {
  font-size: 2rem;
}

.icon {
  height: 80px;
  color: $off-black;
}

.tile[data-design="small"] {
  width: 160px;
  gap: 10px;

  .button {
    font-size: 1.4rem;
  }

  .icon {
    height: 40px;
  }
}

.title {
  font-size: 1.1rem;
  line-height: $spacing;
}

.subtitle {
  color: $off-black;
  line-height: $spacing;
  margin-top: -5px;
}
</style>
