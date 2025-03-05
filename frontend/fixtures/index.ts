import { http, HttpResponse, passthrough } from "msw";
import { feedbackEndpoint } from "@/api/feedback";
import { efetch, esummary } from "@/api/publications";
import { uptimeRobot } from "@/api/uptime";
import associationsTable from "./association-table.json";
import associations from "./associations.json";
import autocomplete from "./autocomplete.json";
import feedback from "./feedback.json";
import histopheno from "./histopheno.json";
import nodePublicationAbstract from "./node-publication-abstract.json";
import nodePublicationSummary from "./node-publication-summary.json";
import node from "./node.json";
import phenotypeExplorerCompare from "./phenotype-explorer-compare.json";
import phenotypeExplorerMulticompare from "./phenotype-explorer-multi-compare.json";
import phenotypeExplorerSearch from "./phenotype-explorer-search.json";
import search from "./search.json";
import textAnnotator from "./text-annotator.json" with { type: "json" };
import uptime from "./uptime.json";

/** api calls to be mocked with fixture data */
export const handlers = [
  /** api status monitoring on /help */
  http.post(uptimeRobot, () => HttpResponse.json(uptime)),

  /** histopheno data */
  http.get("*/histopheno/:id", () => HttpResponse.json(histopheno)),

  /** submit feedback form */
  http.post(feedbackEndpoint, () => HttpResponse.json(feedback)),

  /** search * */
  http.get("*/search", () => HttpResponse.json(search)),

  /** autocomplete */
  http.get("*/autocomplete", () => HttpResponse.json(autocomplete)),

  /** text annotator */
  http.post("*/annotate", () => HttpResponse.json(textAnnotator)),

  /** phenotype explorer */
  http.post("*/semsim/search", () =>
    HttpResponse.json(phenotypeExplorerSearch),
  ),
  http.post("*/semsim/compare", () =>
    HttpResponse.json(phenotypeExplorerCompare),
  ),
  http.post("*/semsim/multicompare", () =>
    HttpResponse.json(phenotypeExplorerMulticompare),
  ),

  /** associations */
  http.get("*/association", () => HttpResponse.json(associations)),

  /** node associations */
  http.get("*/entity/:id/:assoctype", () =>
    HttpResponse.json(associationsTable),
  ),

  /** node lookup */
  http.get("*/entity/:id", ({ params }) => {
    const id = String(params.id);

    /**
     * change fixture data based on request so we can see UI that is conditional
     * on name/category/etc
     */
    const replace: {
      [key: string]: { name?: string; category?: string };
    } = {
      "MONDO:0007523": {
        name: "Ehlers-Danlos syndrome, hypermobility",
        category: "biolink:Disease",
      },
      "HP:0100775": {
        name: "Dural ectasia",
        category: "biolink:Disease",
      },
      "HP:0003179": {
        name: "Protrusio acetabuli",
        category: "biolink:Disease",
      },
      "HP:0001083": {
        name: "Ectopia lentis",
        category: "biolink:Disease",
      },
      "HP:0000501": {
        name: "Glaucoma",
        category: "biolink:Disease",
      },
      "HP:0002705": {
        name: "High, narrow palate",
        category: "biolink:Disease",
      },
      "HP:0004382": {
        name: "Mitral valve calcification",
        category: "biolink:Disease",
      },
      "HP:0004326": {
        name: "Cachexia",
        category: "biolink:Disease",
      },
      "HP:0002816": {
        name: "Genu recurvatum",
        category: "biolink:Disease",
      },
      "HP:0004298": {
        name: "Abnormality of the abdominal wall",
        category: "biolink:Disease",
      },
      "HP:0002996": {
        name: "Limited elbow movement",
        category: "biolink:Disease",
      },
      "MONDO:0020208": {
        name: "syndromic myopia",
        category: "biolink:Disease",
      },
      "PMID:25614286": {
        category: "biolink:Publication",
      },
    };
    const { name, category } = replace[id] || {};
    node.id = id;
    if (name) node.name = name;
    if (category) node.category = category;

    return HttpResponse.json(node);
  }),

  /** node publication info */
  http.get(esummary, () => HttpResponse.json(nodePublicationSummary)),
  http.get(efetch, () => HttpResponse.json(nodePublicationAbstract.abstract)),

  /** any other request */
  http.get("*", ({ request }) => {
    const { pathname } = new URL(request.url);
    if (!pathname.match(/\.[A-Za-z0-9]{2,5}$/))
      console.warn("Non-mocked request", pathname);
    return passthrough();
  }),
];
