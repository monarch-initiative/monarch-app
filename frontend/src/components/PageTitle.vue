<template>
  <div class="title-container">
    <div class="heading-container">
      <AppIcon v-if="icon" :icon="icon" :fallback="fallbackIcon" class="icon" />
      <h1>{{ title }}</h1>
    </div>
    <p v-if="tagline" class="tagline">{{ tagline }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  tagline?: string;
  icon?: string;
  id: string;
  fallbackIcon?: string;
}>();
</script>

<style scoped>
/* Wrap both heading and tagline together */
.title-container {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2em;
}

/* Keep heading and icon aligned */
.heading-container {
  display: flex;
  align-items: center;
  gap: 0.5em;
}

/* Make h1 only take as much width as needed */
h1 {
  display: inline-block;
  margin: 0;
  padding: 0;
}

/* Style tagline */
.tagline {
  margin: 0;
  font-size: 0.85em;
}
</style>
