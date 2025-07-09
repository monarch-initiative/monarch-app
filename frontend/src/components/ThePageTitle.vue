<template>
  <div :id="id" class="title-container">
    <div class="heading-container">
      <template v-if="imgSrc">
        <AppIcon :icon="imgSrc" />
      </template>

      <h1 :class="{ info: isInfoPage }">{{ title }}</h1>
    </div>
    <p v-if="tagline" class="tagline">{{ tagline }}</p>
  </div>
</template>

<script setup lang="ts">
import AppIcon from "./AppIcon.vue";

defineProps<{
  title: string;
  tagline?: string;
  imgSrc?: string;
  id: string;
  isInfoPage?: boolean;
}>();
</script>

<style lang="scss" scoped>
$wrap: 1000px;

.title-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0px 1.5em;
  gap: 0.5em;
  text-align: center;

  @media (max-width: $wrap) {
    padding: 0.5em 1.5em;
  }
}

.title-container .app-icon {
  width: 4em;
  height: 4em;

  @media (max-width: 768px) {
    width: 3em;
    height: 3em;
  }

  @media (max-width: 480px) {
    width: 2.5em;
    height: 2.5em;
  }

  &.img {
    width: 3.5em;
    height: 3.5em;
  }
}

.heading-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  margin-top: 1em;
  gap: 0.5em;

  h1 {
    margin: 0;
    padding: 0;
    font-size: 1.8em;

    &.info {
      font-size: 2em;
    }

    @media (max-width: 768px) {
      font-size: 1.5em;

      &.info {
        font-size: 1.6em;
      }
    }

    @media (max-width: 480px) {
      font-size: 1.2em;

      &.info {
        font-size: 1.3em;
      }
    }
  }
}

.title-container .app-icon :deep(*) {
  fill: inherit !important;
  color: inherit;
  filter: none !important;
}

.tagline {
  margin: 0;
  color: #666666;
  font-weight: 500;
  font-size: 1rem;

  @media (max-width: 768px) {
    font-size: 0.9rem;
  }

  @media (max-width: 480px) {
    font-size: 0.8rem;
  }
}
</style>
