<!--
  dev page for experimenting with design and behavior of components. also a
  place for seeing all variations at once to check for coherence.
-->

<template>
  <AppSection>
    <AppHeading>Testbed</AppHeading>
  </AppSection>

  <!-- phenogrid -->
  <AppSection>
    <AppHeading>Phenogrid - Search mode</AppHeading>
    <iframe
      name="pheno-search"
      title="Phenogrid"
      frameBorder="0"
      src="/phenogrid-search?subjects=HP:0000939,HP:0000444,HP:0000546,HP:0000135&object-group=Human+Diseases"
    ></iframe>

    <AppButton text="Send Message" @click="sendMessage" />
  </AppSection>

  <!-- phenogrid -->
  <AppSection>
    <AppHeading>Phenogrid - Multicompare mode</AppHeading>
    <iframe
      name="pheno-multi"
      title="MultiCompare Phenogrid"
      frameBorder="0"
      src="/phenogrid-multi-compare?subjects=HP:0002616,HP:0001763,HP:0004944,HP:0010749,HP:0001533,HP:0002020,HP:0012450&object-sets=HP:0002616,HP:0001763,HP:0000767,HP:0000023,HP:0002108,HP:0000490,HP:0000545,HP:0100785,HP:0000268&object-sets=HP:0002616,HP:0001763,HP:0004944,HP:0010749,HP:0001533,HP:0002020,HP:0012450,HP:0003394,HP:0003771,HP:0012378,HP:0001278,HP:0002827,HP:0002829,HP:0002999,HP:0003010&object-sets=HP:0002616,HP:0001763,HP:0000767,HP:0000023,HP:0002108,HP:0000490,HP:0000545,HP:0100785,HP:0000268,HP:0001634,HP:0001653,HP:0001659,HP:0002360,HP:0003179,HP:0004970,HP:0005059,HP:0002705,HP:0012432,HP:0007800,HP:0001704"
    ></iframe>
  </AppSection>

  <!-- custom icons -->
  <AppSection>
    <AppHeading>Custom Icons</AppHeading>
    <AppFlex class="icons">
      <AppIcon
        v-for="(icon, index) of icons"
        :key="index"
        v-tooltip="icon + '.svg'"
        :icon="icon"
      />
      <AppIcon icon="test-initials" />
    </AppFlex>
  </AppSection>

  <!-- percentage ring/bar component -->
  <AppSection>
    <AppHeading>Percentage</AppHeading>
    <AppFlex direction="row">
      <AppPercentage tooltip="Percent" :percent="0.25">{{ 123 }}</AppPercentage>
      <AppPercentage tooltip="Percent" :percent="0.5" />
      <AppPercentage tooltip="Percent" :percent="0.75" />
      <AppPercentage tooltip="Percent" :percent="1" />
    </AppFlex>
    <AppFlex direction="row">
      <AppPercentage tooltip="Percent" :percent="0.25" type="bar">{{
        123
      }}</AppPercentage>
      <AppPercentage tooltip="Percent" :percent="0.5" type="bar" />
      <AppPercentage tooltip="Percent" :percent="0.75" type="bar" />
      <AppPercentage tooltip="Percent" :percent="1" type="bar" />
    </AppFlex>
  </AppSection>

  <!-- textbox component -->
  <AppSection>
    <AppHeading>Textbox</AppHeading>
    <label>
      <AppInput v-model="input" placeholder="Raw input" />
    </label>
    <AppTextbox v-model="input" icon="search" placeholder="Single line input" />
    <AppTextbox
      v-model="input"
      :multi="true"
      icon="magnifying-glass"
      placeholder="Multi-line input"
    />
  </AppSection>

  <!-- single select component -->
  <AppSection>
    <AppHeading>Single Select</AppHeading>
    <span>{{ singleSelectValue }}</span>
    <AppSelectSingle
      v-model="singleSelectValue"
      name="Fruits"
      :options="singleSelectOptions"
    />
  </AppSection>

  <!-- multi select component -->
  <AppSection>
    <AppHeading>Multi Select</AppHeading>
    <span>{{ multiSelectValue }}</span>
    <AppSelectMulti
      v-model="multiSelectValue"
      name="Category"
      :options="multiSelectOptions"
    />
    <AppSelectMulti
      v-slot="props"
      v-model="multiSelectValue"
      name="Category"
      design="small"
      :options="multiSelectOptions"
    >
      <AppButton
        v-tooltip="'Test button'"
        icon="filter"
        v-bind="props"
        design="small"
      />
    </AppSelectMulti>
  </AppSection>

  <!-- tags select component -->
  <AppSection>
    <AppHeading>Tags Select</AppHeading>
    <span>{{ tagsSelectValue }}</span>
    <AppSelectTags
      v-model="tagsSelectValue"
      name="Desserts"
      placeholder="Search for a dessert"
      :options="tagsSelectOptions"
    />
  </AppSection>

  <!-- autocomplete select component -->
  <AppSection>
    <AppHeading>Autocomplete Select</AppHeading>
    <AppSelectAutocomplete
      name="Animals"
      :options="autocompleteSelectOptions"
    />
  </AppSection>

  <!-- button component -->
  <AppSection>
    <AppHeading>Button</AppHeading>
    <AppFlex v-for="(row, rowIndex) of buttons" :key="rowIndex">
      <AppButton
        v-for="(props, colIndex) of row"
        :key="colIndex"
        v-tooltip="'Test button'"
        to="/"
        v-bind="props"
        @click="log"
      />
    </AppFlex>
  </AppSection>

  <!-- tabs component -->
  <AppSection>
    <AppHeading>Tabs</AppHeading>
    <AppTabs v-model="tab" :tabs="tabs" name="Tab group" />
    {{ tab }}
  </AppSection>

  <!-- status component -->
  <AppSection>
    <AppHeading>Status</AppHeading>
    <AppGallery>
      <AppStatus code="loading">Loading some results</AppStatus>
      <AppStatus code="success">Action was a success</AppStatus>
      <AppStatus code="warning">Be careful</AppStatus>
      <AppStatus code="error">There was an error</AppStatus>
      <AppStatus code="paused">Action is paused</AppStatus>
      <AppStatus code="unknown">Unexpected result</AppStatus>
    </AppGallery>
  </AppSection>

  <!-- table component -->
  <AppSection>
    <AppHeading>Table</AppHeading>
    <span>{{ omit(table, ["cols", "rows"]) }}</span>
    <AppTable
      id="testbed"
      v-model:sort="table.sort"
      v-model:selectedFilters="table.selectedFilters"
      v-model:per-page="table.perPage"
      v-model:start="table.start"
      v-model:search="table.search"
      :cols="table.cols"
      :rows="table.rows"
      :filter-options="table.filterOptions"
    >
      <template #arbitrary>Arbitrary slot content</template>
    </AppTable>
  </AppSection>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { omit } from "lodash";
import { useEventListener } from "@vueuse/core";
import AppButton from "@/components/AppButton.vue";
import AppInput from "@/components/AppInput.vue";
import AppPercentage from "@/components/AppPercentage.vue";
import AppSelectAutocomplete from "@/components/AppSelectAutocomplete.vue";
import AppSelectMulti from "@/components/AppSelectMulti.vue";
import AppSelectSingle from "@/components/AppSelectSingle.vue";
import AppSelectTags from "@/components/AppSelectTags.vue";
import type { Sort } from "@/components/AppTable.vue";
import AppTable from "@/components/AppTable.vue";
import AppTabs from "@/components/AppTabs.vue";
import AppTextbox from "@/components/AppTextbox.vue";
import { sleep } from "@/util/debug";

/** get all files in custom icon folder */
const icons = Object.values(import.meta.glob("@/assets/icons/*.svg")).map(
  (icon) => (icon.name.split("/").pop() || "").replace(/\.svg$/, ""),
);

/** test phenogrid iframe embedding */
useEventListener(
  "message",
  (
    event: MessageEvent<{
      name: string;
      width: number;
      height: number;
    }>,
  ) => {
    const { width, height, name } = event.data;
    const iframe = document.querySelector<HTMLIFrameElement>(
      `iframe[name='${name}']`,
    );
    if (!iframe) return;
    iframe.style.maxWidth = width + "px";
    iframe.style.maxHeight = height + "px";
  },
);

/** send message to iframe with longer params */
function sendMessage() {
  const iframe = document.querySelector<HTMLIFrameElement>("iframe");
  if (!iframe) return;
  iframe.contentWindow?.postMessage(
    {
      subjects: [
        "MP:0010771",
        "MP:0002169",
        "MP:0005391",
        "MP:0005389",
        "MP:0005367",
      ],
      "object-group": "Human Genes",
    },
    "*",
  );
}

const input = ref("");

type ButtonProps = InstanceType<typeof AppButton>["$props"];

/** enumerate permutations of button options */
const buttons = ref<ButtonProps[][]>([]);
for (const design of ["normal", "circle", "small"] as const) {
  for (const color of ["primary", "secondary"] as const) {
    const row = [];
    for (const [text, icon] of [
      ["Text", ""],
      ["Text", "download"],
      ["", "download"],
    ]) {
      row.push({ design, color, text, icon } satisfies ButtonProps);
    }
    buttons.value.push(row);
  }
}

/** single select */
const singleSelectOptions = ref([
  { id: "apple", icon: "lightbulb" },
  { id: "banana", icon: "lightbulb" },
  { id: "cherry", icon: "lightbulb", count: 54 },
  { id: "durian", icon: "lightbulb", count: 54 },
  { id: "elderberry", count: 54 },
  { id: "fig", count: 54 },
  { id: "grape" },
  { id: "honeydew" },
]);
const singleSelectValue = ref({ id: "durian" });

/** multi select */
const multiSelectOptions = ref([
  { id: "fruits", count: 0 },
  { id: "vegetables", count: 7 },
  { id: "colors", count: 42 },
  { id: "animals", count: 999 },
  { id: "cars" },
  { id: "schools" },
  { id: "appliances" },
]);
const multiSelectValue = ref([{ id: "vegetables" }]);

/** tags select */
const tagsSelectOptions = ref(async (search = "") => {
  await sleep(500); /** test loading spinner */
  return {
    options: [
      { id: "ice cream", icon: "flask" },
      { id: "candy", icon: "database", info: "8 phenotypes" },
      { id: "gummies", info: "4 phenotypes" },
      { id: "brownies", icon: "paper-plane", info: "1 phenotype" },
      { id: "cookies" },
    ].filter(({ id }) => id.includes(search)),
    message: "Selected item!",
  };
});
const tagsSelectValue = ref([
  { id: "candy", icon: "database", count: "8 phenotypes" },
]);

/** autocomplete select */
const autocompleteSelectOptions = ref(async () => {
  await sleep(500); /** test loading spinner */
  return [
    { icon: "flask", label: "Cat" },
    { label: "Dog", info: "good dog" },
    { icon: "download", label: "Zebra" },
  ];
});

/** tabs */
const tabs = [
  { id: "apple", text: "Apple", icon: "asterisk" },
  { id: "banana", text: "Banana", icon: "cogs" },
  { id: "cherry", text: "Cherry", icon: "flask" },
  { id: "durian", text: "Durian", icon: "paper-plane" },
  { id: "elderberry", text: "Elderberry", icon: "sitemap" },
];

/** selected tab */
const tab = ref(tabs[0].id);

/** table input props */
const table = ref({
  cols: [
    {
      slot: "name",
      key: "name" as const,
      heading: "Name",
      align: "left" as const,
      sortable: true,
    },
    {
      slot: "score",
      key: "score" as const,
      heading: "Score",
      sortable: true,
    },
    {
      slot: "details",
      key: "details" as const,
      heading: "Details",
      align: "left" as const,
      sortable: true,
    },
    {
      slot: "arbitrary",
      key: "arbitrary" as const,
      heading: "Arbitrary",
      align: "right" as const,
    },
  ],
  rows: [
    { name: "abc", score: 9, details: [1, 2], arbitrary: 123 },
    { name: "def", score: -1, details: [2, 1, 3] },
    { name: "def", score: 2, details: [1] },
    { name: "abc", score: 4, details: [2, 1] },
    { name: "ghi", score: NaN, details: [1] },
  ],
  sort: { key: "score", direction: "up" } as Sort,
  perPage: 10,
  start: 0,
  end: 11,
  total: 123,
  search: "",
  filterOptions: { score: [{ id: "numbers" }, { id: "nulls" }] },
  selectedFilters: { score: [{ id: "numbers" }] },
});

/** util */
const log = console.debug;
</script>

<style lang="scss" scoped>
iframe {
  width: 100%;
  height: 2000px;
}

.icons {
  color: $theme;
  font-size: 4rem;
}
</style>
