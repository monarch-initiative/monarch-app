# Phenotype Similarity Settings

Monarch's phenotype similarity tools score how well a set of phenotypes matches another set, or every gene or disease in a group.
They're available as the [Phenotype Similarity](https://monarchinitiative.org/search-phenotypes) pages, the [Phenogrid](../Phenogrid/index.md) widget, and the [`/semsim` API endpoints](../FastAPI/Endpoints/semsim.md).

Every setting below has a default that reproduces Monarch's long-standing ranking.
The non-default values are experimental.

## How a score is built

1. **Each pair of phenotypes is scored** with the chosen [metric](#metric).
2. **Each phenotype is matched** to its most similar phenotype on the other side.
3. **The best-match scores are averaged** in the chosen [direction](#direction) to give the overall score.

In a search, the "other side" is each gene or disease in the group. Every result reports both direction scores, so you can see how much of the query it covers and how much of it the query covers.

## Settings

| Setting | API parameter | Values (default first) | Pages |
|---|---|---|---|
| [Metric](#metric) | `metric` | `ancestor_information_content`, `jaccard_similarity`, `phenodigm_score` | search, compare, Phenogrid |
| [Direction](#direction) | `directionality` | `bidirectional`, `object_to_subject`, `subject_to_object` | search, Phenogrid |
| [Candidates](#candidates) | `search_mode` | `hybrid`, `full` | search |
| [Information content](#information-content) | `information_content` | `ontology`, `annotation` | search, compare, Phenogrid |
| [Tie-break](#tie-break) | `tie_break` | `none`, `frequency` | search |
| [Default frequency](#tie-break) | `default_frequency` | `0.5` (0.01 to 1) | API only |

On the search page these are under **Advanced ranking settings**, and each has an info icon that explains it.
The page keeps changed settings in its URL, so a shared link keeps them too.

### Metric

How each pair of phenotypes is scored.

- **Ancestor information content** (default) scores how specific the most specific ancestor the two phenotypes share is. Which [information content](#information-content) is used depends on that setting.
- **Jaccard similarity** scores how much the two phenotypes' ancestors overlap.
- **Phenodigm** is the geometric mean of the other two.

### Direction

Which best matches are averaged into the score.
In a search, and in multicompare, the *subject* is each result and the *object* is the query.

- `bidirectional` (default) averages the two directions below.
- `object_to_subject`, **"How much of the query each result covers"**, averages over the query's phenotypes.
  A result isn't penalized for having many phenotypes the query doesn't mention, which matters for diseases with long phenotype profiles.
- `subject_to_object`, **"How much of each result the query covers"**, averages over the result's phenotypes.

For the plain compare endpoints (`/semsim/compare`), the subjects and objects are exactly the two sets you send. The compare page shows both directions as its A → B and B → A tabs.

### Candidates

Which entities a search scores.

- `hybrid` (default) first ranks every entity in the group by plain overlap with the query (Jaccard similarity of the phenotype sets), and scores only the top of that list.
  It's fast, but it can drop entities with many phenotypes before they are scored.
- `full` scores every entity in the group. It's slower, but nothing is dropped.

### Information content

Information content measures how specific, and so how informative, a phenotype is. It weights the [metric](#metric).

- `ontology` (default) comes from the ontology's structure: a term with fewer descendant terms counts for more.
  Every leaf term gets the same, maximum value, however common the phenotype is.
- `annotation` comes from how few entities carry the phenotype or a more specific one:
  IC(t) = log2(N / n(t)), where n(t) is the number of entities annotated to t or a descendant and N is the number of annotated entities.
  Rarely seen phenotypes count for more.

Annotation information content is computed during the knowledge graph build, separately for each group of entities:

| Group | Annotations used |
|---|---|
| Human Diseases | Mondo diseases' HP phenotypes |
| Human Genes | HGNC genes' HP phenotypes |
| Mouse Genes | MGI genes' MP phenotypes |
| Rat Genes | RGD genes' MP phenotypes |
| Zebrafish Genes | ZFIN genes' ZP phenotypes |
| C. Elegans Genes | WormBase genes' WBPhenotype phenotypes |

A search uses the group it searches. Compare and multicompare need a `group` parameter to choose one, for example `group=Human Diseases`. If the knowledge graph has no annotation information content for that group, the API answers with a 400 error that lists the entity prefixes it has annotation information content for, such as `MONDO`.

### Tie-break

How a search orders results with equal scores. Ties are common, for example when every query phenotype is annotated to several diseases.

- `none` (default) orders ties by entity ID.
- `frequency` ranks a result higher when the phenotypes matching the query are frequent in it.
  For each query phenotype it takes the result's closest matching phenotype (an exact annotation first), reads that annotation's recorded frequency, and multiplies those frequencies together.

Frequencies come from the annotations: a count such as "9 of 12 patients" or a percentage when one is recorded, otherwise the midpoint of the HPO frequency term (Obligate 100%, Very frequent 90%, Frequent 55%, Occasional 17%, Very rare 2.5%).
Annotations with no recorded frequency count as `default_frequency`, 50% unless set otherwise, and every frequency counts as at least 1%.
Model-organism annotations never record a frequency.

## Which backend serves a request

Monarch serves similarity from one of two engines.
Requests that use only the default settings go to the configured engine, as before. So do searches that change only `metric` or `directionality`.
Monarch's DuckDB engine serves any request that changes another setting, and any compare or multicompare request that changes `directionality` or `information_content`.
Search and multicompare results name the engine that scored them in `search_settings`.

## API examples

Search human diseases, averaging over the query and using annotation information content:

```bash
curl "https://api-v3.monarchinitiative.org/v3/api/semsim/search/HP:0001250,HP:0001263,HP:0003128/Human%20Diseases?directionality=object_to_subject&information_content=annotation"
```

The same search, scoring every disease and breaking ties by frequency:

```bash
curl -X POST "https://api-v3.monarchinitiative.org/v3/api/semsim/search" \
  -H "Content-Type: application/json" \
  -d '{
    "termset": ["HP:0001250", "HP:0001263", "HP:0003128"],
    "group": "Human Diseases",
    "directionality": "object_to_subject",
    "search_mode": "full",
    "tie_break": "frequency"
  }'
```

Each result includes:

- `score`, in the requested direction.
- `subject_to_object_score` and `object_to_subject_score`, both directions.
- `search_settings`, the settings and engine used.

For widget parameters, see [Phenogrid](../Phenogrid/index.md).
