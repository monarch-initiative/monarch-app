import { http, HttpResponse, passthrough } from "msw";
import { apiUrl, biolink } from "@/api";
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
import phenotypeExplorerSearch from "./phenotype-explorer-search.json";
import search from "./search.json";
import textAnnotator from "./text-annotator.json";
import uptime from "./uptime.json";

/** make single regex from base url and pattern */
const regex = (base: string = "", pattern: string = "") =>
  new RegExp(base + pattern.replace(/[/\\]/g, "\\$&"), "i");

/** api calls to be mocked with fixture data */
export const handlers = [
  /** api status monitoring on /help */
  http.post(regex(uptimeRobot), () => HttpResponse.json(uptime)),

  /** histopheno data */
  http.get(regex(apiUrl, "/histopheno"), () => HttpResponse.json(histopheno)),

  /** submit feedback form */
  http.post(regex(feedbackEndpoint), () => HttpResponse.json(feedback)),

  /** search * */
  http.get(regex(apiUrl, "/search"), () => HttpResponse.json(search)),

  /** autocomplete */
  http.get(regex(apiUrl, "/autocomplete"), () =>
    HttpResponse.json(autocomplete),
  ),

  /** text annotator */
  http.post(regex(biolink, "/nlp/annotate"), () =>
    HttpResponse.json(textAnnotator),
  ),

  /** phenotype explorer */
  http.get(regex(biolink, "/sim/search"), () =>
    HttpResponse.json(phenotypeExplorerSearch),
  ),
  http.post(regex(apiUrl, "/semsim/compare"), () =>
    HttpResponse.json(phenotypeExplorerCompare),
  ),

  /** node associations */
  http.get(regex(apiUrl, "/associations"), () =>
    HttpResponse.json(associations),
  ),

  /** node associations table */
  http.get(regex(apiUrl, "/entity/.*/.*"), () =>
    HttpResponse.json(associationsTable),
  ),

  /** node lookup */
  http.get(regex(apiUrl, "/entity/.*"), ({ request }) => {
    const { pathname } = new URL(request.url);
    const id = pathname.match(/\/entity\/(.*)/)?.[1] || "";

    console.log(regex(apiUrl, "/entity/:id"));
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
  http.get(regex(esummary), () => HttpResponse.json(nodePublicationSummary)),
  http.get(regex(efetch), () =>
    HttpResponse.json(nodePublicationAbstract.abstract),
  ),

  /** any other request */
  http.get(/.*/, ({ request }) => {
    const { pathname } = new URL(request.url);
    if (!pathname.match(/\.[A-Za-z0-9]{2,5}$/))
      console.warn("Non-mocked request", pathname);
    return passthrough();
  }),
];
