<!--
  drug ↔ condition sections (indications, contraindications, diagnostic uses),
  summarized with facets rather than listed edge by edge. progressive
  disclosure: section overview → one row per drug (or condition, on a drug
  page) → its distinct statements → the label assertions behind a statement.
-->

<template>
  <div class="drug-uses">
    <!-- these sections summarize regulator labels: not clinical guidance -->
    <AppAlert icon="circle-exclamation" class="notice">
      <div>
        <p>
          For research purposes only. This information is not intended to
          diagnose, treat, cure, or prevent any disease, and does not replace
          approved prescribing information or the advice of a healthcare
          professional.
        </p>
        <p v-if="sectionKey === 'drug_contraindications'">
          A drug not listed here is not known to be safe for this condition;
          this list is not a complete record of contraindications.
        </p>
        <AppButton
          v-if="!acknowledged"
          class="acknowledge"
          :text="`I understand, show ${sectionNoun}`"
          @click="onAcknowledge"
        />
      </div>
    </AppAlert>

    <!-- focused after "I understand" so keyboard users land on the content -->
    <div
      v-if="acknowledged"
      ref="content"
      class="content"
      tabindex="-1"
      role="region"
      :aria-label="sectionLabel ?? sectionNoun"
    >
      <!-- direct vs. inferred (subtypes), as in the other association sections -->
      <AppAssociationTabs
        v-if="hasTabs && allCount > 0"
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
          from {{ plural(summary.data.value.total, "assertion") }}
        </span>
        <AppProvenanceIcons
          class="overview-provenance"
          show-labels
          :agent-types="facetValues(summary.data.value.facets.agent_type)"
          :knowledge-levels="
            facetValues(summary.data.value.facets.knowledge_level)
          "
        />
      </p>
      <AppStatus v-else-if="summary.isLoading.value" code="loading"
        >Loading summary</AppStatus
      >
      <AppStatus v-else-if="summary.isError.value" code="error"
        >Error loading {{ sectionNoun }}</AppStatus
      >

      <div class="chips">
        <button
          v-for="j in chips"
          :key="j.value"
          :class="['chip', { active: jurisdiction === j.value }]"
          :aria-pressed="jurisdiction === j.value"
          :title="`Only show ${groupNoun}s with a ${jurisdictionName(j.value)} label`"
          @click="toggleJurisdiction(j.value)"
        >
          {{ jurisdictionName(j.value) }}
          <span class="chip-count">{{ j.count }}</span>
        </button>
        <template
          v-if="
            predicateState.showToggle &&
            (investigationalCount > 0 || includeInvestigational)
          "
        >
          <span class="chip-sep" />
          <button
            :class="['chip', { active: includeInvestigational }]"
            :aria-pressed="includeInvestigational"
            :title="`${plural(investigationalCount, groupNoun)} with only clinical-trial, studied or off-label (applied) uses`"
            @click="includeInvestigational = !includeInvestigational"
          >
            + investigational
            <span class="chip-count">{{ investigationalCount }}</span>
          </button>
        </template>
      </div>

      <!-- level 1: one row per drug / condition -->
      <ul v-if="!summary.isError.value" class="groups">
        <li
          v-for="(group, groupIndex) in groups"
          :key="group.value"
          class="group"
        >
          <!--
            disclosure: the expand button is the control; the row is also
            clickable as a mouse convenience, and names inside it are links
          -->
          <!-- eslint-disable-next-line vuejs-accessibility/click-events-have-key-events, vuejs-accessibility/no-static-element-interactions -->
          <div class="group-row" @click="toggleGroup(group.value)">
            <button
              class="expand"
              :aria-expanded="expanded === group.value"
              :aria-controls="`${sectionKey}-statements-${groupIndex}`"
              :aria-label="`Statements for ${group.fields[labelField] ?? group.value}`"
              @click.stop="toggleGroup(group.value)"
            >
              <AppIcon
                :icon="expanded === group.value ? 'angle-down' : 'angle-right'"
              />
            </button>
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
              <span v-if="moreTargets(group) > 0" class="muted">
                +{{ moreTargets(group) }} more</span
              >
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
            <AppProvenanceIcons
              class="provenance-cell"
              :agent-types="facetValues(group.facets.agent_type)"
              :knowledge-levels="facetValues(group.facets.knowledge_level)"
            />
            <span class="since muted">{{
              year(group.stats.medic_approval_date?.min)
            }}</span>
          </div>

          <!-- level 2: distinct statements for this drug / condition -->
          <div
            v-if="expanded === group.value"
            :id="`${sectionKey}-statements-${groupIndex}`"
            class="statements"
          >
            <AppStatus v-if="statements.isLoading.value" code="loading"
              >Loading statements</AppStatus
            >
            <AppStatus v-else-if="statements.isError.value" code="error"
              >Error loading statements</AppStatus
            >
            <ul v-else>
              <li
                v-for="(st, statementIndex) in statements.data.value.groups"
                :key="st.value"
                class="statement"
              >
                <!-- mouse convenience; the expand button is the keyboard control -->
                <!-- eslint-disable-next-line vuejs-accessibility/click-events-have-key-events, vuejs-accessibility/no-static-element-interactions -->
                <div class="statement-row" @click="toggleStatement(st.value)">
                  <button
                    class="expand"
                    :aria-expanded="openStatement === st.value"
                    :aria-controls="`${sectionKey}-assertions-${statementIndex}`"
                    :aria-label="`Assertions for ${predicateLabel(st.fields.predicate)} ${st.fields.object_label ?? st.fields.object ?? ''}`"
                    @click.stop="toggleStatement(st.value)"
                  >
                    <AppIcon
                      :icon="
                        openStatement === st.value
                          ? 'angle-down'
                          : 'angle-right'
                      "
                    />
                  </button>
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
                  <AppProvenanceIcons
                    :agent-types="facetValues(st.facets.agent_type)"
                    :knowledge-levels="facetValues(st.facets.knowledge_level)"
                  />
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
                <div
                  v-if="openStatement === st.value"
                  :id="`${sectionKey}-assertions-${statementIndex}`"
                  class="assertions"
                >
                  <AppStatus v-if="assertions.isLoading.value" code="loading"
                    >Loading assertions</AppStatus
                  >
                  <AppStatus v-else-if="assertions.isError.value" code="error"
                    >Error loading assertions</AppStatus
                  >
                  <template v-else>
                    <p class="muted assertion-summary">
                      {{ plural(assertions.data.value.total, "assertion")
                      }}<template v-if="distinctTextCount">
                        ·
                        {{
                          plural(distinctTextCount, "distinct supporting text")
                        }}</template
                      >
                    </p>
                    <div
                      v-for="block in assertionBlocks"
                      :key="block.jurisdiction"
                      class="jurisdiction-block"
                    >
                      <h4 class="jurisdiction-head">
                        {{
                          block.jurisdiction
                            ? jurisdictionName(block.jurisdiction)
                            : "Other sources"
                        }}
                        <span class="muted"
                          >{{ plural(block.labelCount, recordNoun(block)) }} ·
                          {{ block.sources.join(", ") }}</span
                        >
                      </h4>
                      <div
                        v-for="text in visibleTexts(block)"
                        :key="text.text"
                        class="assertion"
                      >
                        <p v-if="text.text" class="supporting">
                          {{ text.text }}
                        </p>
                        <!-- no text (CURE ID): the publication is the evidence -->
                        <p v-else class="supporting">
                          Reported in
                          <template
                            v-for="(pub, i) in text.publications"
                            :key="pub"
                            ><span v-if="i">, </span
                            ><a
                              v-if="publicationUrl(pub)"
                              :href="publicationUrl(pub)"
                              target="_blank"
                              rel="noopener"
                              >{{ pub }}</a
                            ><span v-else>{{ pub }}</span></template
                          ><span v-if="!text.publications.length">{{
                            block.sources.join(", ")
                          }}</span>
                        </p>
                        <div class="assertion-links">
                          <span class="muted">{{
                            plural(text.rows.length, recordNoun(block))
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
                            >{{ recordNoun(block) }} {{ i + 1 }}</a
                          >
                          <span v-if="text.links.length > 8" class="muted"
                            >+{{ text.links.length - 8 }} more</span
                          >
                          <template v-if="text.text">
                            <a
                              v-for="pub in text.publications.filter(
                                publicationUrl,
                              )"
                              :key="pub"
                              :href="publicationUrl(pub)"
                              target="_blank"
                              rel="noopener"
                              >{{ pub }}</a
                            >
                          </template>
                          <AppProvenanceIcons
                            :agent-types="
                              text.rows
                                .map((r) => r.agent_type ?? '')
                                .filter(Boolean)
                            "
                            :knowledge-levels="
                              text.rows
                                .map((r) => r.knowledge_level ?? '')
                                .filter(Boolean)
                            "
                          />
                          <button
                            class="link"
                            @click="openDetails(text.rows[0])"
                          >
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
                            : `show ${block.texts.length - TEXTS_SHOWN} more texts`
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
                      {{ assertions.data.value.total }} assertions.
                    </p>
                  </template>
                </div>
              </li>
            </ul>
            <p
              v-if="
                statements.isSuccess.value &&
                statements.data.value.group_total >
                  statements.data.value.groups.length
              "
              class="muted"
            >
              Showing the first {{ statements.data.value.groups.length }} of
              {{ statements.data.value.group_total }} statements.
            </p>
          </div>
        </li>
      </ul>

      <TheTableControls
        v-if="groupTotal > 0 && !summary.isError.value"
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
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";
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
import AppAlert from "@/components/AppAlert.vue";
import AppAssociationTabs from "@/components/AppAssociationTabs.vue";
import AppButton from "@/components/AppButton.vue";
import AppIcon from "@/components/AppIcon.vue";
import AppLink from "@/components/AppLink.vue";
import AppModal from "@/components/AppModal.vue";
import AppNodeBadge from "@/components/AppNodeBadge.vue";
import AppProvenanceIcons from "@/components/AppProvenanceIcons.vue";
import AppStatus from "@/components/AppStatus.vue";
import TheTableControls from "@/components/TheTableContols.vue";
import { useQuery } from "@/composables/use-query";
import { useResearchUseAcknowledgement } from "@/composables/use-research-use-acknowledgement";
import SectionAssociationDetails from "@/pages/node/SectionAssociationDetails.vue";
import {
  defaultPredicatesFor,
  predicateFilterState,
} from "@/util/predicateFilterConfig";
import { parseRetrievalSources } from "@/util/retrievalSources";

type Props = {
  node: Node;
  /** association-type section key, e.g. drug_indications */
  sectionKey: string;
  /** the section's heading, e.g. "Treatments"; the tabs reuse it */
  sectionLabel?: string;
};

const props = defineProps<Props>();

const PAGE = 10;

/**
 * the section's content stays hidden until the research-use notice is
 * acknowledged
 */
const { acknowledged, acknowledge } = useResearchUseAcknowledgement();
const content = ref<HTMLElement | null>(null);
/** acknowledge, then move focus to the content the button revealed */
const onAcknowledge = async () => {
  acknowledge();
  await nextTick();
  content.value?.focus();
};

const isDiseasePage = computed(() =>
  ["biolink:Disease", "biolink:PhenotypicFeature"].includes(
    props.node.category ?? "",
  ),
);
/** direct/inferred tabs on disease pages only, as in SectionAssociations */
const hasTabs = computed(() => props.node.category === "biolink:Disease");

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
const sectionNoun = computed(() =>
  (props.sectionLabel ?? `${groupNoun.value}s`).toLowerCase(),
);
/** tab picked by the user; until then, direct when there are direct rows */
const selectedTab = ref<"direct" | "all" | null>(null);
type TabCounts = { direct: number; all: number };
/**
 * drug / condition counts per tab under the jurisdiction filter, with and
 * without the approved-only predicate filter (kept while reloading)
 */
const approvedCounts = ref<TabCounts>({ direct: 0, all: 0 });
const anyCounts = ref<TabCounts>({ direct: 0, all: 0 });
const shownCounts = computed(() =>
  predicateState.value.filterIds.length
    ? approvedCounts.value
    : anyCounts.value,
);
const directCount = computed(() => shownCounts.value.direct);
const allCount = computed(() => shownCounts.value.all);
const activeTab = computed(
  () => selectedTab.value ?? (directCount.value > 0 ? "direct" : "all"),
);
const direct = computed(() => hasTabs.value && activeTab.value === "direct");

/** the predicates present in this section for this node (any tab, no filters) */
const predicateIds = ref<string[]>([]);
/**
 * approved-only by default when the section also has investigational uses; no
 * filter when only one kind is present, so the section is never empty
 */
const predicateState = computed(() =>
  predicateFilterState(
    props.sectionKey,
    predicateIds.value,
    includeInvestigational.value,
  ),
);
const approvedFilter = computed(() => {
  const ids = predicateFilterState(
    props.sectionKey,
    predicateIds.value,
    false,
  ).filterIds;
  return ids.length ? [`predicate:(${ids.map(solrQuote).join(" OR ")})`] : [];
});
const predicateFilter = computed(() =>
  predicateState.value.filterIds.length ? approvedFilter.value : [],
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
      uniqueFields: ["grouping_key", secondaryField.value],
      statFields: ["medic_approval_date"],
      labelFields: [labelField.value, categoryField.value],
      facetFields: [
        "medic_jurisdiction",
        secondaryField.value,
        "agent_type",
        "knowledge_level",
      ],
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
const jurisdictionChips = ref<AssociationSummaryGroup[]>([]);
const jurisdictions = useQuery(
  async () =>
    getAssociationSummary(props.node.id, props.sectionKey, {
      groupBy: "medic_jurisdiction",
      uniqueFields: [side.value],
      direct: direct.value,
      filterQueries: predicateFilter.value,
    }),
  emptySummary,
  (response) => (jurisdictionChips.value = response.groups),
);

/** which predicates this section has here, for the approved-only default */
const predicates = useQuery(
  async () =>
    defaultPredicatesFor(props.sectionKey)
      ? getAssociationSummary(props.node.id, props.sectionKey, {
          groupBy: "predicate",
          direct: false,
        })
      : emptySummary,
  emptySummary,
  (response) => (predicateIds.value = response.groups.map((g) => g.value)),
);
/** drugs / conditions that only "+ investigational" adds, on the current tab */
const investigationalCount = computed(() => {
  const tab = direct.value ? "direct" : "all";
  return anyCounts.value[tab] - approvedCounts.value[tab];
});

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
        "agent_type",
        "knowledge_level",
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

/**
 * the tab and "+ investigational" counts: cheap summaries read for their
 * distinct-group totals, per tab, with and without the approved-only filter
 */
const tabCounts = useQuery(
  async () => {
    const count = (directOnly: boolean, filters: string[]) =>
      getAssociationSummary(props.node.id, props.sectionKey, {
        groupBy: side.value,
        direct: directOnly,
        filterQueries: [...filters, ...jurisdictionFilter.value],
        offset: 0,
        limit: 1,
      }).then((response) => response.group_total);
    const both = async (filters: string[]): Promise<TabCounts> => {
      const [directTotal, allTotal] = await Promise.all([
        hasTabs.value ? count(true, filters) : 0,
        count(false, filters),
      ]);
      return { direct: directTotal, all: allTotal };
    };
    const any = await both([]);
    const approved = approvedFilter.value.length
      ? await both(approvedFilter.value)
      : any;
    return { any, approved };
  },
  { any: { direct: 0, all: 0 }, approved: { direct: 0, all: 0 } },
  ({ any, approved }) => {
    anyCounts.value = any;
    approvedCounts.value = approved;
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
/**
 * recount before loading rows, so the default tab and the approved-only filter
 * are settled first; the chips only change with the node, tab or predicate
 * filter, not with the jurisdiction picked
 */
const reload = async ({
  newNode = false,
  chips = true,
}: { newNode?: boolean; chips?: boolean } = {}) => {
  if (newNode) {
    selectedTab.value = null;
    await predicates.query();
  }
  await tabCounts.query();
  // a chosen tab that a filter has emptied goes back to the default
  if (selectedTab.value === "direct" && directCount.value === 0)
    selectedTab.value = null;
  firstPage();
  if (chips) jurisdictions.query();
};
/** nothing is fetched until the research-use notice is acknowledged */
watch(
  () => [props.node.id, props.sectionKey, acknowledged.value],
  () => {
    if (acknowledged.value) reload({ newNode: true });
  },
  { immediate: true },
);
watch(includeInvestigational, () => reload());
watch(jurisdiction, () => reload({ chips: false }));

watch([start, perPage], loadPage);
/** a tab click: the list and the chip counts both depend on direct vs. inferred */
const selectTab = (which: "direct" | "all") => {
  selectedTab.value = which;
  firstPage();
  jurisdictions.query();
};

/** the values of a summary facet, e.g. the agent types behind a row */
const facetValues = (values?: { value: string }[]) =>
  (values ?? []).map((v) => v.value);

/** a row's conditions / contexts beyond the ones its facet lists */
const moreTargets = (group: AssociationSummaryGroup) =>
  (group.unique[secondaryField.value] ?? 0) -
  (group.facets[secondaryField.value]?.length ?? 0);

/**
 * the jurisdiction chips, keeping the selected one even when the current
 * filters leave it no rows, so it can always be turned off
 */
const chips = computed(() => {
  const list = jurisdictionChips.value.map((j) => ({
    value: j.value,
    count: j.unique[side.value] ?? 0,
  }));
  if (jurisdiction.value && !list.some((j) => j.value === jurisdiction.value))
    list.push({ value: jurisdiction.value, count: 0 });
  return list;
});

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
  /** supporting text, else the curator's description; "" when neither */
  text: string;
  rows: DirectionalAssociation[];
  links: string[];
  /** PMIDs behind the rows (CURE ID and PubMed records) */
  publications: string[];
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
    // rows with no text (CURE ID) group by the publications they cite instead
    const key =
      rowText(row) || `publications:${(row.publications ?? []).join(" ")}`;
    if (!blocks.has(jurisdiction)) blocks.set(jurisdiction, new Map());
    const texts = blocks.get(jurisdiction)!;
    texts.set(key, [...(texts.get(key) ?? []), row]);
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
        texts: [...texts.values()]
          .map((rows) => ({
            text: rowText(rows[0]),
            rows,
            links: [
              ...new Set(rows.flatMap((r) => labelLinks(r).map((l) => l.url))),
            ],
            publications: [
              ...new Set(rows.flatMap((r) => r.publications ?? [])),
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
/** what an assertion says: its supporting text, else its description */
const rowText = (row: DirectionalAssociation) =>
  (row.supporting_text ?? []).join(" ").trim() ||
  String(rowField(row, "description") ?? "").trim();

/** PubMed link for a PMID, else none */
const publicationUrl = (id: string) =>
  id.startsWith("PMID:")
    ? `https://pubmed.ncbi.nlm.nih.gov/${id.slice("PMID:".length)}`
    : undefined;

/** non-label sources (CURE ID, PubMed) carry no jurisdiction */
const recordNoun = (block: AssertionBlock) =>
  block.jurisdiction ? "label" : "record";
const distinctTextCount = computed(() =>
  assertionBlocks.value.reduce(
    (n, b) => n + b.texts.filter((t) => t.text).length,
    0,
  ),
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
}

/* the disclosure control at the start of a row */
.expand {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  padding: 0;
  border: none;
  border-radius: $rounded;
  background: none;
  color: inherit;
  cursor: pointer;

  &:focus-visible {
    outline: none;
    box-shadow: $outline;
  }
}

/* receives focus after "I understand"; no ring around the whole section */
.content:focus {
  outline: none;
}

.group-row {
  display: grid;
  grid-template-columns: 24px 220px 1fr 200px 64px 90px;
  align-items: center;
  padding: 8px 0;
  gap: 12px;
}

.group-node {
  justify-self: start;
}

.notice {
  justify-content: flex-start;
  margin-bottom: 15px;
  padding: 12px 16px;
  gap: 14px;
  border-left: 4px solid $error;
  background: rgba($error, 0.08);
  color: $off-black;
  font-size: 0.9rem;
  text-align: left;

  :deep(.icon) {
    color: $error;
    font-size: 1.2rem;
  }

  p {
    margin: 0;
  }

  p + p {
    margin-top: 6px;
    font-weight: 600;
  }

  .acknowledge {
    margin-top: 10px;
  }
}

.overview-provenance {
  margin-left: 12px;
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
    .provenance-cell,
    .since {
      grid-column: 2;
      text-align: left;
    }
  }
}
</style>
