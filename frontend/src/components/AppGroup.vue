<!--
  team group logo and link
-->

<template>
  <AppLink
    v-if="name && link"
    :to="link || ''"
    class="group"
    :aria-label="name"
  >
    <img v-if="src" :src="src" class="image" :alt="name" loading="lazy" />
  </AppLink>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { kebabCase, deburr } from "lodash";

interface Props {
  /** group name */
  name: string;
  /** link to site */
  link?: string;
}

const props = defineProps<Props>();

/** get group img src */
const src = computed(() => {
  const image = kebabCase(deburr((props.name || "").toLowerCase()));
  try {
    return require(`@/assets/team/groups/${image}.png`);
  } catch (error) {
    return "";
  }
});
</script>

<style lang="scss" scoped>
.image {
  display: block;
  max-width: 100%;
  max-height: 60px;
}
</style>
