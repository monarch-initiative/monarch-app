# Monarch KG Documentation

Welcome to the documentation for the [Monarch Initiative](https://monarchinitiative.org/) knowledge graph and its associated tools.

The Monarch Knowledge Graph integrates data from dozens of biomedical sources, linking genes, diseases, phenotypes, and other biological entities to support translational research and clinical diagnostics.

## What's in this documentation

- **[KG Data Sources](Sources/index.md)** — Descriptions of each data source ingested into the Monarch KG
- **[KG Build Process](KG-Build-Process/kg-build-process.md)** — How the knowledge graph is assembled: download, transform, merge, and load
- **[Modeling Principles](Principles/modeling-principles.md)** — Guiding principles for data modeling in the Monarch KG
- **[Creating an Ingest](Creating-an-Ingest.md)** — How to add a new data source to the KG
- **[Neo4J](Neo4J/index.md)** — Access the Monarch KG via the Neo4j graph database browser
- **[Monarch R](MonarchR/index.md)** — The monarchr R package for accessing the Monarch KG from R
- **[FastAPI](FastAPI/index.md)** — The Monarch API backend
- **[monarch-py](#monarch-py)** — Python library for querying the Monarch KG
- **[Release Process](release-process.md)** — How Monarch KG releases are managed
- **[Licensing](Licensing/index.md)** — License recommendations for Monarch software and data

---

## monarch-py

**monarch-py** is a Python library for interacting with and querying the
Monarch knowledge graph, with implementations for Solr and SQLite backends.

This means the same API methods can be used regardless of the implementation.

This library provides a collection of interfaces for graph operations such as retrieving entities and browsing associations.

### Installation

Requires Python 3.8 or higher

This library is available via pip or pipx:

```bash
pip install monarch-py
```

### Usage

Full usage instructions [here](./Usage/index.md)

#### Basic Example - CLI

```bash
$ monarch sql entity MONDO:0012933
{
    "id": "MONDO:0012933",
    "category": [
        "biolink:Disease"
    ],
    "name": "breast-ovarian cancer, familial, susceptibility to, 2",
    "description": "Any hereditary breast ovarian cancer syndrome in which the cause of the disease is a mutation in the BRCA2 gene.",
    "xref": [],
    "provided_by": "phenio_nodes",
    "in_taxon": null,
    "source": null,
    "symbol": null,
    "type": null,
    "synonym": []
}
$ monarch associations --subject MONDO:0012933 --limit 5
{
    "limit": 5,
    "offset": 0,
    "total": 5,
    "associations": [
        ... # List of Associations
    ]
}
```

#### Basic Example - As a Module

```python
>>> from monarch_py.implementations.solr.solr_implementation import SolrImplementation
>>> si = SolrImplementation()
>>> entity = si.get_entity("MONDO:0007947")
>>> print(entity.name)
"Marfan syndrome"

>>> response = si.get_associations(predicate="biolink:has_phenotype")
>>> print(response.total > 600000)
True
>>> print("biolink:has_phenotype" in response.associations[0].predicate)
True
```
