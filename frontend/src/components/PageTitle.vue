<template>
  <div class="title-container">
    <div class="heading-container">
      <img v-if="imageSrc" :src="imageSrc" :alt="title" class="title-image" />
      <h1>{{ title }}</h1>
    </div>
    <p v-if="tagline" class="tagline">{{ tagline }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  tagline?: string;
  imageSrc?: string;
  id: string;
}>();
</script>

<style lang="scss" scoped>
$wrap: 1000px;
/* Wrap both heading and tagline together */
.title-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  align-items: center;
  padding: 0px 1.5em;
  text-align: center;
  @media (max-width: $wrap) {
  }
}

/* Keep heading and image aligned */
.heading-container {
  display: flex;
  align-items: center;
  gap: 0.5em;
}

/* Ensure the image is properly styled */
.title-image {
  width: 40px; /* Adjust as needed */
  max-height: 40px;
  object-fit: contain;
}

/* Style heading */
h1 {
  margin: 0;
  font-size: 2em;
}

/* Style tagline */
.tagline {
  margin: 0;
  color: hsl(185, 100%, 30%);
  font-weight: 500;
  font-size: 1rem;
}
</style>
