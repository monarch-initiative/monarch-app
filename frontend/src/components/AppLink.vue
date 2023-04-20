<!--
  unified wrapper for internal (router) or external (other-domain) links.
  can be wrapped around any component or plain text.
-->

<template>
  <span v-if="!to">
    <!-- placeholder if no url provided -->
    <slot />
  </span>

  <a v-else-if="absoluteLink" :href="to" target="_blank">
    <!-- use regular html link for absolute urls -->
    <template v-if="externalLink && plainText && !noIcon">
      <span>
        <slot />
      </span>
      <AppIcon class="icon" icon="external-link-alt" />
    </template>
    <slot v-else />
  </a>

  <router-link
    v-else
    :to="{
      ...splitTo,
      state: mapValues(state, (value) => stringify(value)),
    }"
    :replace="!!splitTo.hash && !splitTo.path"
  >
    <!-- use vue router component for relative urls -->
    <slot />
  </router-link>
</template>

<script setup lang="ts">
import { computed, useSlots } from "vue";
import { mapValues } from "lodash";
import { stringify } from "@/util/object";
import { isAbsolute, isExternal } from "@/util/url";

type Props = {
  /** location to link to */
  to: string;
  /**
   * state data to attach on navigation. object/array values get stringified.
   * https://developer.mozilla.org/en-US/docs/Web/API/History/pushState
   */
  state?: { [key: string]:  unknown };
  /** whether to forcibly forgo external icon when link is external */
  noIcon?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  noIcon: false,
  state: undefined,
});

const slots = useSlots();

/** is "to" prop an external url */
const externalLink = computed(() => isExternal(props.to));

/** is "to" prop an absolute url */
const absoluteLink = computed(() => isAbsolute(props.to));

/** is provided slot just plain text */
const plainText = computed(
  () =>
    slots.default &&
    slots.default().length === 1 &&
    typeof slots.default()[0].children === "string"
);

/**
 * convert "to" prop to separate route props because vue-router can't do this
 * itself
 */
const splitTo = computed(() => {
  const [, path, hash] = props.to.match(/([^#]*)(#[^#]*)?/) || [];
  return { path, hash };
});
</script>

<style lang="scss" scoped>
.icon {
  margin-left: 5px;
}
</style>
