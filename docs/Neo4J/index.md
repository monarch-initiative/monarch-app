# Neo4J

The Monarch Knowledge Graph is available as a Neo4j graph database, providing
direct graph query access via the Cypher query language.

## Neo4j Browser

Browse and query the Monarch KG interactively:

**[https://neo4j.monarchinitiative.org/browser/](https://neo4j.monarchinitiative.org/browser/)**

!!! note
    This is a **read-only** instance of the Monarch KG. You can run queries but
    cannot modify the data.

## Example Cypher Queries

### Find a disease by ID

```cypher
MATCH (d {id: 'MONDO:0007947'})
RETURN d
```

### Get phenotypes associated with a disease

```cypher
MATCH (d {id: 'MONDO:0007947'})-[r:`biolink:has_phenotype`]->(p)
RETURN d.name, r, p.name
LIMIT 25
```

### Find genes associated with a disease

```cypher
MATCH (d {id: 'MONDO:0007947'})-[r:`biolink:gene_associated_with_condition`]-(g)
RETURN g.name, g.id, type(r)
LIMIT 25
```

## Further Resources

- [KG Build Process](../KG-Build-Process/kg-build-process.md) — how the Neo4j database is built
- [KG Data Sources](../Sources/index.md) — the data sources included in the graph
