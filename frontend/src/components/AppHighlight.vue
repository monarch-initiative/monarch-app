<!--
  video and text to show off a feature
-->

<template>
  <div class="highlight">
    <video :src="src" muted autoplay loop controls></video>
    <p>
      <slot />
    </p>
  </div>
</template>

<script setup lang="ts">
interface Props {
  /** source of video */
  src: string;
}

defineProps<Props>();
</script>

<style lang="scss" scoped>
.highlight {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 40px;
  width: 100%;
  margin: 20px 0;

  &:nth-child(even) {
    flex-direction: row-reverse;
  }

  @media (max-width: 800px) {
    flex-direction: column !important;
  }

  video {
    width: 100%;
    max-width: 360px;
    box-shadow: $shadow;
  }

  p {
    flex-grow: 1;
  }
}
</style>
