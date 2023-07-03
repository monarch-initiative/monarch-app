# Usage

monarch-py can be used via command line, or as a Python module.

## CLI

### Overview 

monarch-py can be used to query various implementations of the Monarch knowledge graph.  
The default, and more feature-rich, implementation is Solr, and is the default.

Subcommands are available to specify the backend.

For example:
```bash
# The following two commands are equivalent,
# as both query the Solr KG
$ monarch entity MONDO:0012933 
$ monarch solr entity MONDO:0012933

# Whereas the following specifies the SQL implementation
$ monarch sql entity MONDO:0012933
```

You can also use an environment variable to specify a Solr URL to query a different Solr instance.  
monarch-py checks for the `MONARCH_SOLR_URL` environment variable, and uses it if it exists.  
If not, it uses the default Solr URL of `http://localhost:8983/solr`.

### Commands

CLI commands are listed [here](./CLI.md), or can be found by running `monarch --help`.

## Module

TBD