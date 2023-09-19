<!--
  simple container for blocks of info (primarily for node page)
-->

<template>
  <AppFlex
    ref="cell"
    align-h="left"
    direction="col"
    gap="small"
    :class="['detail', { full: full && !blank }]"
  >
    <AppFlex gap="small" align-h="left">
      <AppIcon v-if="icon" :icon="icon" class="icon" />
      <span class="text">
        {{ title }}
      </span>
      <span v-if="count !== undefined" class="count">
        {{ count }}
      </span>
    </AppFlex>

    <div v-if="blank" class="empty">No info</div>
    <slot v-else />
  </AppFlex>
</template>

<script setup lang="ts">
/**
 * for fields not relevant to current page (e.g. taxon on a disease node page),
 * hide with v-if. for relevant fields, show with v-if, to indicate that field
 * exists, but pass "blank" prop to indicate that no data available
 */

type Props = {
  /** title of info block */
  title: string;
  /** icon next to title */
  icon?: string;
  /** number next to title */
  count?: number;
  /**
   * whether or not to show "no info" placeholder. why? to show that this field
   * exists, but doesn't have data this time.
   */
  blank?: boolean;
  /** whether info block is full width or not */
  full?: boolean;
};

withDefaults(defineProps<Props>(), {
  icon: "",
  count: undefined,
  blank: false,
  full: false,
});

type Slots = {
  default?: () => unknown;
};

defineSlots<Slots>();
</script>

<style lang="scss" scoped>
.detail {
  flex-grow: 1;
  line-height: $spacing;
  text-align: left;

  &.full {
    width: 100%;
  }

  &:not(.full) {
    width: calc((100% - 30px - 30px) / 3);
  }

  @media (max-width: 700px) {
    & {
      width: 100% !important;
    }
  }
}

.icon {
  color: $gray;
}

.text {
  font-weight: 600;
}

.count {
  color: $gray;
}

.empty {
  color: $gray;
}
</style>
