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
  display: inline-flex;
  align-items: center;
  max-width: 100%;
  gap: 30px;
  color: $black;
  text-decoration: none;
}

a.member:hover {
  color: $theme;
}

.image {
  flex-shrink: 0;
  width: 80px;
  height: 80px;

  .portrait {
    width: 100%;
    height: 100%;
    overflow: hidden;
    border-radius: 999px;
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
  font-weight: 500;
  font-size: 1.1rem;
}

.name,
.role {
  margin: 10px 0;
}
</style>
