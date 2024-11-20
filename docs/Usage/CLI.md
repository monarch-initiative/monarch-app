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

* `association-counts`: Retrieve the association counts for a...
* `association-table`
* `associations`: Paginate through associations
* `autocomplete`: Return entity autcomplete matches for a...
* `compare`: Compare two sets of phenotypes using...
* `entity`: Retrieve an entity by ID
* `histopheno`: Retrieve the histopheno associations for a...
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
$ monarch association-table [OPTIONS] ENTITY_ID CATEGORY:{biolink:PairwiseGeneToGeneInteraction|biolink:GeneToExpressionSiteAssociation|biolink:VariantToGeneAssociation|biolink:MacromolecularMachineToBiologicalProcessAssociation|biolink:GeneToPhenotypicFeatureAssociation|biolink:MacromolecularMachineToMolecularActivityAssociation|biolink:MacromolecularMachineToCellularComponentAssociation|biolink:Association|biolink:GeneToGeneHomologyAssociation|biolink:GenotypeToPhenotypicFeatureAssociation|biolink:DiseaseToPhenotypicFeatureAssociation|biolink:GeneToPathwayAssociation|biolink:DiseaseOrPhenotypicFeatureToLocationAssociation|biolink:ChemicalToPathwayAssociation|biolink:GenotypeToDiseaseAssociation|biolink:CorrelatedGeneToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation|biolink:VariantToDiseaseAssociation|biolink:CausalGeneToDiseaseAssociation|biolink:ChemicalToDiseaseOrPhenotypicFeatureAssociation}
```

**Arguments**:

* `ENTITY_ID`: The entity to get associations for  [required]
* `CATEGORY:{biolink:PairwiseGeneToGeneInteraction|biolink:GeneToExpressionSiteAssociation|biolink:VariantToGeneAssociation|biolink:MacromolecularMachineToBiologicalProcessAssociation|biolink:GeneToPhenotypicFeatureAssociation|biolink:MacromolecularMachineToMolecularActivityAssociation|biolink:MacromolecularMachineToCellularComponentAssociation|biolink:Association|biolink:GeneToGeneHomologyAssociation|biolink:GenotypeToPhenotypicFeatureAssociation|biolink:DiseaseToPhenotypicFeatureAssociation|biolink:GeneToPathwayAssociation|biolink:DiseaseOrPhenotypicFeatureToLocationAssociation|biolink:ChemicalToPathwayAssociation|biolink:GenotypeToDiseaseAssociation|biolink:CorrelatedGeneToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation|biolink:VariantToDiseaseAssociation|biolink:CausalGeneToDiseaseAssociation|biolink:ChemicalToDiseaseOrPhenotypicFeatureAssociation}`: The association category to get associations for, ex. biolink:GeneToPhenotypicFeatureAssociation  [required]

**Options**:

* `-q, --query TEXT`
* `-t, --traverse-orthologs`: Whether to traverse orthologs when getting associations
* `-s, --sort TEXT`
* `-l, --limit INTEGER`: The number of results to return  [default: 20]
* `--offset INTEGER`: The offset of the first result to be retrieved  [default: 0]
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

* `-c, --category [biolink:PairwiseGeneToGeneInteraction|biolink:GeneToExpressionSiteAssociation|biolink:VariantToGeneAssociation|biolink:MacromolecularMachineToBiologicalProcessAssociation|biolink:GeneToPhenotypicFeatureAssociation|biolink:MacromolecularMachineToMolecularActivityAssociation|biolink:MacromolecularMachineToCellularComponentAssociation|biolink:Association|biolink:GeneToGeneHomologyAssociation|biolink:GenotypeToPhenotypicFeatureAssociation|biolink:DiseaseToPhenotypicFeatureAssociation|biolink:GeneToPathwayAssociation|biolink:DiseaseOrPhenotypicFeatureToLocationAssociation|biolink:ChemicalToPathwayAssociation|biolink:GenotypeToDiseaseAssociation|biolink:CorrelatedGeneToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation|biolink:VariantToDiseaseAssociation|biolink:CausalGeneToDiseaseAssociation|biolink:ChemicalToDiseaseOrPhenotypicFeatureAssociation]`: Category to get associations for
* `-s, --subject TEXT`: Subject ID to get associations for
* `-p, --predicate [biolink:interacts_with|biolink:expressed_in|biolink:has_phenotype|biolink:is_sequence_variant_of|biolink:enables|biolink:actively_involved_in|biolink:orthologous_to|biolink:located_in|biolink:subclass_of|biolink:related_to|biolink:participates_in|biolink:acts_upstream_of_or_within|biolink:active_in|biolink:part_of|biolink:model_of|biolink:causes|biolink:acts_upstream_of|biolink:has_mode_of_inheritance|biolink:contributes_to|biolink:gene_associated_with_condition|biolink:treats_or_applied_or_studied_to_treat|biolink:colocalizes_with|biolink:acts_upstream_of_positive_effect|biolink:acts_upstream_of_or_within_positive_effect|biolink:acts_upstream_of_negative_effect|biolink:acts_upstream_of_or_within_negative_effect]`: Predicate ID to get associations for
* `-o, --object TEXT`: Object ID to get associations for
* `-e, --entity TEXT`: Entity (subject or object) ID to get associations for
* `-d, --direct`: Whether to exclude associations with subject/object as ancestors
* `-C, --compact`: Whether to return a compact representation of the associations
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

## `monarch mappings`

**Usage**:

```console
$ monarch mappings [OPTIONS]
```

**Options**:

* `-e, --entity-id TEXT`: entity ID to get mappings for
* `-s, --subject-id TEXT`: subject ID to get mappings for
* `-p, --predicate-id [skos:exactMatch|skos:broadMatch]`: predicate ID to get mappings for
* `-o, --object-id TEXT`: object ID to get mappings for
* `-m, --mapping-justification TEXT`: mapping justification to get mappings for
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

**Usage**:

```console
$ monarch search [OPTIONS]
```

**Options**:

* `-q, --query TEXT`: [default: :*]
* `-c, --category [biolink:SequenceVariant|biolink:Gene|biolink:Genotype|biolink:PhenotypicFeature|biolink:BiologicalProcessOrActivity|biolink:Disease|biolink:GrossAnatomicalStructure|biolink:Cell|biolink:Pathway|biolink:NamedThing|biolink:AnatomicalEntity|biolink:CellularComponent|biolink:MolecularEntity|biolink:BiologicalProcess|biolink:MacromolecularComplex|biolink:MolecularActivity|biolink:Protein|biolink:CellularOrganism|biolink:Vertebrate|biolink:Virus|biolink:BehavioralFeature|biolink:ChemicalEntity|biolink:LifeStage|biolink:PathologicalProcess|biolink:Drug|biolink:SmallMolecule|biolink:OrganismTaxon|biolink:InformationContentEntity|biolink:NucleicAcidEntity|biolink:EvidenceType|biolink:RNAProduct|biolink:Transcript|biolink:Fungus|biolink:Plant|biolink:ProcessedMaterial|biolink:Activity|biolink:Agent|biolink:ConfidenceLevel|biolink:Dataset|biolink:EnvironmentalFeature|biolink:GeneticInheritance|biolink:Haplotype|biolink:Invertebrate|biolink:Mammal|biolink:PopulationOfIndividualOrganisms|biolink:ProteinFamily|biolink:Publication|biolink:AccessibleDnaRegion|biolink:Bacterium|biolink:BiologicalSex|biolink:CellLine|biolink:ChemicalExposure|biolink:ChemicalMixture|biolink:DatasetDistribution|biolink:DiagnosticAid|biolink:DrugExposure|biolink:EnvironmentalProcess|biolink:Event|biolink:Exon|biolink:Genome|biolink:GenotypicSex|biolink:Human|biolink:IndividualOrganism|biolink:MaterialSample|biolink:MicroRNA|biolink:OrganismalEntity|biolink:Patent|biolink:PhenotypicSex|biolink:Polypeptide|biolink:ProteinDomain|biolink:ReagentTargetedGene|biolink:RegulatoryRegion|biolink:SiRNA|biolink:Snv|biolink:Study|biolink:StudyVariable|biolink:TranscriptionFactorBindingSite|biolink:Treatment|biolink:WebPage|biolink:Zygosity]`
* `-t, --in-taxon-label TEXT`
* `-ff, --facet-fields TEXT`
* `-fq, --facet-queries TEXT`
* `-l, --limit INTEGER`: The number of results to return  [default: 20]
* `--offset INTEGER`: The offset of the first result to be retrieved  [default: 0]
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
$ monarch solr association-table [OPTIONS] ENTITY_ID CATEGORY:{biolink:PairwiseGeneToGeneInteraction|biolink:GeneToExpressionSiteAssociation|biolink:VariantToGeneAssociation|biolink:MacromolecularMachineToBiologicalProcessAssociation|biolink:GeneToPhenotypicFeatureAssociation|biolink:MacromolecularMachineToMolecularActivityAssociation|biolink:MacromolecularMachineToCellularComponentAssociation|biolink:Association|biolink:GeneToGeneHomologyAssociation|biolink:GenotypeToPhenotypicFeatureAssociation|biolink:DiseaseToPhenotypicFeatureAssociation|biolink:GeneToPathwayAssociation|biolink:DiseaseOrPhenotypicFeatureToLocationAssociation|biolink:ChemicalToPathwayAssociation|biolink:GenotypeToDiseaseAssociation|biolink:CorrelatedGeneToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation|biolink:VariantToDiseaseAssociation|biolink:CausalGeneToDiseaseAssociation|biolink:ChemicalToDiseaseOrPhenotypicFeatureAssociation}
```

**Arguments**:

* `ENTITY_ID`: The entity to get associations for  [required]
* `CATEGORY:{biolink:PairwiseGeneToGeneInteraction|biolink:GeneToExpressionSiteAssociation|biolink:VariantToGeneAssociation|biolink:MacromolecularMachineToBiologicalProcessAssociation|biolink:GeneToPhenotypicFeatureAssociation|biolink:MacromolecularMachineToMolecularActivityAssociation|biolink:MacromolecularMachineToCellularComponentAssociation|biolink:Association|biolink:GeneToGeneHomologyAssociation|biolink:GenotypeToPhenotypicFeatureAssociation|biolink:DiseaseToPhenotypicFeatureAssociation|biolink:GeneToPathwayAssociation|biolink:DiseaseOrPhenotypicFeatureToLocationAssociation|biolink:ChemicalToPathwayAssociation|biolink:GenotypeToDiseaseAssociation|biolink:CorrelatedGeneToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation|biolink:VariantToDiseaseAssociation|biolink:CausalGeneToDiseaseAssociation|biolink:ChemicalToDiseaseOrPhenotypicFeatureAssociation}`: The association category to get associations for, ex. biolink:GeneToPhenotypicFeatureAssociation  [required]

**Options**:

* `-q, --query TEXT`
* `-t, --traverse-orthologs`: Whether to traverse orthologs when getting associations
* `-s, --sort TEXT`
* `-l, --limit INTEGER`: The number of results to return  [default: 20]
* `--offset INTEGER`: The offset of the first result to be retrieved  [default: 0]
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

* `-c, --category [biolink:PairwiseGeneToGeneInteraction|biolink:GeneToExpressionSiteAssociation|biolink:VariantToGeneAssociation|biolink:MacromolecularMachineToBiologicalProcessAssociation|biolink:GeneToPhenotypicFeatureAssociation|biolink:MacromolecularMachineToMolecularActivityAssociation|biolink:MacromolecularMachineToCellularComponentAssociation|biolink:Association|biolink:GeneToGeneHomologyAssociation|biolink:GenotypeToPhenotypicFeatureAssociation|biolink:DiseaseToPhenotypicFeatureAssociation|biolink:GeneToPathwayAssociation|biolink:DiseaseOrPhenotypicFeatureToLocationAssociation|biolink:ChemicalToPathwayAssociation|biolink:GenotypeToDiseaseAssociation|biolink:CorrelatedGeneToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation|biolink:VariantToDiseaseAssociation|biolink:CausalGeneToDiseaseAssociation|biolink:ChemicalToDiseaseOrPhenotypicFeatureAssociation]`: Category to get associations for
* `-s, --subject TEXT`: Subject ID to get associations for
* `-p, --predicate [biolink:interacts_with|biolink:expressed_in|biolink:has_phenotype|biolink:is_sequence_variant_of|biolink:enables|biolink:actively_involved_in|biolink:orthologous_to|biolink:located_in|biolink:subclass_of|biolink:related_to|biolink:participates_in|biolink:acts_upstream_of_or_within|biolink:active_in|biolink:part_of|biolink:model_of|biolink:causes|biolink:acts_upstream_of|biolink:has_mode_of_inheritance|biolink:contributes_to|biolink:gene_associated_with_condition|biolink:treats_or_applied_or_studied_to_treat|biolink:colocalizes_with|biolink:acts_upstream_of_positive_effect|biolink:acts_upstream_of_or_within_positive_effect|biolink:acts_upstream_of_negative_effect|biolink:acts_upstream_of_or_within_negative_effect]`: Predicate ID to get associations for
* `-o, --object TEXT`: Object ID to get associations for
* `-e, --entity TEXT`: Entity (subject or object) ID to get associations for
* `-d, --direct`: Whether to exclude associations with subject/object as ancestors
* `-C, --compact`: Whether to return a compact representation of the associations
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

### `monarch solr mappings`

**Usage**:

```console
$ monarch solr mappings [OPTIONS]
```

**Options**:

* `-e, --entity-id TEXT`: entity ID to get mappings for
* `-s, --subject-id TEXT`: subject ID to get mappings for
* `-p, --predicate-id [skos:exactMatch|skos:broadMatch]`: predicate ID to get mappings for
* `-o, --object-id TEXT`: object ID to get mappings for
* `-m, --mapping-justification TEXT`: mapping justification to get mappings for
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
* `-c, --category [biolink:SequenceVariant|biolink:Gene|biolink:Genotype|biolink:PhenotypicFeature|biolink:BiologicalProcessOrActivity|biolink:Disease|biolink:GrossAnatomicalStructure|biolink:Cell|biolink:Pathway|biolink:NamedThing|biolink:AnatomicalEntity|biolink:CellularComponent|biolink:MolecularEntity|biolink:BiologicalProcess|biolink:MacromolecularComplex|biolink:MolecularActivity|biolink:Protein|biolink:CellularOrganism|biolink:Vertebrate|biolink:Virus|biolink:BehavioralFeature|biolink:ChemicalEntity|biolink:LifeStage|biolink:PathologicalProcess|biolink:Drug|biolink:SmallMolecule|biolink:OrganismTaxon|biolink:InformationContentEntity|biolink:NucleicAcidEntity|biolink:EvidenceType|biolink:RNAProduct|biolink:Transcript|biolink:Fungus|biolink:Plant|biolink:ProcessedMaterial|biolink:Activity|biolink:Agent|biolink:ConfidenceLevel|biolink:Dataset|biolink:EnvironmentalFeature|biolink:GeneticInheritance|biolink:Haplotype|biolink:Invertebrate|biolink:Mammal|biolink:PopulationOfIndividualOrganisms|biolink:ProteinFamily|biolink:Publication|biolink:AccessibleDnaRegion|biolink:Bacterium|biolink:BiologicalSex|biolink:CellLine|biolink:ChemicalExposure|biolink:ChemicalMixture|biolink:DatasetDistribution|biolink:DiagnosticAid|biolink:DrugExposure|biolink:EnvironmentalProcess|biolink:Event|biolink:Exon|biolink:Genome|biolink:GenotypicSex|biolink:Human|biolink:IndividualOrganism|biolink:MaterialSample|biolink:MicroRNA|biolink:OrganismalEntity|biolink:Patent|biolink:PhenotypicSex|biolink:Polypeptide|biolink:ProteinDomain|biolink:ReagentTargetedGene|biolink:RegulatoryRegion|biolink:SiRNA|biolink:Snv|biolink:Study|biolink:StudyVariable|biolink:TranscriptionFactorBindingSite|biolink:Treatment|biolink:WebPage|biolink:Zygosity]`
* `-t, --in-taxon-label TEXT`
* `-ff, --facet-fields TEXT`
* `-fq, --facet-queries TEXT`
* `-l, --limit INTEGER`: The number of results to return  [default: 20]
* `--offset INTEGER`: The offset of the first result to be retrieved  [default: 0]
* `-f, --format [json|yaml|tsv|table]`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: Path to file to write command output (stdout if not specified)
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

* `-q, --quiet`: Set log level to warning
* `-d, --debug`: Set log level to debug
* `--help`: Show this message and exit.

**Commands**:

* `associations`: Paginate through associations
* `entity`: Retrieve an entity by ID

### `monarch sql associations`

Paginate through associations

**Usage**:

```console
$ monarch sql associations [OPTIONS]
```

**Options**:

* `-c, --category [biolink:PairwiseGeneToGeneInteraction|biolink:GeneToExpressionSiteAssociation|biolink:VariantToGeneAssociation|biolink:MacromolecularMachineToBiologicalProcessAssociation|biolink:GeneToPhenotypicFeatureAssociation|biolink:MacromolecularMachineToMolecularActivityAssociation|biolink:MacromolecularMachineToCellularComponentAssociation|biolink:Association|biolink:GeneToGeneHomologyAssociation|biolink:GenotypeToPhenotypicFeatureAssociation|biolink:DiseaseToPhenotypicFeatureAssociation|biolink:GeneToPathwayAssociation|biolink:DiseaseOrPhenotypicFeatureToLocationAssociation|biolink:ChemicalToPathwayAssociation|biolink:GenotypeToDiseaseAssociation|biolink:CorrelatedGeneToDiseaseAssociation|biolink:DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation|biolink:VariantToDiseaseAssociation|biolink:CausalGeneToDiseaseAssociation|biolink:ChemicalToDiseaseOrPhenotypicFeatureAssociation]`: Category to get associations for
* `-s, --subject TEXT`: Subject ID to get associations for
* `-p, --predicate [biolink:interacts_with|biolink:expressed_in|biolink:has_phenotype|biolink:is_sequence_variant_of|biolink:enables|biolink:actively_involved_in|biolink:orthologous_to|biolink:located_in|biolink:subclass_of|biolink:related_to|biolink:participates_in|biolink:acts_upstream_of_or_within|biolink:active_in|biolink:part_of|biolink:model_of|biolink:causes|biolink:acts_upstream_of|biolink:has_mode_of_inheritance|biolink:contributes_to|biolink:gene_associated_with_condition|biolink:treats_or_applied_or_studied_to_treat|biolink:colocalizes_with|biolink:acts_upstream_of_positive_effect|biolink:acts_upstream_of_or_within_positive_effect|biolink:acts_upstream_of_negative_effect|biolink:acts_upstream_of_or_within_negative_effect]`: Predicate ID to get associations for
* `-o, --object TEXT`: Object ID to get associations for
* `-e, --entity TEXT`: Entity (subject or object) ID to get associations for
* `-d, --direct`: Whether to exclude associations with subject/object as ancestors
* `-C, --compact`: Whether to return a compact representation of the associations
* `-l, --limit INTEGER`: The number of results to return  [default: 20]
* `--offset INTEGER`: The offset of the first result to be retrieved  [default: 0]
* `-f, --format [json|yaml|tsv|table]`: The format of the output (json, yaml, tsv, table)  [default: json]
* `-O, --output TEXT`: Path to file to write command output (stdout if not specified)
* `--help`: Show this message and exit.

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

## `monarch test`

Test the CLI

**Usage**:

```console
$ monarch test [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.
