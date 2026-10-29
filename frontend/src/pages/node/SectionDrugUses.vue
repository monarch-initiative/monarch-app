<!--
  drug ↔ condition sections (indications, contraindications, diagnostic uses),
  summarized with facets rather than listed edge by edge. progressive
  disclosure: section overview → one row per drug (or condition, on a drug
  page) → its distinct statements → the label assertions behind a statement.
-->

<template>
  <div class="drug-uses">
    <!-- direct vs. inferred (subtypes), as in the other association sections -->
    <AppAssociationTabs
      v-if="isDiseasePage && allCount > 0"
      :has-direct-associations="directCount > 0"
      :show-all-tab="allCount > directCount"
      :direct-active="activeTab === 'direct'"
      :all-active="activeTab === 'all'"
      :direct-label="`Directly associated ${sectionNoun}`"
      :inferred-label="`Inferred associated ${sectionNoun}`"
      :direct-tooltip="`${plural(directCount, groupNoun)} for ${node.name} itself`"
      :inferred-tooltip="`${plural(allCount, groupNoun)} for ${node.name} or its subtypes (${allCount - directCount} only through a subtype)`"
      @select="selectTab"
    />

    <!-- level 0: section overview -->
    <p v-if="summary.isSuccess.value" class="overview">
      <strong>{{ plural(summary.data.value.group_total, groupNoun) }}</strong>
      <span class="muted">
        ·
        {{ plural(summary.data.value.unique.grouping_key ?? 0, "statement") }}
        from {{ plural(summary.data.value.total, "label assertion") }}
      </span>
    </p>
    <AppStatus v-else-if="summary.isLoading.value" code="loading"
      >Loading summary</AppStatus
    >

    <div class="chips">
      <button
        v-for="j in jurisdictions.data.value.groups"
        :key="j.value"
        :class="['chip', { active: jurisdiction === j.value }]"
        :title="`Only show ${groupNoun}s with a ${jurisdictionName(j.value)} label`"
        @click="toggleJurisdiction(j.value)"
      >
        {{ jurisdictionName(j.value) }}
        <span class="chip-count">{{ j.unique[side] }}</span>
      </button>
      <template v-if="isIndications && investigationalCount > 0">
        <span class="chip-sep" />
        <button
          :class="['chip', { active: includeInvestigational }]"
          title="Clinical-trial, studied and off-label (applied) uses"
          @click="includeInvestigational = !includeInvestigational"
        >
          + investigational
          <span class="chip-count">{{ investigationalCount }}</span>
        </button>
      </template>
    </div>

    <!-- level 1: one row per drug / condition -->
    <ul class="groups">
      <li v-for="group in groups" :key="group.value" class="group">
        <!-- the whole row toggles; names inside it are links -->
        <div
          class="group-row"
          role="button"
          tabindex="0"
          :aria-expanded="expanded === group.value"
          :aria-label="`Show statements for ${group.fields[labelField]}`"
          @click="toggleGroup(group.value)"
          @keydown.enter.space.self.prevent="toggleGroup(group.value)"
        >
          <AppIcon
            class="expand"
            :icon="expanded === group.value ? 'angle-down' : 'angle-right'"
          />
          <span class="group-node" @click.stop>
            <AppNodeBadge
              :node="{
                id: group.value,
                name: group.fields[labelField] ?? group.value,
                category: group.fields[categoryField] ?? undefined,
              }"
            />
          </span>
          <span class="targets">
            <template
              v-for="(target, i) in group.facets[secondaryField] ?? []"
              :key="target.value"
            >
              <span v-if="i" class="muted">, </span>
              <span v-else-if="!isDiseasePage" class="muted">in </span>
              <span
                v-if="target.value === node.id"
                class="muted"
                :title="plural(target.count, 'label assertion')"
                >{{ target.label ?? target.value }}</span
              >
              <AppLink
                v-else
                :to="`/${target.value}`"
                :title="plural(target.count, 'label assertion')"
                @click.stop
                >{{ target.label ?? target.value }}</AppLink
              >
            </template>
          </span>
          <span class="where">
            <span
              v-for="j in group.facets.medic_jurisdiction ?? []"
              :key="j.value"
              class="pill"
              :title="`${plural(j.count, 'label assertion')} from ${jurisdictionName(j.value)}`"
              >{{ jurisdictionAbbrev(j.value) }}
              <span class="pill-count">{{ j.count }}</span></span
            >
          </span>
          <span class="since muted">{{
            year(group.stats.medic_approval_date?.min)
          }}</span>
        </div>

        <!-- level 2: distinct statements for this drug / condition -->
        <div v-if="expanded === group.value" class="statements">
          <AppStatus v-if="statements.isLoading.value" code="loading"
            >Loading statements</AppStatus
          >
          <ul v-else>
            <li
              v-for="st in statements.data.value.groups"
              :key="st.value"
              class="statement"
            >
              <div
                class="statement-row"
                role="button"
                tabindex="0"
                :aria-expanded="openStatement === st.value"
                @click="toggleStatement(st.value)"
                @keydown.enter.space.self.prevent="toggleStatement(st.value)"
              >
                <AppIcon
                  :icon="
                    openStatement === st.value ? 'angle-down' : 'angle-right'
                  "
                />
                <span class="predicate">{{
                  predicateLabel(st.fields.predicate)
                }}</span>
                <span v-if="st.fields.object === node.id" class="target">{{
                  st.fields.object_label
                }}</span>
                <span v-else class="target" @click.stop>
                  <AppNodeBadge
                    :node="{
                      id: st.fields.object ?? '',
                      name: st.fields.object_label ?? st.fields.object ?? '',
                      category: st.fields.object_category ?? undefined,
                    }"
                  />
                </span>
                <span
                  v-for="ctx in st.facets.disease_context_qualifier ?? []"
                  :key="ctx.value"
                  class="context"
                  >in
                  <span v-if="ctx.value === node.id">{{
                    ctx.label ?? ctx.value
                  }}</span>
                  <AppLink v-else :to="`/${ctx.value}`" @click.stop>{{
                    ctx.label ?? ctx.value
                  }}</AppLink></span
                >
                <span class="where">
                  <span
                    v-for="j in st.facets.medic_jurisdiction ?? []"
                    :key="j.value"
                    class="pill"
                    >{{ jurisdictionAbbrev(j.value) }}
                    <span class="pill-count">{{ j.count }}</span></span
                  >
                </span>
                <span class="since muted">{{
                  year(st.stats.medic_approval_date?.min)
                }}</span>
              </div>
              <ul
                v-if="(st.facets.population_context_qualifier ?? []).length"
                class="populations"
              >
                <li
                  v-for="pop in st.facets.population_context_qualifier"
                  :key="pop.value"
                >
                  {{ pop.value }}
                </li>
              </ul>

              <!-- level 3: the label assertions behind one statement -->
              <div v-if="openStatement === st.value" class="assertions">
                <AppStatus v-if="assertions.isLoading.value" code="loading"
                  >Loading labels</AppStatus
                >
                <template v-else>
                  <p class="muted assertion-summary">
                    {{ plural(assertions.data.value.total, "label") }} ·
                    {{ plural(distinctTextCount, "distinct indication text") }}
                  </p>
                  <div
                    v-for="block in assertionBlocks"
                    :key="block.jurisdiction"
                    class="jurisdiction-block"
                  >
                    <h4 class="jurisdiction-head">
                      {{ jurisdictionName(block.jurisdiction) }}
                      <span class="muted"
                        >{{ plural(block.labelCount, "label") }} ·
                        {{ block.sources.join(", ") }}</span
                      >
                    </h4>
                    <div
                      v-for="text in visibleTexts(block)"
                      :key="text.text"
                      class="assertion"
                    >
                      <p class="supporting">{{ text.text }}</p>
                      <div class="assertion-links">
                        <span class="muted">{{
                          plural(text.rows.length, "label")
                        }}</span>
                        <span v-if="text.firstApproved" class="muted"
                          >first approved {{ text.firstApproved }}</span
                        >
                        <a
                          v-for="(link, i) in text.links.slice(0, 8)"
                          :key="link"
                          :href="link"
                          target="_blank"
                          rel="noopener"
                          >label {{ i + 1 }}</a
                        >
                        <span v-if="text.links.length > 8" class="muted"
                          >+{{ text.links.length - 8 }} more</span
                        >
                        <button class="link" @click="openDetails(text.rows[0])">
                          details
                        </button>
                      </div>
                    </div>
                    <button
                      v-if="block.texts.length > TEXTS_SHOWN"
                      class="link"
                      @click="toggleBlock(block.jurisdiction)"
                    >
                      {{
                        openBlocks.has(block.jurisdiction)
                          ? "show fewer"
                          : `show ${block.texts.length - TEXTS_SHOWN} more indication texts`
                      }}
                    </button>
                  </div>
                  <p
                    v-if="
                      assertions.data.value.total >
                      assertions.data.value.items.length
                    "
                    class="muted"
                  >
                    Summarizing the first
                    {{ assertions.data.value.items.length }} of
                    {{ assertions.data.value.total }} labels.
                  </p>
                </template>
              </div>
            </li>
          </ul>
        </div>
      </li>
    </ul>

    <TheTableControls
      v-if="groupTotal > 0"
      v-model:per-page="perPage"
      v-model:start="start"
      class="pager"
      :rows="groups"
      :total="groupTotal"
      :show-download="false"
    />

    <AppModal v-model="showModal" label="Association Details">
      <SectionAssociationDetails
        :node="node"
        :association="selectedAssociation"
      />
    </AppModal>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import {
  getAssociationSummary,
  solrQuote,
  type AssociationSummary,
  type AssociationSummaryGroup,
} from "@/api/association-summary";
import { getAssociations } from "@/api/associations";
import type {
  AssociationTableResults,
  DirectionalAssociation,
  Node,
} from "@/api/model";
import AppAssociationTabs from "@/components/AppAssociationTabs.vue";
import AppIcon from "@/components/AppIcon.vue";
import AppLink from "@/components/AppLink.vue";
import AppModal from "@/components/AppModal.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppStatus from "@/components/AppStatus.vue";
import TheTableControls from "@/components/TheTableContols.vue";
import { useQuery } from "@/composables/use-query";
import SectionAssociationDetails from "@/pages/node/SectionAssociationDetails.vue";
import { parseRetrievalSources } from "@/util/retrievalSources";

type Props = {
  node: Node;
  /** association-type section key, e.g. drug_indications */
  sectionKey: string;
};

const props = defineProps<Props>();

const APPROVED = ["biolink:treats", "biolink:preventative_for_condition"];
const PAGE = 10;

const isDiseasePage = computed(() =>
  ["biolink:Disease", "biolink:PhenotypicFeature"].includes(
    props.node.category ?? "",
  ),
);
const isIndications = computed(() => props.sectionKey === "drug_indications");

/** on a disease page the rows are drugs (subjects); on a drug page, conditions */
const side = computed(() => (isDiseasePage.value ? "subject" : "object"));
const labelField = computed(() => `${side.value}_label`);
const categoryField = computed(() => `${side.value}_category`);
/**
 * the row's secondary column: the conditions a drug is used for (disease page),
 * or the disease contexts a condition is used in (drug page)
 */
const secondaryField = computed(() =>
  isDiseasePage.value ? "object" : "disease_context_qualifier",
);
const groupNoun = computed(() => (isDiseasePage.value ? "drug" : "condition"));

const jurisdiction = ref<string | null>(null);
const includeInvestigational = ref(false);
/** what the tabs call this section's rows, e.g. "Directly associated treatments" */
const sectionNoun = computed(
  () =>
    ({
      drug_indications: "treatments",
      drug_contraindications: "contraindicated drugs",
      drug_diagnostics: "diagnostic agents",
    })[props.sectionKey] ?? `${groupNoun.value}s`,
);
/** tab picked by the user; until then, direct when there are direct rows */
const selectedTab = ref<"direct" | "all" | null>(null);
/** drug counts for the two tabs under the current filters (kept while reloading) */
const directCount = ref(0);
const allCount = ref(0);
const activeTab = computed(
  () => selectedTab.value ?? (directCount.value > 0 ? "direct" : "all"),
);
const direct = computed(
  () => isDiseasePage.value && activeTab.value === "direct",
);

const predicateFilter = computed(() =>
  isIndications.value && !includeInvestigational.value
    ? [`predicate:(${APPROVED.map(solrQuote).join(" OR ")})`]
    : [],
);
const jurisdictionFilter = computed(() =>
  jurisdiction.value
    ? [`medic_jurisdiction:${solrQuote(jurisdiction.value)}`]
    : [],
);

const emptySummary: AssociationSummary = {
  total: 0,
  group_by: "",
  group_total: 0,
  offset: 0,
  limit: 0,
  unique: {},
  facets: {},
  groups: [],
};
const emptyTable = {
  items: [],
  total: 0,
  limit: 0,
  offset: 0,
} as unknown as AssociationTableResults;

const groups = ref<AssociationSummaryGroup[]>([]);
/** level 1 row total, kept while a page loads so the pager doesn't flicker */
const groupTotal = ref(0);
/** level 1 paging, server-side: each page is one summary request */
const perPage = ref(PAGE);
const start = ref(0);

/** level 1: one bucket per drug / condition */
const summary = useQuery(
  async () =>
    getAssociationSummary(props.node.id, props.sectionKey, {
      groupBy: side.value,
      uniqueFields: ["grouping_key"],
      statFields: ["medic_approval_date"],
      labelFields: [labelField.value, categoryField.value],
      facetFields: ["medic_jurisdiction", secondaryField.value],
      facetLabels: { [secondaryField.value]: `${secondaryField.value}_label` },
      direct: direct.value,
      filterQueries: [...predicateFilter.value, ...jurisdictionFilter.value],
      offset: start.value,
      limit: perPage.value,
    }),
  emptySummary,
  (response) => {
    groups.value = response.groups;
    groupTotal.value = response.group_total;
  },
);

/** level 0 chips: how many drugs / conditions each jurisdiction covers */
const jurisdictions = useQuery(
  async () =>
    getAssociationSummary(props.node.id, props.sectionKey, {
      groupBy: "medic_jurisdiction",
      uniqueFields: [side.value],
      direct: direct.value,
      filterQueries: predicateFilter.value,
    }),
  emptySummary,
);

/** level 0: drugs / conditions whose only uses here are investigational */
const predicates = useQuery(
  async () =>
    getAssociationSummary(props.node.id, props.sectionKey, {
      groupBy: "predicate",
      uniqueFields: [side.value],
      direct: direct.value,
    }),
  emptySummary,
);
const investigationalCount = computed(() =>
  predicates.data.value.groups
    .filter((g) => !APPROVED.includes(g.value))
    .reduce((n, g) => n + (g.unique[side.value] ?? 0), 0),
);

const expanded = ref<string | null>(null);
const openStatement = ref<string | null>(null);

/** level 2: distinct statements (grouping_key) for one drug / condition */
const statements = useQuery(
  async (value: string) =>
    getAssociationSummary(props.node.id, props.sectionKey, {
      groupBy: "grouping_key",
      statFields: ["medic_approval_date"],
      labelFields: ["predicate", "object", "object_label", "object_category"],
      facetFields: [
        "medic_jurisdiction",
        "disease_context_qualifier",
        "population_context_qualifier",
      ],
      facetLabels: {
        disease_context_qualifier: "disease_context_qualifier_label",
      },
      direct: direct.value,
      filterQueries: [
        `${side.value}:${solrQuote(value)}`,
        ...predicateFilter.value,
        ...jurisdictionFilter.value,
      ],
      limit: 50,
    }),
  emptySummary,
);

/** level 3: the label assertions behind one statement */
const assertions = useQuery(
  async (groupingKey: string) =>
    getAssociations(
      props.node.id,
      props.sectionKey,
      0,
      200,
      false,
      String(direct.value),
      undefined,
      null,
      undefined,
      [`grouping_key:${solrQuote(groupingKey)}`, ...jurisdictionFilter.value],
    ),
  emptyTable,
);

/** the tab counts: one cheap summary per tab, read for its distinct-group total */
const tabCounts = useQuery(
  async () => {
    const count = (directOnly: boolean) =>
      getAssociationSummary(props.node.id, props.sectionKey, {
        groupBy: side.value,
        direct: directOnly,
        filterQueries: [...predicateFilter.value, ...jurisdictionFilter.value],
        offset: 0,
        limit: 1,
      }).then((response) => response.group_total);
    return Promise.all([count(true), count(false)]);
  },
  [0, 0] as number[],
  ([directTotal, allTotal]) => {
    directCount.value = directTotal;
    allCount.value = allTotal;
  },
);

const loadPage = () => {
  expanded.value = null;
  openStatement.value = null;
  summary.query();
};
/** back to the first page; the start watcher loads it unless already there */
const firstPage = () => {
  if (start.value === 0) loadPage();
  else start.value = 0;
};
/** recount the tabs first (on disease pages) so the default tab is settled */
const reload = async (next: unknown[] = [], previous: unknown[] = []) => {
  if (next[0] !== previous[0] || next[1] !== previous[1])
    selectedTab.value = null;
  if (isDiseasePage.value) await tabCounts.query();
  firstPage();
  jurisdictions.query();
  predicates.query();
};
watch(
  () => [
    props.node.id,
    props.sectionKey,
    jurisdiction.value,
    includeInvestigational.value,
  ],
  reload,
  { immediate: true },
);

watch([start, perPage], loadPage);
/** a tab click: the list and the chip counts both depend on direct vs. inferred */
const selectTab = (which: "direct" | "all") => {
  selectedTab.value = which;
  firstPage();
  jurisdictions.query();
  predicates.query();
};

const toggleJurisdiction = (value: string) =>
  (jurisdiction.value = jurisdiction.value === value ? null : value);

const toggleGroup = (value: string) => {
  openStatement.value = null;
  expanded.value = expanded.value === value ? null : value;
  if (expanded.value) statements.query(value);
};

const toggleStatement = (value: string) => {
  openBlocks.value = new Set();
  openStatement.value = openStatement.value === value ? null : value;
  if (openStatement.value) assertions.query(value);
};

/** how many distinct indication texts a jurisdiction shows before "show more" */
const TEXTS_SHOWN = 2;

type TextGroup = {
  text: string;
  rows: DirectionalAssociation[];
  links: string[];
  firstApproved: string;
};
type AssertionBlock = {
  jurisdiction: string;
  labelCount: number;
  sources: string[];
  texts: TextGroup[];
};

/**
 * level 3 rows, grouped by jurisdiction and then by indication text: generic
 * and combination products repeat the same text across many labels, so each
 * distinct text is shown once with links to every label that carries it
 */
const assertionBlocks = computed<AssertionBlock[]>(() => {
  const blocks = new Map<string, Map<string, DirectionalAssociation[]>>();
  for (const row of assertions.data.value.items) {
    const jurisdiction = String(rowField(row, "medic_jurisdiction") ?? "");
    const text = (row.supporting_text ?? []).join(" ").trim() || "(no text)";
    if (!blocks.has(jurisdiction)) blocks.set(jurisdiction, new Map());
    const texts = blocks.get(jurisdiction)!;
    texts.set(text, [...(texts.get(text) ?? []), row]);
  }
  return [...blocks.entries()]
    .map(([jurisdiction, texts]) => {
      const rows = [...texts.values()].flat();
      return {
        jurisdiction,
        labelCount: rows.length,
        sources: [
          ...new Set(rows.map((r) => sourceName(r.primary_knowledge_source))),
        ],
        texts: [...texts.entries()]
          .map(([text, rows]) => ({
            text,
            rows,
            links: [
              ...new Set(rows.flatMap((r) => labelLinks(r).map((l) => l.url))),
            ],
            firstApproved:
              rows
                .map((r) => formatDate(rowField(r, "medic_approval_date")))
                .filter(Boolean)
                .sort()[0] ?? "",
          }))
          .sort((a, b) => b.rows.length - a.rows.length),
      };
    })
    .sort((a, b) => b.labelCount - a.labelCount);
});
const distinctTextCount = computed(() =>
  assertionBlocks.value.reduce((n, b) => n + b.texts.length, 0),
);

const openBlocks = ref(new Set<string>());
const toggleBlock = (jurisdiction: string) => {
  const next = new Set(openBlocks.value);
  if (next.has(jurisdiction)) next.delete(jurisdiction);
  else next.add(jurisdiction);
  openBlocks.value = next;
};
const visibleTexts = (block: AssertionBlock) =>
  openBlocks.value.has(block.jurisdiction)
    ? block.texts
    : block.texts.slice(0, TEXTS_SHOWN);

const showModal = ref(false);
const selectedAssociation = ref<DirectionalAssociation | null>(null);
const openDetails = (row: DirectionalAssociation) => {
  selectedAssociation.value = row;
  showModal.value = true;
};

/** MeDIC's extra columns aren't in the generated model */
const rowField = (row: DirectionalAssociation, field: string) =>
  (row as unknown as Record<string, unknown>)[field];

/** links to the label documents behind an assertion */
const labelLinks = (row: DirectionalAssociation) => {
  const sources = parseRetrievalSources(
    (row as { sources?: string[] }).sources,
  );
  const urls = sources.flatMap((s) => s.source_record_urls ?? []);
  // DailyMed records carry both the label page and its PDF; keep the page
  const pages = urls.filter(
    (url) => url.startsWith("http") && !url.includes("downloadpdffile"),
  );
  return (
    pages.length ? pages : urls.filter((url) => url.startsWith("http"))
  ).map((url) => ({
    url,
    text:
      url.includes("downloadpdffile") || url.endsWith(".pdf") ? "PDF" : "Label",
  }));
};

const JURISDICTIONS: Record<string, [string, string]> = {
  USA: ["United States", "US"],
  EU: ["European Union", "EU"],
  JAPAN: ["Japan", "JP"],
  INDIA: ["India", "IN"],
};
const jurisdictionName = (value: string) => JURISDICTIONS[value]?.[0] ?? value;
const jurisdictionAbbrev = (value: string) =>
  JURISDICTIONS[value]?.[1] ?? value;

const SOURCES: Record<string, string> = {
  "infores:fda-dailymed": "DailyMed",
  "infores:ema": "EMA",
  "infores:pmda": "PMDA",
  "infores:cdsco": "CDSCO",
  "infores:pubmed": "PubMed",
  "infores:ctd": "CTD",
  "infores:cureid": "CURE ID",
};
const sourceName = (value?: string | null) =>
  value ? (SOURCES[value] ?? value.replace("infores:", "")) : "";

const PREDICATES: Record<string, string> = {
  "biolink:treats": "treats",
  "biolink:preventative_for_condition": "prevents",
  "biolink:contraindicated_in": "contraindicated in",
  "biolink:diagnoses": "diagnoses",
  "biolink:in_clinical_trials_for": "in clinical trials for",
  "biolink:studied_to_treat": "studied to treat",
  "biolink:applied_to_treat": "applied to treat",
};
const predicateLabel = (value?: string | null) =>
  value
    ? (PREDICATES[value] ?? value.replace("biolink:", "").replace(/_/g, " "))
    : "";

/** approval dates are yyyymmdd strings */
const year = (value?: string | null) =>
  value && /^\d{4}/.test(value) ? `since ${value.slice(0, 4)}` : "";
const formatDate = (value: unknown) => {
  const s = String(value ?? "");
  return /^\d{8}$/.test(s)
    ? `${s.slice(0, 4)}-${s.slice(4, 6)}-${s.slice(6, 8)}`
    : "";
};

const plural = (n: number, noun: string) =>
  `${n.toLocaleString()} ${noun}${n === 1 ? "" : "s"}`;
</script>

<style lang="scss" scoped>
.drug-uses {
  display: flex;
  flex-direction: column;
  gap: 12px;
  text-align: left;
}

.overview {
  margin: 0;
}

.muted {
  color: $dark-gray;
}

.pager {
  margin-top: 15px;
}
.chips {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.chip {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  gap: 6px;
  border: 1px solid $light-gray;
  border-radius: 999px;
  background: $white;
  font: inherit;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background $fast;

  &:hover {
    background: $off-white;
  }

  &.active {
    border-color: $theme;
    background: $theme;
    color: $white;

    .chip-count {
      color: $white;
    }
  }
}

.chip-count {
  color: $dark-gray;
  font-weight: 600;
}

.chip-sep {
  width: 1px;
  height: 20px;
  background: $light-gray;
}

.groups,
.statements ul,
.populations {
  margin: 0;
  padding: 0;
  list-style: none;
}

.group {
  border-bottom: 1px solid $light-gray;
}

.group-row,
.statement-row {
  cursor: pointer;

  &:hover {
    background: $off-white;
  }

  &:focus-visible {
    outline: none;
    box-shadow: $outline;
  }
}

.group-row {
  display: grid;
  grid-template-columns: 24px 220px 1fr 200px 90px;
  align-items: center;
  padding: 8px 0;
  gap: 12px;
}

.group-node {
  justify-self: start;
}

.targets {
  overflow: hidden;
  font-size: 0.9rem;
  text-overflow: ellipsis;
}

.where {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 4px;
}

.pill {
  padding: 1px 6px;
  border-radius: $rounded;
  background: $light-gray;
  font-size: 0.8rem;
  white-space: nowrap;
}

.pill-count {
  color: $dark-gray;
}

.since {
  font-size: 0.85rem;
  text-align: right;
}

.statements {
  margin: 0 0 10px 36px;
  padding-left: 12px;
  border-left: 2px solid $theme-light;
}

.statement {
  padding: 4px 0;
}

.statement-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  width: 100%;
  padding: 4px 0;
  gap: 8px;

  .where {
    margin-left: auto;
  }
}

.predicate {
  color: $theme;
  font-weight: 600;
}

.context {
  padding: 1px 6px;
  border-radius: $rounded;
  background: $theme-light;
  font-size: 0.8rem;
}

.populations {
  margin-left: 24px;
  color: $off-black;
  font-size: 0.85rem;

  li::before {
    content: "↳ ";
    color: $gray;
  }
}

.assertions {
  display: flex;
  flex-direction: column;
  margin: 6px 0 6px 24px;
  gap: 10px;
}

.assertion {
  align-self: stretch;
  padding: 8px 10px;
  border-radius: $rounded;
  background: $off-white;
}

.assertion-summary {
  margin: 0;
  font-size: 0.85rem;
}

.jurisdiction-block {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
}

.jurisdiction-head {
  margin: 4px 0 0;
  font-size: 0.95rem;
}

.assertion-links {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  margin-top: 4px;
  gap: 4px 10px;
  font-size: 0.8rem;
}

.link {
  padding: 0;
  border: none;
  background: none;
  color: $theme;
  font: inherit;
  font-size: 0.85rem;
  text-decoration: underline;
  cursor: pointer;
}

.supporting {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  margin: 6px 0 0;
  overflow: hidden;
  font-size: 0.85rem;
  -webkit-box-orient: vertical;
}

@media (max-width: 800px) {
  .group-row {
    grid-template-columns: 24px 1fr;

    .targets,
    .where,
    .since {
      grid-column: 2;
      text-align: left;
    }
  }
}
</style>
