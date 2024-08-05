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
    <slot />
    <div class="title">{{ title }}</div>
    <div v-if="subtitle" class="subtitle">{{ subtitle }}</div>
  </div>
</template>

<script setup lang="ts">
type Props = {
  /** where to link to */
  to?: string;
  /** icon to show in button */
  icon?: string;
  /** main text */
  title: string;
  /** secondary text */
  subtitle?: string;
  /** visual design */
  design?: "extra-small" | "small" | "big";
};

withDefaults(defineProps<Props>(), {
  to: "",
  icon: "",
  subtitle: "",
  design: "big",
});
</script>

<style lang="scss" scoped>
.tile {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  width: 200px;
  gap: 15px;
}

.button {
  font-size: 2rem;
}

.icon {
  height: 80px;
  color: $off-black;
}

.tile.small {
  width: 160px;
  gap: 10px;

  .button {
    font-size: 1.4rem;
  }

  .icon {
    height: 40px;
  }
}

.tile.extra-small {
  width: 160px;
  gap: 10px;

  .title {
    font-size: 1rem;
  }

  .button {
    font-size: 1.2rem;
  }

  .icon {
    height: 20px;
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
