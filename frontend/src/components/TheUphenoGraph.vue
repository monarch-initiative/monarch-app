<template>
  <div id="graph"></div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, watchEffect } from "vue";
import * as d3 from "d3";
import humanIcon from "../assets/icons/humanIcon.svg?url";
import mouseIcon from "../assets/icons/mouseIcon.svg?url";
import zebrafishIcon from "../assets/icons/zebrafishIcon.svg?url";

const props = defineProps({
  data: {
    type: Object,
    default: () => ({}),
  },
  currentId: {
    type: String,
    default: "",
  },
});

const ICON_MAP = {
  human: humanIcon,
  mouse: mouseIcon,
  zebrafish: zebrafishIcon,
};

// Define Node
interface Node {
  id: string;
  label: string;
  ontology: string;
  taxon?: string;
  x?: number;
  y?: number;
  width?: number;
  height?: number;
}

// Define Link
interface Link {
  source: Node;
  target: Node;
}

const drawGraph = () => {
  const container = document.getElementById("graph");
  if (!container) return;

  // Get dynamic width & height
  const width = container.clientWidth || 600;
  const height = container.clientHeight || 400;
  const parentY = 50;

  // Adjust childrenY dynamically to avoid excessive distance
  const maxChildrenY = 350;
  const childrenY = Math.min(
    Math.max(parentY + 150, height * 0.4),
    maxChildrenY,
  );

  const parentX = width / 2;
  const numChildren = props.data?.species_specific_children?.length || 0;
  const maxChildSpacing = 150;
  const minChildSpacing = 80;
  const childSpacing = Math.max(
    minChildSpacing,
    Math.min(maxChildSpacing, width / Math.max(numChildren, 1)),
  );
  const startX = parentX - ((numChildren - 1) * childSpacing) / 2;
  const graphWidth = width;
  const graphHeight = Math.max(childrenY + 150, parentY + 100);

  // Clear previous SVG before drawing
  const svg = d3
    .select("#graph")
    .html("")
    .append("svg")
    .attr("width", "100%")
    .attr("height", graphHeight)
    .attr("viewBox", `0 0 ${graphWidth} ${graphHeight}`)
    .attr("preserveAspectRatio", "xMidYMid meet")
    .attr("class", "custom-svg");

  const g = svg
    .append("g")
    .attr("class", "graph-group")
    .attr("transform", "translate(10, 50)"); // Ensure no offset

  // Create nodes (parent and children)
  const nodes: Node[] = [
    {
      ...(props.data?.upheno_parent ?? {}),
      x: parentX,
      y: parentY,
      width: 239,
      height: 99,
    },
    ...(props.data?.species_specific_children ?? []).map(
      (child: Node, i: number) => ({
        ...child,
        x: startX + i * childSpacing,
        y: childrenY,
        width: 107,
        height: 136,
      }),
    ),
  ];

  // Create links from parent to children
  const links: Link[] = (props.data?.species_specific_children ?? []).map(
    (child: Node) => ({
      source: nodes[0],
      target: nodes.find((n) => n.id === child.id)!,
    }),
  );

  g.selectAll(".link")
    .data(links)
    .enter()
    .append("line")
    .attr("class", "link")
    .attr("stroke", "#999")
    .attr("stroke-width", 2)
    .attr("x1", (d) => d.source.x!)
    .attr("y1", (d) => d.source.y! + d.source.height! / 2)
    .attr("x2", (d) => d.target.x!)
    .attr("y2", (d) => d.target.y! - d.target.height! / 2);

  // Create rectangles (nodes)
  g.selectAll(".node")
    .data(nodes)
    .enter()
    .append("rect")
    .attr("class", "node")
    .attr("width", (d) => d.width!)
    .attr("height", (d) => d.height!)
    .attr("rx", 10)
    .attr("ry", 10)
    .attr("fill", (d) =>
      d.id === props.currentId
        ? "none"
        : d.ontology === "uPheno"
          ? "#1f77b4"
          : "#ff7f0e",
    )
    .attr("stroke", (d) => (d.id === props.currentId ? "#f0a737" : "none"))
    .attr("stroke-width", (d) => (d.id === props.currentId ? 4 : 0))
    .attr("filter", "url(#shadow)")
    .attr("x", (d) => d.x! - d.width! / 2)
    .attr("y", (d) => d.y! - d.height! / 2);

  // Add SVG images inside nodes based on the taxon property
  g.selectAll(".node-image")
    .data(nodes)
    .enter()
    .append("image")
    .attr("class", "node-image")
    .attr("x", (d) => d.x! - 15)
    .attr("y", (d) => d.y! - 30 - 20)
    .attr("width", 25)
    .attr("height", 25)
    .attr("preserveAspectRatio", "xMidYMid slice")
    .attr("xlink:href", (d) => {
      if (d.taxon === "human") return ICON_MAP.human;
      if (d.taxon === "mouse") return ICON_MAP.mouse;
      if (d.taxon === "zebrafish") return ICON_MAP.zebrafish;
      return null;
    });

  // Function to wrap text inside nodes
  const wrapText = (text: string, maxWidth: number, fontSize: number) => {
    const words = text.split(" ");
    let line = "",
      lines: string[] = [];
    words.forEach((word) => {
      const testLine = line ? `${line} ${word}` : word;
      const testWidth = testLine.length * fontSize * 0.6;
      if (testWidth > maxWidth) {
        lines.push(line);
        line = word;
      } else {
        line = testLine;
      }
    });
    if (line) lines.push(line);
    return lines;
  };

  // Create text inside nodes (ID and label)
  g.selectAll(".node-text")
    .data(nodes)
    .enter()
    .append("text")
    .attr("class", "node-text")
    .attr("text-anchor", "middle")
    .attr("x", (d) => d.x!)
    .attr("y", (d) => d.y!)
    .each(function (d: Node) {
      const text = d3.select(this);
      const maxWidth = d.width! - 10,
        fontSize = 12,
        lineHeight = fontSize * 1.2;

      text
        .append("tspan")
        .attr("x", d.x!)
        .attr("dy", "-0.2em")
        .text(d.id)
        .attr("class", "node-id")
        .style("fill", (d) =>
          (d as Node).id === props.currentId ? "#000000" : "#FFD700",
        );

      const wrappedLines = wrapText(d.label, maxWidth, fontSize);
      wrappedLines.forEach((line, i) => {
        text
          .append("tspan")
          .attr("x", d.x!)
          .attr("dy", i === 0 ? "1.5em" : `${lineHeight}px`)
          .text(line)
          .attr("class", "node-label")
          .style("fill", (d) =>
            (d as Node).id === props.currentId ? "#000000" : "#FFFFFF",
          );
      });
    });

  // Create shadow filter
  const filter = svg
    .append("defs")
    .append("filter")
    .attr("id", "shadow")
    .attr("x", "-50%")
    .attr("y", "-50%")
    .attr("width", "200%")
    .attr("height", "200%");

  filter
    .append("feDropShadow")
    .attr("dx", 3)
    .attr("dy", 3)
    .attr("stdDeviation", 5)
    .attr("flood-color", "rgba(0, 0, 0, 0.5)");
};

// Resize graph dynamically
const updateGraph = () => {
  drawGraph();
};

// Watch for changes in data and redraw graph
watchEffect(drawGraph);

// Mount & unmount resize listener
onMounted(() => {
  window.addEventListener("resize", updateGraph);
  drawGraph();
});

onUnmounted(() => {
  window.removeEventListener("resize", updateGraph);
});
</script>

<style>
/**
 * We may need to pass down/adjust the height and width of the graph 
 * if we plan to use it in multiple locations. 
 (it will depend on how much space we are planning to allocate for the graph)
 */
#graph {
  width: 100%;
  height: 100%;
  overflow: auto;
}

.node-text {
  font-family: Arial, sans-serif;
  text-anchor: middle;
}

.node-id {
  font-weight: bold;
  font-size: 14px;
  fill: #ffd700;
  padding: 2px;
}

.node-label {
  font-weight: normal;
  font-size: 12px;
  fill: #ffffff;
}

.custom-svg {
  display: flex;
}

.image {
  border-radius: 10px;
}
</style>
