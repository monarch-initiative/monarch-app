<!--
  team group logo and link
-->

<template>
  <AppLink v-if="src" :to="link || ''" class="group" :aria-label="name">
    <img :src="src" class="image" :alt="name" loading="lazy" />
  </AppLink>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { deburr, kebabCase } from "lodash";

type Props = {
  /** group name */
  name: string;
  /** link to site */
  link?: string;
};

const props = defineProps<Props>();

/** get group img src */
const src = ref("");
watch(
  () => props.name,
  async () => {
    const image = kebabCase(deburr((props.name || "").toLowerCase()));
    try {
      src.value = (await import(`../assets/team/groups/${image}.png`)).default;
    } catch (error) {
      console.error("failed to load team group image", image);
    }
  },
  { immediate: true },
);
</script>

<style lang="scss" scoped>
.image {
  display: block;
  max-width: 100%;
  max-height: 60px;
}
</style>
