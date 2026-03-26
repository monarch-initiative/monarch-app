# `monarch`

**Usage**:

```console
$ monarch [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-v, --version`: Show the currently installed version
* `-q, --quiet`: Set log level to warning
* `-d, --debug`: Set log level to debug
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `test`: Test the CLI
* `schema`: Print the linkml schema for the data model
* `entity`: Retrieve an entity by ID
* `associations`: Paginate through associations
* `multi-entity-associations`: Paginate through associations for multiple...
* `search`: Search for entities
* `autocomplete`: Return entity autcomplete matches for a...
* `histopheno`: Retrieve the histopheno associations for a...
* `association-counts`: Retrieve the association counts for a...
* `association-table`
* `mappings`
* `compare`: Compare two sets of phenotypes using...
* `releases`: List all available releases of the Monarch...
* `release`: Retrieve metadata for a specific release
* `solr`
* `sql`

## `monarch test`

Test the CLI

**Usage**:

```console
$ monarch test [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `monarch schema`

Print the linkml schema for the data model

**Usage**:

```console
$ monarch schema [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `monarch entity`

Retrieve an entity by ID

**Usage**:

```console
$ monarch entity [OPTIONS] ENTITY_ID
```

**Arguments**:

* `ENTITY_ID`: The identifier of the entity to be retrieved  [required]

**Options**:

* `-e, --extra`: Include extra fields in the output (association_counts and node_hierarchy)
* `-f, --format [json|yaml|tsv|table]`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: Path to file to write command output (stdout if not specified)
* `--help`: Show this message and exit.

## `monarch associations`

Paginate through associations

**Usage**:

```console
$ monarch associations [OPTIONS]
```

**Options**:

* `-c, --category [biolink:PairwiseGeneToGeneInteraction|biolink:GeneToExpressionSiteAssociation|biolink:GeneToGeneHomologyAssociation|biolink:Association|biolink:MacromolecularMachineToBiologicalProcessAssociation|biolink:MacromolecularMachineToMolecularActivityAssociation|biolink:MacromolecularMachineToCellularComponentAssociation|biolink:GeneToPhenotypicFeatureAssociation|biolink:GenotypeToPhenotypicFeatureAssociation|biolink:VariantToPhenotypicFeatureAssociation|biolink:DiseaseToPhenotypicFeatureAssociation|biolink:GeneToPathwayAssociation|biolink:VariantToGeneAssociation|biolink:CaseToPhenotypicFeatureAssociation|biolink:GenotypeToGeneAssociation|biolink:GenotypeToVariantAssociation|biolink:ChemicalEntityToPathwayAssociation|biolink:VariantToDiseaseAssociation|biolink:ChemicalEntityToDiseaseOrPhenotypicFeatureAssociation|biolink:GenotypeToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation|biolink:CorrelatedGeneToDiseaseAssociation|biolink:CaseToDiseaseAssociation|biolink:CaseToGeneAssociation|biolink:CausalGeneToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToLocationAssociation|biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation]`: Category to get associations for
* `-s, --subject TEXT`: Subject ID to get associations for
* `-p, --predicate [biolink:interacts_with|biolink:expressed_in|biolink:has_phenotype|biolink:orthologous_to|biolink:enables|biolink:actively_involved_in|biolink:related_to|biolink:located_in|biolink:subclass_of|biolink:participates_in|biolink:acts_upstream_of_or_within|biolink:is_sequence_variant_of|biolink:is_active_in|biolink:has_sequence_variant|biolink:part_of|biolink:causes|biolink:treats_or_applied_or_studied_to_treat|biolink:homologous_to|biolink:contributes_to|biolink:model_of|biolink:has_mode_of_inheritance|biolink:has_disease|biolink:has_gene|biolink:gene_associated_with_condition|biolink:associated_with_increased_likelihood_of|biolink:colocalizes_with|biolink:same_as|biolink:acts_upstream_of|biolink:genetically_associated_with|biolink:disease_has_location|biolink:acts_upstream_of_or_within_positive_effect|biolink:ameliorates_condition|biolink:acts_upstream_of_positive_effect|biolink:acts_upstream_of_negative_effect|biolink:acts_upstream_of_or_within_negative_effect|biolink:has_participant|biolink:preventative_for_condition|biolink:disrupts|biolink:caused_by|biolink:contraindicated_in]`: Predicate ID to get associations for
* `-o, --object TEXT`: Object ID to get associations for
* `-e, --entity TEXT`: Entity (subject or object) ID to get associations for
* `-d, --direct`: Whether to exclude associations with subject/object as ancestors
* `-C, --compact`: Whether to return a compact representation of the associations
* `-l, --limit INTEGER`: The number of results to return  [default: 20]
* `--offset INTEGER`: The offset of the first result to be retrieved  [default: 0]
* `-f, --format [json|yaml|tsv|table]`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: Path to file to write command output (stdout if not specified)
* `--help`: Show this message and exit.

## `monarch multi-entity-associations`

Paginate through associations for multiple entities

**Usage**:

```console
$ monarch multi-entity-associations [OPTIONS]
```

**Options**:

* `-e, --entity TEXT`: Comma-separated list of entities
* `-c, --counterpart-category TEXT`: A comma-separated list of counterpart categories
* `-l, --limit INTEGER`: The number of results to return  [default: 20]
* `--offset INTEGER`: The offset of the first result to be retrieved  [default: 0]
* `-f, --format [json|yaml|tsv|table]`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: Path to file to write command output (stdout if not specified)
* `--help`: Show this message and exit.

## `monarch search`

Search for entities

**Usage**:

```console
$ monarch search [OPTIONS]
```

**Options**:

* `-q, --query TEXT`: [default: :*]
* `-c, --category [biolink:Gene|biolink:SequenceVariant|biolink:PhenotypicFeature|biolink:Genotype|biolink:AnatomicalEntity|biolink:NamedThing|biolink:BiologicalProcess|biolink:Disease|biolink:Protein|biolink:Pathway|biolink:ChemicalEntity|biolink:MolecularActivity|biolink:Case|biolink:CellularComponent|biolink:Cell|biolink:OrganismTaxon|biolink:MolecularEntity|biolink:LifeStage]`
* `-t, --in-taxon-label TEXT`
* `-ff, --facet-fields TEXT`
* `-fq, --facet-queries TEXT`
* `-l, --limit INTEGER`: The number of results to return  [default: 20]
* `--offset INTEGER`: The offset of the first result to be retrieved  [default: 0]
* `-f, --format [json|yaml|tsv|table]`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: Path to file to write command output (stdout if not specified)
* `--help`: Show this message and exit.

## `monarch autocomplete`

Return entity autcomplete matches for a query string

**Usage**:

```console
$ monarch autocomplete [OPTIONS] Q
```

**Arguments**:

* `Q`: Query string to autocomplete against  [required]

**Options**:

* `-f, --format [json|yaml|tsv|table]`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: Path to file to write command output (stdout if not specified)
* `--help`: Show this message and exit.

## `monarch histopheno`

Retrieve the histopheno associations for a given subject

**Usage**:

```console
$ monarch histopheno [OPTIONS] SUBJECT
```

**Arguments**:

* `SUBJECT`: The subject of the association  [required]

**Options**:

* `-f, --format [json|yaml|tsv|table]`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: Path to file to write command output (stdout if not specified)
* `--help`: Show this message and exit.

## `monarch association-counts`

Retrieve the association counts for a given entity

**Usage**:

```console
$ monarch association-counts [OPTIONS] ENTITY_ID
```

**Arguments**:

* `ENTITY_ID`: The entity to get association counts for  [required]

**Options**:

* `-f, --format [json|yaml|tsv|table]`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: Path to file to write command output (stdout if not specified)
* `--help`: Show this message and exit.

## `monarch association-table`

**Usage**:

```console
$ monarch association-table [OPTIONS] ENTITY_ID CATEGORY:{biolink:PairwiseGeneToGeneInteraction|biolink:GeneToExpressionSiteAssociation|biolink:GeneToGeneHomologyAssociation|biolink:Association|biolink:MacromolecularMachineToBiologicalProcessAssociation|biolink:MacromolecularMachineToMolecularActivityAssociation|biolink:MacromolecularMachineToCellularComponentAssociation|biolink:GeneToPhenotypicFeatureAssociation|biolink:GenotypeToPhenotypicFeatureAssociation|biolink:VariantToPhenotypicFeatureAssociation|biolink:DiseaseToPhenotypicFeatureAssociation|biolink:GeneToPathwayAssociation|biolink:VariantToGeneAssociation|biolink:CaseToPhenotypicFeatureAssociation|biolink:GenotypeToGeneAssociation|biolink:GenotypeToVariantAssociation|biolink:ChemicalEntityToPathwayAssociation|biolink:VariantToDiseaseAssociation|biolink:ChemicalEntityToDiseaseOrPhenotypicFeatureAssociation|biolink:GenotypeToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation|biolink:CorrelatedGeneToDiseaseAssociation|biolink:CaseToDiseaseAssociation|biolink:CaseToGeneAssociation|biolink:CausalGeneToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToLocationAssociation|biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation}
```

**Arguments**:

* `ENTITY_ID`: The entity to get associations for  [required]
* `CATEGORY:{biolink:PairwiseGeneToGeneInteraction|biolink:GeneToExpressionSiteAssociation|biolink:GeneToGeneHomologyAssociation|biolink:Association|biolink:MacromolecularMachineToBiologicalProcessAssociation|biolink:MacromolecularMachineToMolecularActivityAssociation|biolink:MacromolecularMachineToCellularComponentAssociation|biolink:GeneToPhenotypicFeatureAssociation|biolink:GenotypeToPhenotypicFeatureAssociation|biolink:VariantToPhenotypicFeatureAssociation|biolink:DiseaseToPhenotypicFeatureAssociation|biolink:GeneToPathwayAssociation|biolink:VariantToGeneAssociation|biolink:CaseToPhenotypicFeatureAssociation|biolink:GenotypeToGeneAssociation|biolink:GenotypeToVariantAssociation|biolink:ChemicalEntityToPathwayAssociation|biolink:VariantToDiseaseAssociation|biolink:ChemicalEntityToDiseaseOrPhenotypicFeatureAssociation|biolink:GenotypeToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation|biolink:CorrelatedGeneToDiseaseAssociation|biolink:CaseToDiseaseAssociation|biolink:CaseToGeneAssociation|biolink:CausalGeneToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToLocationAssociation|biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation}`: The association category to get associations for, ex. biolink:GeneToPhenotypicFeatureAssociation  [required]

**Options**:

* `-q, --query TEXT`
* `-t, --traverse-orthologs`: Whether to traverse orthologs when getting associations
* `-s, --sort TEXT`
* `-l, --limit INTEGER`: The number of results to return  [default: 20]
* `--offset INTEGER`: The offset of the first result to be retrieved  [default: 0]
* `-f, --format [json|yaml|tsv|table]`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: Path to file to write command output (stdout if not specified)
* `--help`: Show this message and exit.

## `monarch mappings`

**Usage**:

```console
$ monarch mappings [OPTIONS]
```

**Options**:

* `-e, --entity-id TEXT`: entity ID to get mappings for
* `-s, --subject-id TEXT`: subject ID to get mappings for
* `-p, --predicate-id [skos:exactMatch|skos:closeMatch|skos:broadMatch]`: predicate ID to get mappings for
* `-o, --object-id TEXT`: object ID to get mappings for
* `-m, --mapping-justification TEXT`: mapping justification to get mappings for
* `-l, --limit INTEGER`: The number of results to return  [default: 20]
* `--offset INTEGER`: The offset of the first result to be retrieved  [default: 0]
* `-f, --format [json|yaml|tsv|table]`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: Path to file to write command output (stdout if not specified)
* `--help`: Show this message and exit.

## `monarch compare`

Compare two sets of phenotypes using semantic similarity via SemSimian

**Usage**:

```console
$ monarch compare [OPTIONS] SUBJECTS OBJECTS
```

**Arguments**:

* `SUBJECTS`: Comma separated list of subjects to compare  [required]
* `OBJECTS`: Comma separated list of objects to compare  [required]

**Options**:

* `-m, --metric [ancestor_information_content|jaccard_similarity|phenodigm_score]`: The metric to use for comparison  [default: ancestor_information_content]
* `-f, --format [json|yaml|tsv|table]`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: Path to file to write command output (stdout if not specified)
* `--help`: Show this message and exit.

## `monarch releases`

List all available releases of the Monarch Knowledge Graph

**Usage**:

```console
$ monarch releases [OPTIONS]
```

**Options**:

* `--dev`: Get dev releases of the KG (default is False)
* `-l, --limit INTEGER`: The number of results to return  [default: 0]
* `--help`: Show this message and exit.

## `monarch release`

Retrieve metadata for a specific release

**Usage**:

```console
$ monarch release [OPTIONS] RELEASE_VER
```

**Arguments**:

* `RELEASE_VER`: The release version to get metadata for  [required]

**Options**:

* `-f, --format [json|yaml|tsv|table]`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: Path to file to write command output (stdout if not specified)
* `--help`: Show this message and exit.

## `monarch solr`

**Usage**:

```console
$ monarch solr [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-q, --quiet`: Set log level to warning
* `-d, --debug`: Set log level to debug
* `--help`: Show this message and exit.

**Commands**:

* `start`: Starts a local Solr container.
* `stop`: Stops the local Solr container.
* `status`: Checks the status of the local Solr...
* `download`: Download the Monarch Solr KG.
* `entity`: Retrieve an entity by ID
* `associations`: Paginate through associations
* `multi-entity-associations`: Paginate through associations for multiple...
* `search`: Search for entities
* `autocomplete`: Return entity autcomplete matches for a...
* `histopheno`: Retrieve the histopheno associations for a...
* `association-counts`: Retrieve the association counts for a...
* `association-table`
* `mappings`

### `monarch solr start`

Starts a local Solr container.

**Usage**:

```console
$ monarch solr start [OPTIONS]
```

**Options**:

* `--update / --no-update`: [default: no-update]
* `--help`: Show this message and exit.

### `monarch solr stop`

Stops the local Solr container.

**Usage**:

```console
$ monarch solr stop [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `monarch solr status`

Checks the status of the local Solr container.

**Usage**:

```console
$ monarch solr status [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `monarch solr download`

Download the Monarch Solr KG.

**Usage**:

```console
$ monarch solr download [OPTIONS] [VERSION]
```

**Arguments**:

* `[VERSION]`: The version of the Solr KG to download (latest, dev, or a specific version)  [default: latest]

**Options**:

* `--overwrite`: Overwrite the existing Solr KG if it exists
* `--help`: Show this message and exit.

### `monarch solr entity`

Retrieve an entity by ID

**Usage**:

```console
$ monarch solr entity [OPTIONS] ENTITY_ID
```

**Arguments**:

* `ENTITY_ID`: The identifier of the entity to be retrieved  [required]

**Options**:

* `-e, --extra`: Include extra fields in the output (association_counts and node_hierarchy)
* `-f, --format [json|yaml|tsv|table]`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: Path to file to write command output (stdout if not specified)
* `--help`: Show this message and exit.

### `monarch solr associations`

Paginate through associations

**Usage**:

```console
$ monarch solr associations [OPTIONS]
```

**Options**:

* `-c, --category [biolink:PairwiseGeneToGeneInteraction|biolink:GeneToExpressionSiteAssociation|biolink:GeneToGeneHomologyAssociation|biolink:Association|biolink:MacromolecularMachineToBiologicalProcessAssociation|biolink:MacromolecularMachineToMolecularActivityAssociation|biolink:MacromolecularMachineToCellularComponentAssociation|biolink:GeneToPhenotypicFeatureAssociation|biolink:GenotypeToPhenotypicFeatureAssociation|biolink:VariantToPhenotypicFeatureAssociation|biolink:DiseaseToPhenotypicFeatureAssociation|biolink:GeneToPathwayAssociation|biolink:VariantToGeneAssociation|biolink:CaseToPhenotypicFeatureAssociation|biolink:GenotypeToGeneAssociation|biolink:GenotypeToVariantAssociation|biolink:ChemicalEntityToPathwayAssociation|biolink:VariantToDiseaseAssociation|biolink:ChemicalEntityToDiseaseOrPhenotypicFeatureAssociation|biolink:GenotypeToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation|biolink:CorrelatedGeneToDiseaseAssociation|biolink:CaseToDiseaseAssociation|biolink:CaseToGeneAssociation|biolink:CausalGeneToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToLocationAssociation|biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation]`: Category to get associations for
* `-s, --subject TEXT`: Subject ID to get associations for
* `-p, --predicate [biolink:interacts_with|biolink:expressed_in|biolink:has_phenotype|biolink:orthologous_to|biolink:enables|biolink:actively_involved_in|biolink:related_to|biolink:located_in|biolink:subclass_of|biolink:participates_in|biolink:acts_upstream_of_or_within|biolink:is_sequence_variant_of|biolink:is_active_in|biolink:has_sequence_variant|biolink:part_of|biolink:causes|biolink:treats_or_applied_or_studied_to_treat|biolink:homologous_to|biolink:contributes_to|biolink:model_of|biolink:has_mode_of_inheritance|biolink:has_disease|biolink:has_gene|biolink:gene_associated_with_condition|biolink:associated_with_increased_likelihood_of|biolink:colocalizes_with|biolink:same_as|biolink:acts_upstream_of|biolink:genetically_associated_with|biolink:disease_has_location|biolink:acts_upstream_of_or_within_positive_effect|biolink:ameliorates_condition|biolink:acts_upstream_of_positive_effect|biolink:acts_upstream_of_negative_effect|biolink:acts_upstream_of_or_within_negative_effect|biolink:has_participant|biolink:preventative_for_condition|biolink:disrupts|biolink:caused_by|biolink:contraindicated_in]`: Predicate ID to get associations for
* `-o, --object TEXT`: Object ID to get associations for
* `-e, --entity TEXT`: Entity (subject or object) ID to get associations for
* `-d, --direct`: Whether to exclude associations with subject/object as ancestors
* `-C, --compact`: Whether to return a compact representation of the associations
* `-l, --limit INTEGER`: The number of results to return  [default: 20]
* `--offset INTEGER`: The offset of the first result to be retrieved  [default: 0]
* `-f, --format [json|yaml|tsv|table]`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: Path to file to write command output (stdout if not specified)
* `--help`: Show this message and exit.

### `monarch solr multi-entity-associations`

Paginate through associations for multiple entities

**Usage**:

```console
$ monarch solr multi-entity-associations [OPTIONS]
```

**Options**:

* `-e, --entity TEXT`: Comma-separated list of entities
* `-c, --counterpart-category TEXT`: A comma-separated list of counterpart categories
* `-l, --limit INTEGER`: The number of results to return  [default: 20]
* `--offset INTEGER`: The offset of the first result to be retrieved  [default: 0]
* `-f, --format [json|yaml|tsv|table]`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: Path to file to write command output (stdout if not specified)
* `--help`: Show this message and exit.

### `monarch solr search`

Search for entities

**Usage**:

```console
$ monarch solr search [OPTIONS]
```

**Options**:

* `-q, --query TEXT`: [default: :*]
* `-c, --category [biolink:Gene|biolink:SequenceVariant|biolink:PhenotypicFeature|biolink:Genotype|biolink:AnatomicalEntity|biolink:NamedThing|biolink:BiologicalProcess|biolink:Disease|biolink:Protein|biolink:Pathway|biolink:ChemicalEntity|biolink:MolecularActivity|biolink:Case|biolink:CellularComponent|biolink:Cell|biolink:OrganismTaxon|biolink:MolecularEntity|biolink:LifeStage]`
* `-t, --in-taxon-label TEXT`
* `-ff, --facet-fields TEXT`
* `-fq, --facet-queries TEXT`
* `-l, --limit INTEGER`: The number of results to return  [default: 20]
* `--offset INTEGER`: The offset of the first result to be retrieved  [default: 0]
* `-f, --format [json|yaml|tsv|table]`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: Path to file to write command output (stdout if not specified)
* `--help`: Show this message and exit.

### `monarch solr autocomplete`

Return entity autcomplete matches for a query string

**Usage**:

```console
$ monarch solr autocomplete [OPTIONS] Q
```

**Arguments**:

* `Q`: Query string to autocomplete against  [required]

**Options**:

* `-f, --format [json|yaml|tsv|table]`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: Path to file to write command output (stdout if not specified)
* `--help`: Show this message and exit.

### `monarch solr histopheno`

Retrieve the histopheno associations for a given subject

**Usage**:

```console
$ monarch solr histopheno [OPTIONS] SUBJECT
```

**Arguments**:

* `SUBJECT`: The subject of the association  [required]

**Options**:

* `-f, --format [json|yaml|tsv|table]`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: Path to file to write command output (stdout if not specified)
* `--help`: Show this message and exit.

### `monarch solr association-counts`

Retrieve the association counts for a given entity

**Usage**:

```console
$ monarch solr association-counts [OPTIONS] ENTITY_ID
```

**Arguments**:

* `ENTITY_ID`: The entity to get association counts for  [required]

**Options**:

* `-f, --format [json|yaml|tsv|table]`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: Path to file to write command output (stdout if not specified)
* `--help`: Show this message and exit.

### `monarch solr association-table`

**Usage**:

```console
$ monarch solr association-table [OPTIONS] ENTITY_ID CATEGORY:{biolink:PairwiseGeneToGeneInteraction|biolink:GeneToExpressionSiteAssociation|biolink:GeneToGeneHomologyAssociation|biolink:Association|biolink:MacromolecularMachineToBiologicalProcessAssociation|biolink:MacromolecularMachineToMolecularActivityAssociation|biolink:MacromolecularMachineToCellularComponentAssociation|biolink:GeneToPhenotypicFeatureAssociation|biolink:GenotypeToPhenotypicFeatureAssociation|biolink:VariantToPhenotypicFeatureAssociation|biolink:DiseaseToPhenotypicFeatureAssociation|biolink:GeneToPathwayAssociation|biolink:VariantToGeneAssociation|biolink:CaseToPhenotypicFeatureAssociation|biolink:GenotypeToGeneAssociation|biolink:GenotypeToVariantAssociation|biolink:ChemicalEntityToPathwayAssociation|biolink:VariantToDiseaseAssociation|biolink:ChemicalEntityToDiseaseOrPhenotypicFeatureAssociation|biolink:GenotypeToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation|biolink:CorrelatedGeneToDiseaseAssociation|biolink:CaseToDiseaseAssociation|biolink:CaseToGeneAssociation|biolink:CausalGeneToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToLocationAssociation|biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation}
```

**Arguments**:

* `ENTITY_ID`: The entity to get associations for  [required]
* `CATEGORY:{biolink:PairwiseGeneToGeneInteraction|biolink:GeneToExpressionSiteAssociation|biolink:GeneToGeneHomologyAssociation|biolink:Association|biolink:MacromolecularMachineToBiologicalProcessAssociation|biolink:MacromolecularMachineToMolecularActivityAssociation|biolink:MacromolecularMachineToCellularComponentAssociation|biolink:GeneToPhenotypicFeatureAssociation|biolink:GenotypeToPhenotypicFeatureAssociation|biolink:VariantToPhenotypicFeatureAssociation|biolink:DiseaseToPhenotypicFeatureAssociation|biolink:GeneToPathwayAssociation|biolink:VariantToGeneAssociation|biolink:CaseToPhenotypicFeatureAssociation|biolink:GenotypeToGeneAssociation|biolink:GenotypeToVariantAssociation|biolink:ChemicalEntityToPathwayAssociation|biolink:VariantToDiseaseAssociation|biolink:ChemicalEntityToDiseaseOrPhenotypicFeatureAssociation|biolink:GenotypeToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation|biolink:CorrelatedGeneToDiseaseAssociation|biolink:CaseToDiseaseAssociation|biolink:CaseToGeneAssociation|biolink:CausalGeneToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToLocationAssociation|biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation}`: The association category to get associations for, ex. biolink:GeneToPhenotypicFeatureAssociation  [required]

**Options**:

* `-q, --query TEXT`
* `-t, --traverse-orthologs`: Whether to traverse orthologs when getting associations
* `-s, --sort TEXT`
* `-l, --limit INTEGER`: The number of results to return  [default: 20]
* `--offset INTEGER`: The offset of the first result to be retrieved  [default: 0]
* `-f, --format [json|yaml|tsv|table]`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: Path to file to write command output (stdout if not specified)
* `--help`: Show this message and exit.

### `monarch solr mappings`

**Usage**:

```console
$ monarch solr mappings [OPTIONS]
```

**Options**:

* `-e, --entity-id TEXT`: entity ID to get mappings for
* `-s, --subject-id TEXT`: subject ID to get mappings for
* `-p, --predicate-id [skos:exactMatch|skos:closeMatch|skos:broadMatch]`: predicate ID to get mappings for
* `-o, --object-id TEXT`: object ID to get mappings for
* `-m, --mapping-justification TEXT`: mapping justification to get mappings for
* `-l, --limit INTEGER`: The number of results to return  [default: 20]
* `--offset INTEGER`: The offset of the first result to be retrieved  [default: 0]
* `-f, --format [json|yaml|tsv|table]`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: Path to file to write command output (stdout if not specified)
* `--help`: Show this message and exit.

## `monarch sql`

**Usage**:

```console
$ monarch sql [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-q, --quiet`: Set log level to warning
* `-d, --debug`: Set log level to debug
* `--help`: Show this message and exit.

**Commands**:

* `entity`: Retrieve an entity by ID
* `associations`: Paginate through associations

### `monarch sql entity`

Retrieve an entity by ID

**Usage**:

```console
$ monarch sql entity [OPTIONS] ENTITY_ID
```

**Arguments**:

* `ENTITY_ID`: The identifier of the entity to be retrieved  [required]

**Options**:

* `-e, --extra`: Include extra fields in the output (association_counts and node_hierarchy)  [required]
* `-u, --update`: Whether to re-download the Monarch KG  [required]
* `-f, --format [json|yaml|tsv|table]`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: Path to file to write command output (stdout if not specified)
* `--help`: Show this message and exit.

### `monarch sql associations`

Paginate through associations

**Usage**:

```console
$ monarch sql associations [OPTIONS]
```

**Options**:

* `-c, --category [biolink:PairwiseGeneToGeneInteraction|biolink:GeneToExpressionSiteAssociation|biolink:GeneToGeneHomologyAssociation|biolink:Association|biolink:MacromolecularMachineToBiologicalProcessAssociation|biolink:MacromolecularMachineToMolecularActivityAssociation|biolink:MacromolecularMachineToCellularComponentAssociation|biolink:GeneToPhenotypicFeatureAssociation|biolink:GenotypeToPhenotypicFeatureAssociation|biolink:VariantToPhenotypicFeatureAssociation|biolink:DiseaseToPhenotypicFeatureAssociation|biolink:GeneToPathwayAssociation|biolink:VariantToGeneAssociation|biolink:CaseToPhenotypicFeatureAssociation|biolink:GenotypeToGeneAssociation|biolink:GenotypeToVariantAssociation|biolink:ChemicalEntityToPathwayAssociation|biolink:VariantToDiseaseAssociation|biolink:ChemicalEntityToDiseaseOrPhenotypicFeatureAssociation|biolink:GenotypeToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation|biolink:CorrelatedGeneToDiseaseAssociation|biolink:CaseToDiseaseAssociation|biolink:CaseToGeneAssociation|biolink:CausalGeneToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToLocationAssociation|biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation]`: Category to get associations for
* `-s, --subject TEXT`: Subject ID to get associations for
* `-p, --predicate [biolink:interacts_with|biolink:expressed_in|biolink:has_phenotype|biolink:orthologous_to|biolink:enables|biolink:actively_involved_in|biolink:related_to|biolink:located_in|biolink:subclass_of|biolink:participates_in|biolink:acts_upstream_of_or_within|biolink:is_sequence_variant_of|biolink:is_active_in|biolink:has_sequence_variant|biolink:part_of|biolink:causes|biolink:treats_or_applied_or_studied_to_treat|biolink:homologous_to|biolink:contributes_to|biolink:model_of|biolink:has_mode_of_inheritance|biolink:has_disease|biolink:has_gene|biolink:gene_associated_with_condition|biolink:associated_with_increased_likelihood_of|biolink:colocalizes_with|biolink:same_as|biolink:acts_upstream_of|biolink:genetically_associated_with|biolink:disease_has_location|biolink:acts_upstream_of_or_within_positive_effect|biolink:ameliorates_condition|biolink:acts_upstream_of_positive_effect|biolink:acts_upstream_of_negative_effect|biolink:acts_upstream_of_or_within_negative_effect|biolink:has_participant|biolink:preventative_for_condition|biolink:disrupts|biolink:caused_by|biolink:contraindicated_in]`: Predicate ID to get associations for
* `-o, --object TEXT`: Object ID to get associations for
* `-e, --entity TEXT`: Entity (subject or object) ID to get associations for
* `-d, --direct`: Whether to exclude associations with subject/object as ancestors
* `-C, --compact`: Whether to return a compact representation of the associations
* `-l, --limit INTEGER`: The number of results to return  [default: 20]
* `--offset INTEGER`: The offset of the first result to be retrieved  [default: 0]
* `-f, --format [json|yaml|tsv|table]`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: Path to file to write command output (stdout if not specified)
* `--help`: Show this message and exit.
