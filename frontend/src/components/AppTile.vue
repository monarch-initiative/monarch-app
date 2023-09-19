<!--
  big link button with text and sub text
-->

<template>
  <div :class="['tile', design]">
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
type Props = {
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
};

withDefaults(defineProps<Props>(), { to: "", subtitle: "", design: "big" });
</script>

<style lang="scss" scoped>
.tile {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
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

.tile.small {
  gap: 10px;
  width: 160px;

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
  margin-top: -5px;
  color: $off-black;
  line-height: $spacing;
}
</style>
