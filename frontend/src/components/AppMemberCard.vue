<template>
  <AppLink :to="link || ''" class="sab-member-row">
    <div v-if="!noImage" class="image">
      <img class="portrait" :src="src" alt="" loading="lazy" />
    </div>
    <div class="sab-info">
      <p class="sab-name">{{ name }}</p>
      <p v-if="role" class="sab-description">{{ role }}</p>
    </div>
  </AppLink>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { deburr, kebabCase } from "lodash";
import AppLink from "@/components/AppLink.vue";

type Props = {
  name: string;
  role?: string;
  link?: string;
  noImage?: true;
};

const props = defineProps<Props>();

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

<style scoped>
.sab-member-row {
  display: flex;
  align-items: center;
  max-width: 800px;
  margin: 0 auto 2rem;
  gap: 1.5rem;
  color: inherit;
  text-decoration: none;
}

.image {
  flex-shrink: 0;
  width: 140px;
  height: 170px;

  overflow: hidden;
  border: 3px solid #2b7bb9;
  border-radius: 50% / 45%;
}

.portrait {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.sab-member-row:hover .portrait {
  transform: scale(1.1);
  filter: saturate(0) sepia(50%) hue-rotate(120deg);
}

.sab-info {
  flex: 1;
}

.sab-name {
  margin-bottom: 0.25rem;
  font-weight: 500;
  font-size: 1.1rem;
}

.sab-designation {
  display: inline-block;
  margin-bottom: 0.5rem;
  color: #2b7bb9;
  text-decoration: none;
}

.sab-description {
  color: #333;
  font-weight: 500;
  font-size: 0.95rem;
  line-height: 1.4;
  text-align: left;
}

@media (max-width: 600px) {
  .sab-member-row {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .sab-info {
    max-width: 90%;
  }
}
</style>
