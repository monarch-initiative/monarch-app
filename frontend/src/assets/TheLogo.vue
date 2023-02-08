<!--
  the monarch logo. do this as a vue component for css scoping.
-->

<template>
  <svg viewBox="-50 -30 100 60">
    <mask id="logo-mask">
      <rect x="-50" y="-50" width="100" height="100" fill="white" />
      <rect x="-10" y="7.5" width="20" height="5" fill="black" />
      <rect x="7.5" y="-10" width="5" height="20" fill="black" />
    </mask>

    <g transform="scale(0.8) rotate(-45)">
      <path
        class="logo-path"
        fill="none"
        stroke="currentColor"
        stroke-width="5"
        stroke-linecap="round"
        mask="url(#logo-mask)"
        d="M 5 10 L 5 -20 A 25 25 0 1 0 -20 5 L -15 5"
      />
      <path
        class="logo-path"
        fill="none"
        stroke="currentColor"
        stroke-width="5"
        stroke-linecap="round"
        mask="url(#logo-mask)"
        d="M -5 10 L -5 -20 A 15 15 0 1 0 -20 -5 L -15 -5"
      />
      <path
        class="logo-path"
        fill="none"
        stroke="currentColor"
        stroke-width="5"
        stroke-linecap="round"
        mask="url(#logo-mask)"
        d="M -5 15 L -5 20 A 25 25 0 1 0 20 -5 L 10 -5"
      />
      <path
        class="logo-path"
        fill="none"
        stroke="currentColor"
        stroke-width="5"
        stroke-linecap="round"
        mask="url(#logo-mask)"
        d="M 5 15 L 5 20 A 15 15 0 1 0 20 5 L 10 5"
      />
    </g>
  </svg>
</template>

<style lang="scss" scoped>
svg {
  outline: none;
}

path:nth-child(1) {
  --length: 152.826;
  animation-delay: 0.8s;
}

path:nth-child(2) {
  --length: 105.696;
  animation-delay: 0.5s;
}

path:nth-child(3) {
  --length: 132.826;
  animation-delay: 0.8s;
}

path:nth-child(4) {
  --length: 85.696;
  animation-delay: 0.5s;
}

path {
  stroke-dasharray: var(--length);
  stroke-dashoffset: var(--length);
  animation: stroke 1s ease forwards;
}

@keyframes stroke {
  from {
    stroke-dashoffset: var(--length);
  }
  to {
    stroke-dashoffset: 0;
  }
}
</style>
