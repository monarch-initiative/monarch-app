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
  width?: number;
  height?: number;
}

interface Link {
  source: Node;
  target: Node;
}

const data = ref<{ upheno_parent: Node; species_specific_children: Node[] }>({
  upheno_parent: { id: "UPHENO:123", label: "big heart", ontology: "uPheno" },
  species_specific_children: [
    { id: "HP:123", label: "cardiomegaly", ontology: "HP", taxon: "human" },
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
    { id: "NP:436", label: "The new label", ontology: "NP", taxon: "Rat" },
  ],
});

const drawGraph = () => {
  const width = 600,
    height = 400;
  const parentY = 50,
    childrenY = 250;
  const parentX = width / 2,
    childSpacing = 150;

  // Clear previous SVG before drawing
  const svg = d3
    .select("#graph")
    .html("")
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g");

  // Set positions and dimensions for nodes
  const numChildren = data.value.species_specific_children.length;
  const startX = parentX - ((numChildren - 1) * childSpacing) / 2;
  const nodes: Node[] = [
    {
      ...data.value.upheno_parent,
      x: parentX,
      y: parentY,
      width: 239,
      height: 99,
    },
    ...data.value.species_specific_children.map((child, i) => ({
      ...child,
      x: startX + i * childSpacing,
      y: childrenY,
      width: 107,
      height: 136,
    })),
  ];

  // Create links from parent to children
  const links: Link[] = data.value.species_specific_children.map((child) => ({
    source: nodes[0],
    target: nodes.find((n) => n.id === child.id)!,
  }));
  svg
    .selectAll(".link")
    .data(links)
    .enter()
    .append("line")
    .attr("stroke", "#999")
    .attr("stroke-width", 2)
    .attr("x1", (d) => d.source.x!)
    .attr("y1", (d) => d.source.y! + d.source.height! / 2)
    .attr("x2", (d) => d.target.x!)
    .attr("y2", (d) => d.target.y! - d.target.height! / 2);

  // Create rectangles (nodes)
  svg
    .selectAll(".node")
    .data(nodes)
    .enter()
    .append("rect")
    .attr("width", (d) => d.width!)
    .attr("height", (d) => d.height!)
    .attr("rx", 10)
    .attr("ry", 10)
    .attr("fill", (d) => (d.ontology === "uPheno" ? "#1f77b4" : "#ff7f0e"))
    .attr("x", (d) => d.x! - d.width! / 2)
    .attr("y", (d) => d.y! - d.height! / 2);

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
  svg
    .selectAll(".node-text")
    .data(nodes)
    .enter()
    .append("text")
    .attr("text-anchor", "middle")
    .attr("x", (d) => d.x!)
    .attr("y", (d) => d.y!)
    .attr("class", "node-text")
    .each(function (d) {
      const text = d3.select(this);
      const maxWidth = d.width! - 10,
        fontSize = 12,
        lineHeight = fontSize * 1.2;
      text
        .append("tspan")
        .attr("x", d.x!)
        .attr("dy", "-0.5em")
        .text(d.id)
        .attr("class", "node-id");
      const wrappedLines = wrapText(d.label, maxWidth, fontSize);
      wrappedLines.forEach((line, i) => {
        text
          .append("tspan")
          .attr("x", d.x!)
          .attr("dy", i === 0 ? "1.5em" : `${lineHeight}px`)
          .text(line)
          .attr("class", "node-label");
      });
    });
};

// Watch for changes in data and redraw graph
watch(data, drawGraph);
onMounted(drawGraph);
</script>

<style>
.node-text {
  font-family: Arial, sans-serif;
  text-anchor: middle;
}

.node-id {
  font-weight: bold;
  font-size: 14px;
  fill: yellow;
}

.node-label {
  font-weight: normal;
  font-size: 12px;
  fill: white;
}
</style>
