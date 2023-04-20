<!--
  team member profile/portrait
-->

<template>
  <AppLink :to="link || ''" class="member">
    <div class="image">
      <div class="portrait">
        <img :src="src" :alt="name" loading="lazy" />
      </div>
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
  /** Member name */
  name: string;
  /** Their role */
  role?: string;
  /** Link to bio */
  link?: string;
};

const props = defineProps<Props>();

/** Get member img src with fallback if not found */
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
  { immediate: true }
);
</script>

<style lang="scss" scoped>
.member {
  display: inline-flex;
  align-items: center;
  gap: 30px;
  max-width: 100%;
  color: $black;
  text-decoration: none;
}

a.member:hover {
  color: $theme;
}

.image {
  width: 80px;
  height: 80px;
  flex-shrink: 0;

  .portrait {
    width: 100%;
    height: 100%;
    border-radius: 999px;
    overflow: hidden;
  }

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.text {
  text-align: left;
}

.name {
  font-size: 1.1rem;
  font-weight: 500;
}

.name,
.role {
  margin: 10px 0;
}
</style>
