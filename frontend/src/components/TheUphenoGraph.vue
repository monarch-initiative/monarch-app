<template>
  <div id="graph"></div>
</template>

<script setup>
import { onMounted } from "vue";
import * as d3 from "d3";

// Sample data
const data = {
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
  ],
};

onMounted(() => {
  const width = 500,
    height = 300;

  const svg = d3
    .select("#graph")
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", "translate(50,50)");

  const links = [
    { source: data.upheno_parent, target: data.species_specific_children[0] },
    { source: data.upheno_parent, target: data.species_specific_children[1] },
  ];

  const nodes = [data.upheno_parent, ...data.species_specific_children];

  const simulation = d3
    .forceSimulation(nodes)
    .force(
      "link",
      d3
        .forceLink(links)
        .id((d) => d.id)
        .distance(100),
    )
    .force("x", d3.forceX(width / 2)) // Center nodes horizontally
    .force(
      "y",
      d3.forceY((d) => (d.ontology === "uPheno" ? 50 : 200)),
    ) // Parent at top, children below
    .force("collide", d3.forceCollide(50)); // Avoid overlap

  const link = svg
    .selectAll(".link")
    .data(links)
    .enter()
    .append("line")
    .attr("stroke", "#999")
    .attr("stroke-width", 2);

  const node = svg
    .selectAll(".node")
    .data(nodes)
    .enter()
    .append("rect")
    .attr("width", 120) // Set width of the box
    .attr("height", 50) // Set height of the box
    .attr("rx", 10) // Rounded corners
    .attr("ry", 10) // Rounded corners
    .attr("fill", (d) => (d.ontology === "uPheno" ? "#1f77b4" : "#ff7f0e"));

  const label = svg
    .selectAll(".label")
    .data(nodes)
    .enter()
    .append("text")
    .text((d) => `${d.label} (${d.id})`)
    .attr("text-anchor", "middle")
    .attr("dy", -15) // Adjust the vertical position of the label
    .style("fill", "#333")
    .style("font-size", "12px");

  node
    .on("mouseover", function (event, d) {
      if (d.ontology !== "uPheno") {
        d3.select(this).attr("stroke", "black").attr("stroke-width", 2); // Highlight on hover
      }
    })
    .on("mouseout", function (event, d) {
      if (d.ontology !== "uPheno") {
        d3.select(this).attr("stroke", "none"); // Reset highlight on hover out
      }
    });

  simulation.on("tick", () => {
    link
      .attr("x1", (d) => d.source.x)
      .attr("y1", (d) => d.source.y)
      .attr("x2", (d) => d.target.x)
      .attr("y2", (d) => d.target.y);

    node
      .attr("x", (d) => d.x - 60) // Adjust the position of the box
      .attr("y", (d) => d.y - 25); // Adjust the vertical position of the box
    label
      .attr("x", (d) => d.x) // Position the label inside the box
      .attr("y", (d) => d.y); // Position the label inside the box
  });
});
</script>
