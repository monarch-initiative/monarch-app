# Modeling Principles

## Conforms to Schema
The Monarch Biolink Specification is an implementation of the Biolink Model.
The KG must be conformant with The Monarch Biolink Specification.

## Node Normalization
The final KG must have Nodes normalized to the canonical prefix for any given node type.
The canonical prefix should be determined by The Monarch Biolink Model Specification.

## Authoratative Source
Providers of Associations are not the authoratative sources for the Nodes in general. Nodes should be ingested from their
own authoratative source, seperate from edge ingests.

## Genes and Proteins
Genes and reference Proteins shall be treated as equivalent.
When collapsing nodes give the Gene Id the priority, original_subject = UniProt Id.
If in future there is a need to represent Isoforms, then UniProt Isoform Ids should be used.

## Variants
Variant to Disease/Phenotype Associations may be rolled up to the Gene level.
If they are rolled up, then a subject_modifier = Variant Id.

## Gene to Disease Associations
Gene to Disease Associations should come from high quality sources that have been vetted by domain experts within Monarch.
Gene to Disease Associations must not confuse single Gene causal Mendelian Associations with otherwise associated Genes. (e.g. contributing or associated Genes)

