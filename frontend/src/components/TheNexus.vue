<!--
  fun background visualization element behind header
-->

<template>
  <canvas id="nexus"></canvas>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { debounce } from "lodash";
import {
  useEventListener,
  useIntervalFn,
  useResizeObserver,
} from "@vueuse/core";
import type { Point2d, Point3d } from "@/util/math";
import { cos, dist, getMidpoint, project, sin } from "@/util/math";

/** Settings shared across functions */

/** Size of dots and links */
const size = 4;
/** Distance between dots */
const gap = 50;

/** Color of elements at rest (10% white, 90% theme-dark) */
const baseColor: Color = [25, 143, 154];
/** Color of element when pulsing (50% white, 50% theme-dark) */
const pulseColor: Color = [127, 193, 199];

/** 3d axis rotations */
let rx = 0;
let ry = 0;
let rxTarget = 0;
let ryTarget = 0;

/** Efficient rgb tuple format */
type Color = [number, number, number];

interface Dot {
  /** Position in 3d space */
  point: Point3d;
  /** 3d position projected into 2d for canvas rendering */
  projected?: Point2d;
  /** Target and actual color */
  color: Color;
  colorTarget: Color;
}

interface Link {
  /** Dots to link together */
  from: Dot;
  to: Dot;
  /** Target and actual color (in efficient rgb tuple format) */
  color: Color;
  colorTarget: Color;
}

/** Globals */
let canvas = null as HTMLCanvasElement | null;
let ctx = null as CanvasRenderingContext2D | null;
let width = 0;
let height = 0;
let dots: Array<Dot> = [];
let links: Array<Link> = [];

/** Resize canvas */
function resize() {
  if (!canvas || !ctx) return;
  const scale = window.devicePixelRatio;
  width = canvas.clientWidth;
  height = canvas.clientHeight;
  canvas.width = width * scale;
  canvas.height = height * scale;
  ctx.scale(scale, scale);
}

/** Generate field of dots and links */
const generate = debounce(() => {
  /** Generate field of dots */
  dots = [];
  /** Start from grid so dots relatively uniformly distributed */
  for (let x = 0; x <= width; x += gap) {
    for (let y = 0; y <= height; y += gap) {
      if (
        /** Eliminate some to make more "organic" and less "grid" */
        Math.random() > 0.4 &&
        /** Avoid direct center to make visual space for log */
        (Math.abs(x - width / 2) > gap * 2 || Math.abs(y - height / 2) > gap)
      ) {
        const angle = Math.random() * 360;
        dots.push({
          point: {
            /** Nudge off grid to make more "organic" */
            x: x + sin(angle) * (gap / 4),
            y: y + cos(angle) * (gap / 4),
            /** Random range to create nice thin-ish 3d layer */
            z: -gap + Math.random() * 2 * gap,
          },
          color: [...baseColor],
          colorTarget: [...baseColor],
        });
      }
    }
  }

  /** Hard limit dots for performance */
  while (dots.length > 200)
    dots.splice(Math.floor(dots.length * Math.random()), 1);

  /** Sort dots by z */
  dots.sort((a, b) => a.point.z - b.point.z);

  /** Go through each pair of dots */
  links = [];
  for (let a = 0; a < dots.length; a++) {
    for (let b = 0; b < dots.length; b++) {
      /** Upper triangular matrix to only count each pair once */
      if (a > b) {
        const from = dots[a];
        const to = dots[b];
        /** Only link if dots close enough together */
        if (
          dist(from.point.x, from.point.y, to.point.x, to.point.y) <
          gap * 1.5
        )
          links.push({
            from,
            to,
            color: [...baseColor],
            colorTarget: [...baseColor],
          });
      }
    }
  }

  /** Eliminate dots with no links */
  dots = dots.filter((dot) =>
    links.find(({ from, to }) => dot === from || dot === to)
  );
}, 50);

/** Rotate 3d world */
function rotate(event: MouseEvent | TouchEvent) {
  /** Point touched */
  const x = "clientX" in event ? event.clientX : event.touches[0].clientX;
  const y = "clientY" in event ? event.clientY : event.touches[0].clientY;
  /** Set destination 3d world rotation */
  rxTarget = (0.5 - y / window.innerHeight) * 90;
  ryTarget = -(0.5 - x / window.innerWidth) * 90;
}

/** Move physics simulation one step */
function move() {
  /** Move 3d world rotation toward target rotation smoothly */
  rx += (rxTarget - rx) / 100;
  ry += (ryTarget - ry) / 100;

  /** For each dot */
  for (const dot of dots) {
    /** Project from 3d into 2d using 3d rotation matrix */
    dot.projected = project(dot.point, rx, ry, width / 2, height / 2);
  }

  /** For each entity (dot or link) */
  for (const entity of [...dots, ...links])
    for (let c = 0; c < 3; c++)
      /** Move color toward target smoothly */
      entity.color[c] += (entity.colorTarget[c] - entity.color[c]) / 15;
}

/** Clear canvas for redrawing */
function clear() {
  if (!canvas || !ctx) return;
  ctx.clearRect(0, 0, width || 0, height || 0);
}

/** Draw dots and links to canvas */
function draw() {
  if (!ctx) return;

  /** Draw links */
  for (const { from, to, color } of links) {
    if (!from.projected || !to.projected) continue;
    ctx.strokeStyle = "rgb(" + color.join(",") + ")";
    ctx.lineWidth = size / 3;
    ctx.beginPath();
    ctx.moveTo(from.projected.x, from.projected.y);
    ctx.lineTo(to.projected.x, to.projected.y);
    ctx.stroke();
  }

  /** Draw dots */
  for (const { projected, color } of dots) {
    if (!projected) continue;
    ctx.fillStyle = "rgb(" + color.join(",") + ")";
    ctx.beginPath();
    ctx.arc(projected.x, projected.y, size, 0, 2 * Math.PI);
    ctx.fill();
  }
}

/** Pulse color of field of dots and links from inward to outward */
function pulse() {
  for (const entity of [...dots, ...links]) {
    /** Get center position of entity */
    const center =
      "point" in entity
        ? entity.point
        : getMidpoint(entity.from.point, entity.to.point);

    /** Time delays */
    const speed = 5 / 10; /** How fast pulse propagates outward */
    const start = dist(center.x - width / 2, center.y - height / 2) / speed;
    const reset = start + 100 / speed;
    /** Set timers */
    window.setTimeout(() => (entity.colorTarget = [...pulseColor]), start);
    window.setTimeout(() => (entity.colorTarget = [...baseColor]), reset);
  }
}

/** One step/tick/frame */
function step() {
  move();
  clear();
  draw();
}

onMounted(() => {
  /** Setup canvas */
  canvas = document.querySelector("#nexus");
  ctx = canvas?.getContext("2d") || null;

  /** Listen for resizes to canvas element */
  useResizeObserver(canvas, () => {
    /** Resize canvas */
    resize();
    /** Regenerate field */
    generate();
  });
});

/** Event listeners */
useEventListener(window, "mousemove", rotate);
useEventListener(window, "touchmove", rotate);
useEventListener(window, "mousedown", pulse);

/** Intervals */
useIntervalFn(step, 1000 / 60);
useIntervalFn(pulse, 10000);
</script>

<style lang="scss" scoped>
#nexus {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: -1;
  animation: fade-in forwards 1s linear;
}

@keyframes fade-in {
  0% {
    opacity: 0;
  }

  100% {
    opacity: 1;
  }
}
</style>
