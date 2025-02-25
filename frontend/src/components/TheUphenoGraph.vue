<template>
  <div id="graph"></div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import * as d3 from "d3";

// Define Node and Link Types
interface Node {
  id: string;
  label: string;
  ontology: string;
  taxon?: string;
  x?: number;
  y?: number;
}

interface Link {
  source: Node;
  target: Node;
}

// Define the data
const data = ref<{
  upheno_parent: Node;
  species_specific_children: Node[];
}>({
  upheno_parent: {
    id: "UPHENO:123",
    label: "big heart",
    ontology: "uPheno",
  },
  species_specific_children: [
    {
      id: "HP:123",
      label: "cardiomegaly",
      ontology: "HP",
      taxon: "human",
    },
    {
      id: "ZP:436",
      label: "heart enlarged, abnormal",
      ontology: "ZP",
      taxon: "zebrafish",
    },
    {
      id: "MP:436",
      label: "heart enlarged, very abnormal",
      ontology: "MP",
      taxon: "mouse",
    },
    {
      id: "NP:436",
      label: "The new label",
      ontology: "NP",
      taxon: "Rat",
    },
  ],
});

const drawGraph = () => {
  const width = 600,
    height = 400;
  const parentY = 50,
    childrenY = 250; // Fixed Y positions
  const parentX = width / 2;

  // Clear previous SVG before drawing
  const svg = d3
    .select("#graph")
    .html("")
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g");

  // Calculate X positions for children (evenly spaced)
  const numChildren = data.value.species_specific_children.length;
  const childSpacing = 150;
  const startX = parentX - ((numChildren - 1) * childSpacing) / 2;

  // Set explicit positions
  const nodes: Node[] = [
    { ...data.value.upheno_parent, x: parentX, y: parentY },
    ...data.value.species_specific_children.map((child, i) => ({
      ...child,
      x: startX + i * childSpacing, // Evenly distribute children horizontally
      y: childrenY,
    })),
  ];

  // Define links from parent to each child
  const links: Link[] = data.value.species_specific_children.map((child) => ({
    source: nodes[0], // Parent node
    target: nodes.find((n) => n.id === child.id)!,
  }));

  // Create links
  svg
    .selectAll(".link")
    .data(links)
    .enter()
    .append("line")
    .attr("stroke", "#999")
    .attr("stroke-width", 2)
    .attr("x1", (d) => d.source.x!)
    .attr("y1", (d) => d.source.y!)
    .attr("x2", (d) => d.target.x!)
    .attr("y2", (d) => d.target.y!);

  // Create nodes (rectangles)
  const node = svg
    .selectAll(".node")
    .data(nodes)
    .enter()
    .append("rect")
    .attr("width", (d) => (d.ontology === "uPheno" ? 239 : 107))
    .attr("height", (d) => (d.ontology === "uPheno" ? 99 : 136))
    .attr("rx", 10)
    .attr("ry", 10)
    .attr("fill", (d) => (d.ontology === "uPheno" ? "#1f77b4" : "#ff7f0e"))
    .attr("x", (d) => d.x! - (d.ontology === "uPheno" ? 239 : 107) / 2)
    .attr("y", (d) => d.y! - (d.ontology === "uPheno" ? 99 : 136) / 2);

  // Create text labels
  svg
    .selectAll(".label")
    .data(nodes)
    .enter()
    .append("text")
    .text((d) => d.label)
    .attr("text-anchor", "middle")
    .attr("x", (d) => d.x!)
    .attr("y", (d) => d.y! + (d.ontology === "uPheno" ? 60 : 80))
    .style("fill", "#333")
    .style("font-size", "12px");
};

// Watch for changes in data and redraw graph
watch(data, () => {
  drawGraph();
});

onMounted(() => {
  drawGraph();
});
</script>
