<!--
  team member profile/portrait
-->

<template>
  <AppLink :to="link || ''" class="member">
    <div class="image">
      <img class="portrait" :src="src" :alt="name" loading="lazy" />
    </div>
    <div class="text">
      <div class="name">{{ name }}</div>
      <div v-if="role" class="role">{{ role }}</div>
    </div>
  </AppLink>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { deburr, kebabCase } from "lodash";

type Props = {
  /** member name */
  name: string;
  /** their role */
  role?: string;
  /** link to bio */
  link?: string;
};

const props = defineProps<Props>();

/** get member img src with fallback if not found */
const src = ref("");
watch(
  () => props.name,
  async () => {
    const image = kebabCase(deburr((props.name || "").toLowerCase()));
    try {
      src.value = (await import(`../assets/team/members/${image}.jpg`)).default;
    } catch (error) {
      src.value = (await import(`../assets/team/_member.jpg`)).default;
    }
  },
  { immediate: true },
);
</script>

<style lang="scss" scoped>
.member {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 10px;
  text-decoration: none;
  overflow-wrap: break-word;
}

.image {
  aspect-ratio: 1 / 1;
  width: 100%;
  overflow: hidden;

  .portrait {
    width: 100%;
    height: 100%;
  }

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition:
      transform $fast,
      filter $fast;
  }
}

.member:hover img {
  transform: scale(1.1);
  filter: saturate(0) sepia(50%) hue-rotate(120deg);
}

.text {
  display: flex;
  flex-direction: column;
}

.name {
  font-weight: 500;
  font-size: 1.1rem;
}
</style>
