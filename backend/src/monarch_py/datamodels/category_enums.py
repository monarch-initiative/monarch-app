from enum import Enum


class EntityCategory(Enum):
    """Entity categories"""

    GENE = "biolink:Gene"
    SEQUENCE_VARIANT = "biolink:SequenceVariant"
    PHENOTYPIC_FEATURE = "biolink:PhenotypicFeature"
    GENOTYPE = "biolink:Genotype"
    ANATOMICAL_ENTITY = "biolink:AnatomicalEntity"
    NAMED_THING = "biolink:NamedThing"
    BIOLOGICAL_PROCESS = "biolink:BiologicalProcess"
    DISEASE = "biolink:Disease"
    PROTEIN = "biolink:Protein"
    PATHWAY = "biolink:Pathway"
    CHEMICAL_ENTITY = "biolink:ChemicalEntity"
    MOLECULAR_ACTIVITY = "biolink:MolecularActivity"
    CASE = "biolink:Case"
    CELLULAR_COMPONENT = "biolink:CellularComponent"
    CELL = "biolink:Cell"
    ORGANISM_TAXON = "biolink:OrganismTaxon"
    MOLECULAR_ENTITY = "biolink:MolecularEntity"
    LIFE_STAGE = "biolink:LifeStage"


class AssociationCategory(Enum):
    """Association categories"""

    PAIRWISE_GENE_TO_GENE_INTERACTION = "biolink:PairwiseGeneToGeneInteraction"
    GENE_TO_EXPRESSION_SITE_ASSOCIATION = "biolink:GeneToExpressionSiteAssociation"
    GENE_TO_GENE_HOMOLOGY_ASSOCIATION = "biolink:GeneToGeneHomologyAssociation"
    ASSOCIATION = "biolink:Association"
    MACROMOLECULAR_MACHINE_TO_BIOLOGICAL_PROCESS_ASSOCIATION = (
        "biolink:MacromolecularMachineToBiologicalProcessAssociation"
    )
    MACROMOLECULAR_MACHINE_TO_MOLECULAR_ACTIVITY_ASSOCIATION = (
        "biolink:MacromolecularMachineToMolecularActivityAssociation"
    )
    MACROMOLECULAR_MACHINE_TO_CELLULAR_COMPONENT_ASSOCIATION = (
        "biolink:MacromolecularMachineToCellularComponentAssociation"
    )
    GENE_TO_PHENOTYPIC_FEATURE_ASSOCIATION = "biolink:GeneToPhenotypicFeatureAssociation"
    GENOTYPE_TO_PHENOTYPIC_FEATURE_ASSOCIATION = "biolink:GenotypeToPhenotypicFeatureAssociation"
    VARIANT_TO_PHENOTYPIC_FEATURE_ASSOCIATION = "biolink:VariantToPhenotypicFeatureAssociation"
    DISEASE_TO_PHENOTYPIC_FEATURE_ASSOCIATION = "biolink:DiseaseToPhenotypicFeatureAssociation"
    GENE_TO_PATHWAY_ASSOCIATION = "biolink:GeneToPathwayAssociation"
    VARIANT_TO_GENE_ASSOCIATION = "biolink:VariantToGeneAssociation"
    CASE_TO_PHENOTYPIC_FEATURE_ASSOCIATION = "biolink:CaseToPhenotypicFeatureAssociation"
    GENOTYPE_TO_GENE_ASSOCIATION = "biolink:GenotypeToGeneAssociation"
    GENOTYPE_TO_VARIANT_ASSOCIATION = "biolink:GenotypeToVariantAssociation"
    CHEMICAL_ENTITY_TO_PATHWAY_ASSOCIATION = "biolink:ChemicalEntityToPathwayAssociation"
    VARIANT_TO_DISEASE_ASSOCIATION = "biolink:VariantToDiseaseAssociation"
    CHEMICAL_ENTITY_TO_DISEASE_OR_PHENOTYPIC_FEATURE_ASSOCIATION = (
        "biolink:ChemicalEntityToDiseaseOrPhenotypicFeatureAssociation"
    )
    GENOTYPE_TO_DISEASE_ASSOCIATION = "biolink:GenotypeToDiseaseAssociation"
    DISEASE_OR_PHENOTYPIC_FEATURE_TO_GENETIC_INHERITANCE_ASSOCIATION = (
        "biolink:DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation"
    )
    CORRELATED_GENE_TO_DISEASE_ASSOCIATION = "biolink:CorrelatedGeneToDiseaseAssociation"
    CASE_TO_DISEASE_ASSOCIATION = "biolink:CaseToDiseaseAssociation"
    CASE_TO_GENE_ASSOCIATION = "biolink:CaseToGeneAssociation"
    CAUSAL_GENE_TO_DISEASE_ASSOCIATION = "biolink:CausalGeneToDiseaseAssociation"
    DISEASE_OR_PHENOTYPIC_FEATURE_TO_LOCATION_ASSOCIATION = "biolink:DiseaseOrPhenotypicFeatureToLocationAssociation"
    CHEMICAL_OR_DRUG_OR_TREATMENT_TO_DISEASE_OR_PHENOTYPIC_FEATURE_ASSOCIATION = (
        "biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation"
    )


class AssociationPredicate(Enum):
    """Association predicates"""

    INTERACTS_WITH = "biolink:interacts_with"
    EXPRESSED_IN = "biolink:expressed_in"
    HAS_PHENOTYPE = "biolink:has_phenotype"
    ORTHOLOGOUS_TO = "biolink:orthologous_to"
    ENABLES = "biolink:enables"
    ACTIVELY_INVOLVED_IN = "biolink:actively_involved_in"
    RELATED_TO = "biolink:related_to"
    LOCATED_IN = "biolink:located_in"
    SUBCLASS_OF = "biolink:subclass_of"
    PARTICIPATES_IN = "biolink:participates_in"
    ACTS_UPSTREAM_OF_OR_WITHIN = "biolink:acts_upstream_of_or_within"
    IS_SEQUENCE_VARIANT_OF = "biolink:is_sequence_variant_of"
    IS_ACTIVE_IN = "biolink:is_active_in"
    HAS_SEQUENCE_VARIANT = "biolink:has_sequence_variant"
    PART_OF = "biolink:part_of"
    CAUSES = "biolink:causes"
    TREATS_OR_APPLIED_OR_STUDIED_TO_TREAT = "biolink:treats_or_applied_or_studied_to_treat"
    HOMOLOGOUS_TO = "biolink:homologous_to"
    CONTRIBUTES_TO = "biolink:contributes_to"
    MODEL_OF = "biolink:model_of"
    HAS_MODE_OF_INHERITANCE = "biolink:has_mode_of_inheritance"
    HAS_DISEASE = "biolink:has_disease"
    HAS_GENE = "biolink:has_gene"
    GENE_ASSOCIATED_WITH_CONDITION = "biolink:gene_associated_with_condition"
    ASSOCIATED_WITH_INCREASED_LIKELIHOOD_OF = "biolink:associated_with_increased_likelihood_of"
    COLOCALIZES_WITH = "biolink:colocalizes_with"
    SAME_AS = "biolink:same_as"
    ACTS_UPSTREAM_OF = "biolink:acts_upstream_of"
    GENETICALLY_ASSOCIATED_WITH = "biolink:genetically_associated_with"
    DISEASE_HAS_LOCATION = "biolink:disease_has_location"
    ACTS_UPSTREAM_OF_OR_WITHIN_POSITIVE_EFFECT = "biolink:acts_upstream_of_or_within_positive_effect"
    AMELIORATES_CONDITION = "biolink:ameliorates_condition"
    ACTS_UPSTREAM_OF_POSITIVE_EFFECT = "biolink:acts_upstream_of_positive_effect"
    ACTS_UPSTREAM_OF_NEGATIVE_EFFECT = "biolink:acts_upstream_of_negative_effect"
    ACTS_UPSTREAM_OF_OR_WITHIN_NEGATIVE_EFFECT = "biolink:acts_upstream_of_or_within_negative_effect"
    HAS_PARTICIPANT = "biolink:has_participant"
    PREVENTATIVE_FOR_CONDITION = "biolink:preventative_for_condition"
    DISRUPTS = "biolink:disrupts"
    CAUSED_BY = "biolink:caused_by"
    CONTRAINDICATED_IN = "biolink:contraindicated_in"


class MappingPredicate(Enum):
    """Mapping predicates"""

    EXACT_MATCH = "skos:exactMatch"
    CLOSE_MATCH = "skos:closeMatch"
    BROAD_MATCH = "skos:broadMatch"
