# `monarch`

**Usage**:

```console
$ monarch [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--version / --no-version`
* `--quiet / --no-quiet`: [default: no-quiet]
* `--debug / --no-debug`: [default: no-debug]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `association-counts`: Retrieve association counts for an entity...
* `association-table`
* `associations`: Paginate through associations
* `autocomplete`: Return entity autcomplete matches for a...
* `entity`: Retrieve an entity by ID
* `histopheno`: Retrieve the histopheno data for an entity...
* `schema`: Print the linkml schema for the data model
* `search`: Search for entities
* `solr`
* `sql`
* `test`: Test the CLI

## `monarch association-counts`

Retrieve association counts for an entity by ID

Args:
    entity: The entity to get association counts for
    fmt: The format of the output (json, yaml, tsv, table). Default JSON
    output: The path to the output file. Default stdout

Returns:
    A list of association counts for the given entity containing association type, label and count

**Usage**:

```console
$ monarch association-counts [OPTIONS] [ENTITY]
```

**Arguments**:

* `[ENTITY]`: The entity to get association counts for

**Options**:

* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-o, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

## `monarch association-table`

**Usage**:

```console
$ monarch association-table [OPTIONS] ENTITY CATEGORY
```

**Arguments**:

* `ENTITY`: The entity to get associations for  [required]
* `CATEGORY`: The association category to get associations for, ex. biolink:GeneToPhenotypicFeatureAssociation  [required]

**Options**:

* `-q, --query TEXT`
* `-l, --limit INTEGER`: [default: 5]
* `--offset INTEGER`: [default: 0]
* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-o, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

## `monarch associations`

Paginate through associations

Args:
    category: A comma-separated list of categories
    subject: A comma-separated list of subjects
    predicate: A comma-separated list of predicates
    object: A comma-separated list of objects
    entity: A comma-separated list of entities
    limit: The number of associations to return
    direct: Whether to exclude associations with subject/object as ancestors
    offset: The offset of the first association to be retrieved
    fmt: The format of the output (json, yaml, tsv, table)
    output: The path to the output file (stdout if not specified)

**Usage**:

```console
$ monarch associations [OPTIONS]
```

**Options**:

* `-c, --category TEXT`: Comma-separated list of categories
* `-s, --subject TEXT`: Comma-separated list of subjects
* `-p, --predicate TEXT`: Comma-separated list of predicates
* `-o, --object TEXT`: Comma-separated list of objects
* `-e, --entity TEXT`: Comma-separated list of entities
* `-d, --direct`: Whether to exclude associations with subject/object as ancestors
* `-l, --limit INTEGER`: The number of associations to return  [default: 20]
* `--offset INTEGER`: The offset of the first association to be retrieved  [default: 0]
* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-o, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

## `monarch autocomplete`

Return entity autcomplete matches for a query string

Args:
    q: The query string to autocomplete against
    fmt: The format of the output (json, yaml, tsv, table)
    output: The path to the output file (stdout if not specified)

**Usage**:

```console
$ monarch autocomplete [OPTIONS] [Q]
```

**Arguments**:

* `[Q]`: Query string to autocomplete against

**Options**:

* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-o, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

## `monarch entity`

Retrieve an entity by ID

Args:
    id: The identifier of the entity to be retrieved
    fmt: The format of the output (json, yaml, tsv, table)
    output: The path to the output file (stdout if not specified)

**Usage**:

```console
$ monarch entity [OPTIONS] [ID]
```

**Arguments**:

* `[ID]`: The identifier of the entity to be retrieved

**Options**:

* `-e, --extra`: Include extra fields in the output (association_counts and node_hierarchy)
* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-o, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

## `monarch histopheno`

Retrieve the histopheno data for an entity by ID

Args:
    subject: The subject of the association

Optional Args:
    fmt (str): The format of the output (json, yaml, tsv, table). Default JSON
    output (str): The path to the output file. Default stdout

**Usage**:

```console
$ monarch histopheno [OPTIONS] [SUBJECT]
```

**Arguments**:

* `[SUBJECT]`: The subject of the association

**Options**:

* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-o, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

## `monarch schema`

Print the linkml schema for the data model

**Usage**:

```console
$ monarch schema [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `monarch search`

Search for entities

Args:
    q: The query string to search for
    category: The category of the entity
    taxon: The taxon of the entity
    limit: The number of entities to return
    offset: The offset of the first entity to be retrieved
    fmt: The format of the output (json, yaml, tsv, table)
    output: The path to the output file (stdout if not specified)

**Usage**:

```console
$ monarch search [OPTIONS]
```

**Options**:

* `-q, --query TEXT`
* `-c, --category TEXT`
* `-t, --in-taxon TEXT`
* `-ff, --facet-fields TEXT`
* `--facet-queries TEXT`
* `-l, --limit INTEGER`: [default: 20]
* `--offset INTEGER`: [default: 0]
* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-o, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

## `monarch solr`

**Usage**:

```console
$ monarch solr [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--quiet / --no-quiet`: [default: no-quiet]
* `--debug / --no-debug`: [default: no-debug]
* `--help`: Show this message and exit.

**Commands**:

* `association-counts`: Retrieve the association counts for a...
* `association-table`
* `associations`: Paginate through associations
* `autocomplete`: Return entity autcomplete matches for a...
* `download`: Download the Monarch Solr KG.
* `entity`: Retrieve an entity by ID
* `histopheno`: Retrieve the histopheno associations for a...
* `search`: Search for entities
* `start`: Starts a local Solr container.
* `status`: Checks the status of the local Solr...
* `stop`: Stops the local Solr container.

### `monarch solr association-counts`

Retrieve the association counts for a given entity

Args:
    entity (str): The entity to get association counts for

Optional Args:
    update (bool): Whether to re-download the Monarch KG. Default False
    fmt (str): The format of the output (json, yaml, tsv, table). Default JSON
    output (str): The path to the output file. Default stdout

**Usage**:

```console
$ monarch solr association-counts [OPTIONS] [ENTITY]
```

**Arguments**:

* `[ENTITY]`: The entity to get association counts for

**Options**:

* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-o, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

### `monarch solr association-table`

**Usage**:

```console
$ monarch solr association-table [OPTIONS] ENTITY CATEGORY
```

**Arguments**:

* `ENTITY`: The entity to get associations for  [required]
* `CATEGORY`: The association category to get associations for, ex. biolink:GeneToPhenotypicFeatureAssociation  [required]

**Options**:

* `-q, --query TEXT`
* `-l, --limit INTEGER`: [default: 5]
* `--offset INTEGER`: [default: 0]
* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-o, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

### `monarch solr associations`

Paginate through associations

Args:
    category: A comma-separated list of categories
    subject: A comma-separated list of subjects
    predicate: A comma-separated list of predicates
    object: A comma-separated list of objects
    entity: A comma-separated list of entities
    limit: The number of associations to return
    direct: Whether to exclude associations with subject/object as ancestors
    offset: The offset of the first association to be retrieved
    fmt: The format of the output (json, yaml, tsv, table)
    output: The path to the output file (stdout if not specified)

**Usage**:

```console
$ monarch solr associations [OPTIONS]
```

**Options**:

* `-c, --category TEXT`: Comma-separated list of categories
* `-s, --subject TEXT`: Comma-separated list of subjects
* `-p, --predicate TEXT`: Comma-separated list of predicates
* `-o, --object TEXT`: Comma-separated list of objects
* `-e, --entity TEXT`: Comma-separated list of entities
* `-d, --direct`: Whether to exclude associations with subject/object as ancestors
* `-l, --limit INTEGER`: The number of associations to return  [default: 20]
* `--offset INTEGER`: The offset of the first association to be retrieved  [default: 0]
* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-o, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

### `monarch solr autocomplete`

Return entity autcomplete matches for a query string

Args:
    q: The query string to autocomplete against
    fmt: The format of the output (json, yaml, tsv, table)
    output: The path to the output file (stdout if not specified)

**Usage**:

```console
$ monarch solr autocomplete [OPTIONS] [Q]
```

**Arguments**:

* `[Q]`: Query string to autocomplete against

**Options**:

* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-o, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

### `monarch solr download`

Download the Monarch Solr KG.

**Usage**:

```console
$ monarch solr download [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `monarch solr entity`

Retrieve an entity by ID

Args:
    id (str): The identifier of the entity to be retrieved

Optional Args:
    fmt (str): The format of the output (json, yaml, tsv, table). Default JSON
    output (str): The path to the output file. Default stdout

**Usage**:

```console
$ monarch solr entity [OPTIONS] [ID]
```

**Arguments**:

* `[ID]`: The identifier of the entity to be retrieved

**Options**:

* `-e, --extra`: Include extra fields in the output (association_counts and node_hierarchy)
* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-o, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

### `monarch solr histopheno`

Retrieve the histopheno associations for a given subject

Args:
    subject (str): The subject of the association

Optional Args:
    update (bool): Whether to re-download the Monarch KG. Default False
    fmt (str): The format of the output (json, yaml, tsv, table). Default JSON
    output (str): The path to the output file. Default stdout

**Usage**:

```console
$ monarch solr histopheno [OPTIONS] [SUBJECT]
```

**Arguments**:

* `[SUBJECT]`: The subject of the association

**Options**:

* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: JSON]
* `-o, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

### `monarch solr search`

Search for entities

Optional Args:
    q: The query string to search for
    category: The category of the entity
    taxon: The taxon of the entity
    facet_fields: The fields to facet on
    facet_queries: The queries to facet on
    limit: The number of entities to return
    offset: The offset of the first entity to be retrieved
    fmt (str): The format of the output (json, yaml, tsv, table). Default JSON
    output (str): The path to the output file. Default stdout

**Usage**:

```console
$ monarch solr search [OPTIONS]
```

**Options**:

* `-q, --query TEXT`
* `-c, --category TEXT`
* `-t, --in-taxon TEXT`
* `-ff, --facet-fields TEXT`
* `--facet-queries TEXT`
* `-l, --limit INTEGER`: [default: 20]
* `--offset INTEGER`: [default: 0]
* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-o, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

### `monarch solr start`

Starts a local Solr container.

**Usage**:

```console
$ monarch solr start [OPTIONS]
```

**Options**:

* `--update / --no-update`: [default: no-update]
* `--help`: Show this message and exit.

### `monarch solr status`

Checks the status of the local Solr container.

**Usage**:

```console
$ monarch solr status [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `monarch solr stop`

Stops the local Solr container.

**Usage**:

```console
$ monarch solr stop [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `monarch sql`

**Usage**:

```console
$ monarch sql [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--quiet / --no-quiet`: [default: no-quiet]
* `--debug / --no-debug`: [default: no-debug]
* `--help`: Show this message and exit.

**Commands**:

* `associations`: Paginate through associations
* `entity`: Retrieve an entity by ID

### `monarch sql associations`

Paginate through associations

Args:
    category: A comma-separated list of categories
    subject: A comma-separated list of subjects
    predicate: A comma-separated list of predicates
    object: A comma-separated list of objects
    entity: A comma-separated list of entities
    limit: The number of associations to return
    offset: The offset of the first association to be retrieved
    fmt: The format of the output (json, yaml, tsv, table)
    output: The path to the output file (stdout if not specified)

**Usage**:

```console
$ monarch sql associations [OPTIONS]
```

**Options**:

* `-c, --category TEXT`: Comma-separated list of categories
* `-s, --subject TEXT`: Comma-separated list of subjects
* `-p, --predicate TEXT`: Comma-separated list of predicates
* `-o, --object TEXT`: Comma-separated list of objects
* `-e, --entity TEXT`: Comma-separated list of entities
* `-d, --direct`: Whether to exclude associations with subject/object as ancestors
* `-l, --limit INTEGER`: The number of associations to return  [default: 20]
* `--offset INTEGER`: The offset of the first association to be retrieved  [default: 0]
* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-o, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

### `monarch sql entity`

Retrieve an entity by ID

Args:
    id (str): The identifier of the entity to be retrieved
    update (bool): = Whether to re-download the Monarch KG. Default False
    fmt (str): The format of the output (json, yaml, tsv, table). Default JSON
    output (str): The path to the output file. Default stdout

**Usage**:

```console
$ monarch sql entity [OPTIONS] [ID]
```

**Arguments**:

* `[ID]`: The identifier of the entity to be retrieved

**Options**:

* `-e, --extra`: Include extra fields in the output (association_counts and node_hierarchy)
* `-u, --update`: Whether to re-download the Monarch KG
* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-o, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

## `monarch test`

Test the CLI

**Usage**:

```console
$ monarch test [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.
