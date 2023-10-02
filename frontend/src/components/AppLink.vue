<!--
  unified wrapper for internal (router) or external (other-domain) links.
  can be wrapped around any component or plain text.
-->

<template>
  <span v-if="!to">
    <!-- placeholder if no url provided -->
    <slot />
  </span>

  <a v-else-if="absoluteLink" :href="stringTo" target="_blank">
    <!-- use regular html link for absolute urls -->
    <template v-if="externalLink && plainText && !noIcon">
      <span>
        <slot />
      </span>
      <AppIcon class="icon" icon="arrow-up-right-from-square" />
    </template>
    <slot v-else />
  </a>

  <router-link
    v-else
    :to="{
      ...routeTo,
      state: mapValues(state, (value) => stringify(value)),
    }"
    :replace="!!routeTo.hash && !routeTo.path"
  >
    <!-- use vue router component for relative urls -->
    <slot />
  </router-link>
</template>

<script setup lang="ts">
import { computed, useSlots } from "vue";
import { useRouter, type RouteLocationRaw } from "vue-router";
import { mapValues } from "lodash";
import { stringify } from "@/util/object";
import { isAbsolute, isExternal } from "@/util/url";

/** route info */
const router = useRouter();

type Props = {
  /** location to link to */
  to: string | RouteLocationRaw;
  /**
   * state data to attach on navigation. object/array values get stringified.
   * https://developer.mozilla.org/en-US/docs/Web/API/History/pushState
   */
  state?: { [key: string]: unknown };
  /** whether to forcibly forgo external icon when link is external */
  noIcon?: boolean;
};

const props = withDefaults(defineProps<Props>(), {
  noIcon: false,
  state: undefined,
});

const slots = useSlots();

type Slots = {
  default: () => unknown;
};

defineSlots<Slots>();

/** interpret location as href string */
const stringTo = computed(() => {
  if (typeof props.to === "string") return props.to;
  else return router.resolve(props.to).href;
});

/** interpret location as route object */
const routeTo = computed(() => router.resolve(props.to));

/** is "to" prop an external url */
const externalLink = computed(() => isExternal(stringTo.value));

/** is "to" prop an absolute url */
const absoluteLink = computed(() => isAbsolute(stringTo.value));

/** is provided slot just plain text */
const plainText = computed(
  () =>
    slots.default &&
    slots.default().length === 1 &&
    typeof slots.default()[0].children === "string",
);
</script>

<style lang="scss" scoped>
.icon {
  margin-left: 5px;
}
</style>
