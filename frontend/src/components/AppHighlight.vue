<!--
  video and text to show off a feature
-->

<template>
  <div class="highlight">
    <video :src="src" muted :autoplay="os.name !== 'iOS'" loop controls></video>
    <p>
      <slot />
    </p>
  </div>
</template>

<script setup lang="ts">
// import parser from "ua-parser-js";
import { UAParser } from "ua-parser-js";

// const { os } = parser();
const { os } = new UAParser().getResult();
console.log({ os });

type Props = {
  /** source of video */
  src: string;
};

defineProps<Props>();

type Slots = {
  default: () => unknown;
};

defineSlots<Slots>();
</script>

<style lang="scss" scoped>
.highlight {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  margin: 20px 0;
  gap: 40px;

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
