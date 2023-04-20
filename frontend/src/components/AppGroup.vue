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
import { ref, watch } from "vue";
import { deburr, kebabCase } from "lodash";

type Props = {
  /** Group name */
  name: string;
  /** Link to site */
  link?: string;
};

const props = defineProps<Props>();

/** Get group img src */
const src = ref("");
watch(
  () => props.name,
  async () => {
    const image = kebabCase(deburr((props.name || "").toLowerCase()));
    try {
      src.value = (await import(`../assets/team/groups/${image}.png`)).default;
    } catch (error) {}
  },
  { immediate: true }
);
</script>

<style lang="scss" scoped>
.image {
  display: block;
  max-width: 100%;
  max-height: 60px;
}
</style>
