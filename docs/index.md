# monarch-py

## Introduction

**monarch-py** is a Python library for interacting with and querying the  
Monarch knowledge graph, with implementations for Solr and SQLite backends.

This means the same API methods can be used regardless of the implementation.

This library provides a collection of interfaces for graph operations such as retrieving entities and browsing associations.

## Installation

Requires Python 3.8 or higher

This library is available via pip or pipx:

```bash
pip install monarch-py
```

## Usage

Full usage instructions [here](./Usage/index.md)

### Basic Example - CLI

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

### Basic Example - As a Module

```python
>>> from monarch_py.implementations.solr.solr_implentation import SolrImplementation
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
