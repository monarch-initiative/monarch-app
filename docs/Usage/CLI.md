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
* `compare`: Compare two sets of phenotypes using...
* `entity`: Retrieve an entity by ID
* `histopheno`: Retrieve the histopheno data for an entity...
* `mappings`
* `multi-entity-associations`: Paginate through associations for multiple...
* `release`: Retrieve metadata for a specific release
* `releases`: List all available releases of the Monarch...
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
* `-O, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

## `monarch association-table`

**Usage**:

```console
$ monarch association-table [OPTIONS] ENTITY CATEGORY:{biolink:PairwiseGeneToGeneInteraction|biolink:GeneToExpressionSiteAssociation|biolink:MacromolecularMachineToBiologicalProcessAssociation|biolink:GeneToPhenotypicFeatureAssociation|biolink:MacromolecularMachineToMolecularActivityAssociation|biolink:MacromolecularMachineToCellularComponentAssociation|biolink:Association|biolink:GeneToGeneHomologyAssociation|biolink:DiseaseToPhenotypicFeatureAssociation|biolink:GeneToPathwayAssociation|biolink:ChemicalToPathwayAssociation|biolink:CorrelatedGeneToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation|biolink:CausalGeneToDiseaseAssociation}
```

**Arguments**:

* `ENTITY`: The entity to get associations for  [required]
* `CATEGORY:{biolink:PairwiseGeneToGeneInteraction|biolink:GeneToExpressionSiteAssociation|biolink:MacromolecularMachineToBiologicalProcessAssociation|biolink:GeneToPhenotypicFeatureAssociation|biolink:MacromolecularMachineToMolecularActivityAssociation|biolink:MacromolecularMachineToCellularComponentAssociation|biolink:Association|biolink:GeneToGeneHomologyAssociation|biolink:DiseaseToPhenotypicFeatureAssociation|biolink:GeneToPathwayAssociation|biolink:ChemicalToPathwayAssociation|biolink:CorrelatedGeneToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation|biolink:CausalGeneToDiseaseAssociation}`: The association category to get associations for, ex. biolink:GeneToPhenotypicFeatureAssociation  [required]

**Options**:

* `-q, --query TEXT`
* `-t, --traverse-orthologs`: Whether to traverse orthologs when getting associations
* `-s, --sort TEXT`
* `-l, --limit INTEGER`: [default: 5]
* `--offset INTEGER`: [default: 0]
* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: The path to the output file
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

* `-c, --category [biolink:PairwiseGeneToGeneInteraction|biolink:GeneToExpressionSiteAssociation|biolink:MacromolecularMachineToBiologicalProcessAssociation|biolink:GeneToPhenotypicFeatureAssociation|biolink:MacromolecularMachineToMolecularActivityAssociation|biolink:MacromolecularMachineToCellularComponentAssociation|biolink:Association|biolink:GeneToGeneHomologyAssociation|biolink:DiseaseToPhenotypicFeatureAssociation|biolink:GeneToPathwayAssociation|biolink:ChemicalToPathwayAssociation|biolink:CorrelatedGeneToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation|biolink:CausalGeneToDiseaseAssociation]`: Category to get associations for
* `-s, --subject TEXT`: Subject ID to get associations for
* `-p, --predicate [biolink:interacts_with|biolink:expressed_in|biolink:has_phenotype|biolink:enables|biolink:actively_involved_in|biolink:orthologous_to|biolink:located_in|biolink:subclass_of|biolink:participates_in|biolink:acts_upstream_of_or_within|biolink:related_to|biolink:active_in|biolink:part_of|biolink:acts_upstream_of|biolink:has_mode_of_inheritance|biolink:gene_associated_with_condition|biolink:contributes_to|biolink:causes|biolink:colocalizes_with|biolink:acts_upstream_of_or_within_positive_effect|biolink:acts_upstream_of_positive_effect|biolink:acts_upstream_of_or_within_negative_effect|biolink:acts_upstream_of_negative_effect]`: Predicate ID to get associations for
* `-o, --object TEXT`: Object ID to get associations for
* `-e, --entity TEXT`: Entity (subject or object) ID to get associations for
* `-d, --direct`: Whether to exclude associations with subject/object as ancestors
* `-C, --compact`: Whether to return a compact representation of the associations
* `-l, --limit INTEGER`: The number of associations to return  [default: 20]
* `--offset INTEGER`: The offset of the first association to be retrieved  [default: 0]
* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: The path to the output file
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
* `-O, --output TEXT`: The path to the output file
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
* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: The path to the output file
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
* `-O, --output TEXT`: The path to the output file
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
* `-O, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

## `monarch mappings`

**Usage**:

```console
$ monarch mappings [OPTIONS]
```

**Options**:

* `-e, --entity-id TEXT`: entity ID to get mappings for
* `-s, --subject-id TEXT`: subject ID to get mappings for
* `-p, --predicate-id [skos:exactMatch|skos:closeMatch|skos:broadMatch|skos:narrowMatch]`: predicate ID to get mappings for
* `-o, --object-id TEXT`: object ID to get mappings for
* `-m, --mapping-justification TEXT`: mapping justification to get mappings for
* `--offset INTEGER`: The offset of the first mapping to be retrieved  [default: 0]
* `-l, --limit INTEGER`: The number of mappings to return  [default: 20]
* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

## `monarch multi-entity-associations`

Paginate through associations for multiple entities

Args:
    entity: A comma-separated list of entities
    counterpart_category: A comma-separated list of counterpart categories
    limit: The number of associations to return
    offset: The offset of the first association to be retrieved
    fmt: The format of the output (json, yaml, tsv, table)
    output: The path to the output file (stdout if not specified)

**Usage**:

```console
$ monarch multi-entity-associations [OPTIONS]
```

**Options**:

* `-e, --entity TEXT`: Comma-separated list of entities
* `-c, --counterpart-category TEXT`
* `-l, --limit INTEGER`: [default: 20]
* `--offset INTEGER`: [default: 0]
* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-o, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

## `monarch release`

Retrieve metadata for a specific release

Args:
    release_ver: The release version to get metadata for
    fmt: The format of the output (json, yaml, tsv, table)
    output: The path to the output file (stdout if not specified)

**Usage**:

```console
$ monarch release [OPTIONS] [RELEASE_VER]
```

**Arguments**:

* `[RELEASE_VER]`: The release version to get metadata for

**Options**:

* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

## `monarch releases`

List all available releases of the Monarch Knowledge Graph

**Usage**:

```console
$ monarch releases [OPTIONS]
```

**Options**:

* `--dev`: Get dev releases of the KG (default is False)
* `-l, --limit INTEGER`: The number of releases to return  [default: 0]
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
    in_taxon_label: The taxon label to filter by
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
* `-c, --category [biolink:Gene|biolink:PhenotypicFeature|biolink:BiologicalProcessOrActivity|biolink:GrossAnatomicalStructure|biolink:Disease|biolink:Pathway|biolink:Cell|biolink:NamedThing|biolink:AnatomicalEntity|biolink:CellularComponent|biolink:MolecularEntity|biolink:BiologicalProcess|biolink:MacromolecularComplex|biolink:MolecularActivity|biolink:Protein|biolink:CellularOrganism|biolink:PhenotypicQuality|biolink:Vertebrate|biolink:Virus|biolink:BehavioralFeature|biolink:LifeStage|biolink:PathologicalProcess|biolink:ChemicalEntity|biolink:Drug|biolink:OrganismTaxon|biolink:SequenceVariant|biolink:SmallMolecule|biolink:InformationContentEntity|biolink:NucleicAcidEntity|biolink:EvidenceType|biolink:GeographicExposure|biolink:RNAProduct|biolink:Transcript|biolink:Fungus|biolink:Plant|biolink:Dataset|biolink:Invertebrate|biolink:PopulationOfIndividualOrganisms|biolink:ProteinFamily|biolink:Activity|biolink:Agent|biolink:ChemicalExposure|biolink:ConfidenceLevel|biolink:EnvironmentalFeature|biolink:Exon|biolink:GeneticInheritance|biolink:Genome|biolink:Genotype|biolink:Haplotype|biolink:Human|biolink:IndividualOrganism|biolink:Mammal|biolink:MaterialSample|biolink:MicroRNA|biolink:Patent|biolink:ProteinDomain|biolink:Publication|biolink:RegulatoryRegion|biolink:Study|biolink:Treatment|biolink:WebPage|biolink:AccessibleDnaRegion|biolink:Article|biolink:Attribute|biolink:Bacterium|biolink:BiologicalEntity|biolink:BiologicalSex|biolink:CellLine|biolink:ChemicalMixture|biolink:CodingSequence|biolink:DatasetDistribution|biolink:DiagnosticAid|biolink:DrugExposure|biolink:EnvironmentalProcess|biolink:Event|biolink:GenotypicSex|biolink:NoncodingRNAProduct|biolink:OrganismalEntity|biolink:PhenotypicSex|biolink:Polypeptide|biolink:Procedure|biolink:ProcessedMaterial|biolink:ReagentTargetedGene|biolink:SiRNA|biolink:Snv|biolink:StudyVariable|biolink:TranscriptionFactorBindingSite|biolink:Zygosity]`
* `-t, --in-taxon-label TEXT`
* `-ff, --facet-fields TEXT`
* `--facet-queries TEXT`
* `-l, --limit INTEGER`: [default: 20]
* `--offset INTEGER`: [default: 0]
* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: The path to the output file
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
* `mappings`
* `multi-entity-associations`: Paginate through associations for multiple...
* `search`: Search for entities
* `start`: Starts a local Solr container.
* `status`: Checks the status of the local Solr...
* `stop`: Stops the local Solr container.

### `monarch solr association-counts`

Retrieve the association counts for a given entity

Args:
    entity (str): The entity to get association counts for

Optional Args:
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
* `-O, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

### `monarch solr association-table`

**Usage**:

```console
$ monarch solr association-table [OPTIONS] ENTITY [CATEGORY]:[biolink:PairwiseGeneToGeneInteraction|biolink:GeneToExpressionSiteAssociation|biolink:MacromolecularMachineToBiologicalProcessAssociation|biolink:GeneToPhenotypicFeatureAssociation|biolink:MacromolecularMachineToMolecularActivityAssociation|biolink:MacromolecularMachineToCellularComponentAssociation|biolink:Association|biolink:GeneToGeneHomologyAssociation|biolink:DiseaseToPhenotypicFeatureAssociation|biolink:GeneToPathwayAssociation|biolink:ChemicalToPathwayAssociation|biolink:CorrelatedGeneToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation|biolink:CausalGeneToDiseaseAssociation]
```

**Arguments**:

* `ENTITY`: The entity to get associations for  [required]
* `[CATEGORY]:[biolink:PairwiseGeneToGeneInteraction|biolink:GeneToExpressionSiteAssociation|biolink:MacromolecularMachineToBiologicalProcessAssociation|biolink:GeneToPhenotypicFeatureAssociation|biolink:MacromolecularMachineToMolecularActivityAssociation|biolink:MacromolecularMachineToCellularComponentAssociation|biolink:Association|biolink:GeneToGeneHomologyAssociation|biolink:DiseaseToPhenotypicFeatureAssociation|biolink:GeneToPathwayAssociation|biolink:ChemicalToPathwayAssociation|biolink:CorrelatedGeneToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation|biolink:CausalGeneToDiseaseAssociation]`: The association category to get associations for, ex. biolink:GeneToPhenotypicFeatureAssociation

**Options**:

* `-t, --traverse-orthologs`: Whether to traverse orthologs when getting associations
* `-q, --query TEXT`
* `-s, --sort TEXT`
* `-l, --limit INTEGER`: [default: 5]
* `--offset INTEGER`: [default: 0]
* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

### `monarch solr associations`

Paginate through associations

Args:
    category: The category of the association (multi-valued)
    subject: The subject of the association (multi-valued)
    predicate: The predicate of the association (multi-valued)
    object: The object of the association (multi-valued)
    entity: The entity (subject or object) of the association (multi-valued)
    limit: The number of associations to return (default 20)
    direct: Whether to exclude associations with subject/object as ancestors (default False)
    offset: The offset of the first association to be retrieved
    fmt: The format of the output (json, yaml, tsv, table) (default json)
    output: The path to the output file (stdout if not specified) (default None)

**Usage**:

```console
$ monarch solr associations [OPTIONS]
```

**Options**:

* `-c, --category [biolink:PairwiseGeneToGeneInteraction|biolink:GeneToExpressionSiteAssociation|biolink:MacromolecularMachineToBiologicalProcessAssociation|biolink:GeneToPhenotypicFeatureAssociation|biolink:MacromolecularMachineToMolecularActivityAssociation|biolink:MacromolecularMachineToCellularComponentAssociation|biolink:Association|biolink:GeneToGeneHomologyAssociation|biolink:DiseaseToPhenotypicFeatureAssociation|biolink:GeneToPathwayAssociation|biolink:ChemicalToPathwayAssociation|biolink:CorrelatedGeneToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation|biolink:CausalGeneToDiseaseAssociation]`: Category to get associations for
* `-s, --subject TEXT`: Subject ID to get associations for
* `-p, --predicate [biolink:interacts_with|biolink:expressed_in|biolink:has_phenotype|biolink:enables|biolink:actively_involved_in|biolink:orthologous_to|biolink:located_in|biolink:subclass_of|biolink:participates_in|biolink:acts_upstream_of_or_within|biolink:related_to|biolink:active_in|biolink:part_of|biolink:acts_upstream_of|biolink:has_mode_of_inheritance|biolink:gene_associated_with_condition|biolink:contributes_to|biolink:causes|biolink:colocalizes_with|biolink:acts_upstream_of_or_within_positive_effect|biolink:acts_upstream_of_positive_effect|biolink:acts_upstream_of_or_within_negative_effect|biolink:acts_upstream_of_negative_effect]`: Predicate ID to get associations for
* `-o, --object TEXT`: Object ID to get associations for
* `-e, --entity TEXT`: Entity (subject or object) ID to get associations for
* `-d, --direct`: Whether to exclude associations with subject/object as ancestors
* `-C, --compact`: Whether to return a compact representation of the associations
* `-l, --limit INTEGER`: The number of associations to return  [default: 20]
* `--offset INTEGER`: The offset of the first association to be retrieved  [default: 0]
* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: The path to the output file
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
* `-O, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

### `monarch solr download`

Download the Monarch Solr KG.

**Usage**:

```console
$ monarch solr download [OPTIONS]
```

**Options**:

* `--version TEXT`: [default: latest]
* `--overwrite / --no-overwrite`: [default: no-overwrite]
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
* `-O, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

### `monarch solr histopheno`

Retrieve the histopheno associations for a given subject

Args:
    subject (str): The subject of the association

Optional Args:
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
* `-O, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

### `monarch solr mappings`

**Usage**:

```console
$ monarch solr mappings [OPTIONS]
```

**Options**:

* `-e, --entity-id TEXT`: entity ID to get mappings for
* `-s, --subject-id TEXT`: subject ID to get mappings for
* `-p, --predicate-id [skos:exactMatch|skos:closeMatch|skos:broadMatch|skos:narrowMatch]`: predicate ID to get mappings for
* `-o, --object-id TEXT`: object ID to get mappings for
* `-m, --mapping-justification TEXT`: mapping justification to get mappings for
* `--offset INTEGER`: The offset of the first mapping to be retrieved  [default: 0]
* `-l, --limit INTEGER`: The number of mappings to return  [default: 20]
* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

### `monarch solr multi-entity-associations`

Paginate through associations for multiple entities

Args:
    entity: A comma-separated list of entities
    counterpart_category: A comma-separated list of counterpart categories
    limit: The number of associations to return
    offset: The offset of the first association to be retrieved
    fmt: The format of the output (json, yaml, tsv, table)
    output: The path to the output file (stdout if not specified)

**Usage**:

```console
$ monarch solr multi-entity-associations [OPTIONS]
```

**Options**:

* `-e, --entity TEXT`: Entity ID to get associations for
* `-c, --counterpart-category TEXT`: Counterpart category to get associations for
* `-l, --limit INTEGER`: [default: 20]
* `--offset INTEGER`: [default: 0]
* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: The path to the output file
* `--help`: Show this message and exit.

### `monarch solr search`

Search for entities

Optional Args:
    q: The query string to search for
    category: The category of the entity
    in_taxon_label: The taxon label to filter on
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

* `-q, --query TEXT`: [default: *:*]
* `-c, --category [biolink:Gene|biolink:PhenotypicFeature|biolink:BiologicalProcessOrActivity|biolink:GrossAnatomicalStructure|biolink:Disease|biolink:Pathway|biolink:Cell|biolink:NamedThing|biolink:AnatomicalEntity|biolink:CellularComponent|biolink:MolecularEntity|biolink:BiologicalProcess|biolink:MacromolecularComplex|biolink:MolecularActivity|biolink:Protein|biolink:CellularOrganism|biolink:PhenotypicQuality|biolink:Vertebrate|biolink:Virus|biolink:BehavioralFeature|biolink:LifeStage|biolink:PathologicalProcess|biolink:ChemicalEntity|biolink:Drug|biolink:OrganismTaxon|biolink:SequenceVariant|biolink:SmallMolecule|biolink:InformationContentEntity|biolink:NucleicAcidEntity|biolink:EvidenceType|biolink:GeographicExposure|biolink:RNAProduct|biolink:Transcript|biolink:Fungus|biolink:Plant|biolink:Dataset|biolink:Invertebrate|biolink:PopulationOfIndividualOrganisms|biolink:ProteinFamily|biolink:Activity|biolink:Agent|biolink:ChemicalExposure|biolink:ConfidenceLevel|biolink:EnvironmentalFeature|biolink:Exon|biolink:GeneticInheritance|biolink:Genome|biolink:Genotype|biolink:Haplotype|biolink:Human|biolink:IndividualOrganism|biolink:Mammal|biolink:MaterialSample|biolink:MicroRNA|biolink:Patent|biolink:ProteinDomain|biolink:Publication|biolink:RegulatoryRegion|biolink:Study|biolink:Treatment|biolink:WebPage|biolink:AccessibleDnaRegion|biolink:Article|biolink:Attribute|biolink:Bacterium|biolink:BiologicalEntity|biolink:BiologicalSex|biolink:CellLine|biolink:ChemicalMixture|biolink:CodingSequence|biolink:DatasetDistribution|biolink:DiagnosticAid|biolink:DrugExposure|biolink:EnvironmentalProcess|biolink:Event|biolink:GenotypicSex|biolink:NoncodingRNAProduct|biolink:OrganismalEntity|biolink:PhenotypicSex|biolink:Polypeptide|biolink:Procedure|biolink:ProcessedMaterial|biolink:ReagentTargetedGene|biolink:SiRNA|biolink:Snv|biolink:StudyVariable|biolink:TranscriptionFactorBindingSite|biolink:Zygosity]`
* `-t, --in-taxon-label TEXT`
* `-ff, --facet-fields TEXT`
* `--facet-queries TEXT`
* `-l, --limit INTEGER`: [default: 20]
* `--offset INTEGER`: [default: 0]
* `-f, --format TEXT`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: The path to the output file
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
    direct: Whether to exclude associations with subject/object as ancestors
    compact: Whether to return a compact representation of the associations
    limit: The number of associations to return
    offset: The offset of the first association to be retrieved
    fmt: The format of the output (json, yaml, tsv, table)
    output: The path to the output file (stdout if not specified)

**Usage**:

```console
$ monarch sql associations [OPTIONS]
```

**Options**:

* `-c, --category [biolink:PairwiseGeneToGeneInteraction|biolink:GeneToExpressionSiteAssociation|biolink:MacromolecularMachineToBiologicalProcessAssociation|biolink:GeneToPhenotypicFeatureAssociation|biolink:MacromolecularMachineToMolecularActivityAssociation|biolink:MacromolecularMachineToCellularComponentAssociation|biolink:Association|biolink:GeneToGeneHomologyAssociation|biolink:DiseaseToPhenotypicFeatureAssociation|biolink:GeneToPathwayAssociation|biolink:ChemicalToPathwayAssociation|biolink:CorrelatedGeneToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation|biolink:CausalGeneToDiseaseAssociation]`: Category to get associations for
* `-s, --subject TEXT`: Subject ID to get associations for
* `-p, --predicate [biolink:interacts_with|biolink:expressed_in|biolink:has_phenotype|biolink:enables|biolink:actively_involved_in|biolink:orthologous_to|biolink:located_in|biolink:subclass_of|biolink:participates_in|biolink:acts_upstream_of_or_within|biolink:related_to|biolink:active_in|biolink:part_of|biolink:acts_upstream_of|biolink:has_mode_of_inheritance|biolink:gene_associated_with_condition|biolink:contributes_to|biolink:causes|biolink:colocalizes_with|biolink:acts_upstream_of_or_within_positive_effect|biolink:acts_upstream_of_positive_effect|biolink:acts_upstream_of_or_within_negative_effect|biolink:acts_upstream_of_negative_effect]`: Predicate ID to get associations for
* `-o, --object TEXT`: Object ID to get associations for
* `-e, --entity TEXT`: Entity (subject or object) ID to get associations for
* `-d, --direct`: Whether to exclude associations with subject/object as ancestors
* `-C, --compact`: Whether to return a compact representation of the associations
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
