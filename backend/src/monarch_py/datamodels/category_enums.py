from enum import Enum


class EntityCategory(Enum):
    """Entity categories"""

    GENE = "biolink:Gene"
    SEQUENCE_VARIANT = "biolink:SequenceVariant"
    PHENOTYPIC_FEATURE = "biolink:PhenotypicFeature"
    GENOTYPE = "biolink:Genotype"
    ANATOMICAL_ENTITY = "biolink:AnatomicalEntity"
    BIOLOGICAL_PROCESS = "biolink:BiologicalProcess"
    DISEASE = "biolink:Disease"
    NAMED_THING = "biolink:NamedThing"
    PROTEIN = "biolink:Protein"
    CHEMICAL_ENTITY = "biolink:ChemicalEntity"
    PATHWAY = "biolink:Pathway"
    MOLECULAR_ACTIVITY = "biolink:MolecularActivity"
    CELLULAR_COMPONENT = "biolink:CellularComponent"
    CELL = "biolink:Cell"
    ORGANISM_TAXON = "biolink:OrganismTaxon"
    MOLECULAR_ENTITY = "biolink:MolecularEntity"
    LIFE_STAGE = "biolink:LifeStage"


class AssociationCategory(Enum):
    """Association categories"""

    PAIRWISE_GENE_TO_GENE_INTERACTION = "biolink:PairwiseGeneToGeneInteraction"
    GENE_TO_EXPRESSION_SITE_ASSOCIATION = "biolink:GeneToExpressionSiteAssociation"
    MACROMOLECULAR_MACHINE_TO_BIOLOGICAL_PROCESS_ASSOCIATION = (
        "biolink:MacromolecularMachineToBiologicalProcessAssociation"
    )
    GENE_TO_GENE_HOMOLOGY_ASSOCIATION = "biolink:GeneToGeneHomologyAssociation"
    MACROMOLECULAR_MACHINE_TO_MOLECULAR_ACTIVITY_ASSOCIATION = (
        "biolink:MacromolecularMachineToMolecularActivityAssociation"
    )
    MACROMOLECULAR_MACHINE_TO_CELLULAR_COMPONENT_ASSOCIATION = (
        "biolink:MacromolecularMachineToCellularComponentAssociation"
    )
    ASSOCIATION = "biolink:Association"
    GENE_TO_PHENOTYPIC_FEATURE_ASSOCIATION = "biolink:GeneToPhenotypicFeatureAssociation"
    GENOTYPE_TO_PHENOTYPIC_FEATURE_ASSOCIATION = "biolink:GenotypeToPhenotypicFeatureAssociation"
    VARIANT_TO_PHENOTYPIC_FEATURE_ASSOCIATION = "biolink:VariantToPhenotypicFeatureAssociation"
    DISEASE_TO_PHENOTYPIC_FEATURE_ASSOCIATION = "biolink:DiseaseToPhenotypicFeatureAssociation"
    GENE_TO_PATHWAY_ASSOCIATION = "biolink:GeneToPathwayAssociation"
    VARIANT_TO_GENE_ASSOCIATION = "biolink:VariantToGeneAssociation"
    GENOTYPE_TO_VARIANT_ASSOCIATION = "biolink:GenotypeToVariantAssociation"
    GENOTYPE_TO_GENE_ASSOCIATION = "biolink:GenotypeToGeneAssociation"
    CHEMICAL_TO_PATHWAY_ASSOCIATION = "biolink:ChemicalToPathwayAssociation"
    CHEMICAL_TO_DISEASE_OR_PHENOTYPIC_FEATURE_ASSOCIATION = "biolink:ChemicalToDiseaseOrPhenotypicFeatureAssociation"
    VARIANT_TO_DISEASE_ASSOCIATION = "biolink:VariantToDiseaseAssociation"
    GENOTYPE_TO_DISEASE_ASSOCIATION = "biolink:GenotypeToDiseaseAssociation"
    DISEASE_OR_PHENOTYPIC_FEATURE_TO_GENETIC_INHERITANCE_ASSOCIATION = (
        "biolink:DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation"
    )
    CORRELATED_GENE_TO_DISEASE_ASSOCIATION = "biolink:CorrelatedGeneToDiseaseAssociation"
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
    LOCATED_IN = "biolink:located_in"
    SUBCLASS_OF = "biolink:subclass_of"
    RELATED_TO = "biolink:related_to"
    PARTICIPATES_IN = "biolink:participates_in"
    ACTS_UPSTREAM_OF_OR_WITHIN = "biolink:acts_upstream_of_or_within"
    IS_ACTIVE_IN = "biolink:is_active_in"
    IS_SEQUENCE_VARIANT_OF = "biolink:is_sequence_variant_of"
    HAS_SEQUENCE_VARIANT = "biolink:has_sequence_variant"
    PART_OF = "biolink:part_of"
    TREATS_OR_APPLIED_OR_STUDIED_TO_TREAT = "biolink:treats_or_applied_or_studied_to_treat"
    CAUSES = "biolink:causes"
    ACTS_UPSTREAM_OF = "biolink:acts_upstream_of"
    MODEL_OF = "biolink:model_of"
    CONTRIBUTES_TO = "biolink:contributes_to"
    HAS_MODE_OF_INHERITANCE = "biolink:has_mode_of_inheritance"
    GENE_ASSOCIATED_WITH_CONDITION = "biolink:gene_associated_with_condition"
    ASSOCIATED_WITH_INCREASED_LIKELIHOOD_OF = "biolink:associated_with_increased_likelihood_of"
    COLOCALIZES_WITH = "biolink:colocalizes_with"
    GENETICALLY_ASSOCIATED_WITH = "biolink:genetically_associated_with"
    DISEASE_HAS_LOCATION = "biolink:disease_has_location"
    ACTS_UPSTREAM_OF_POSITIVE_EFFECT = "biolink:acts_upstream_of_positive_effect"
    AMELIORATES_CONDITION = "biolink:ameliorates_condition"
    ACTS_UPSTREAM_OF_OR_WITHIN_POSITIVE_EFFECT = "biolink:acts_upstream_of_or_within_positive_effect"
    ACTS_UPSTREAM_OF_NEGATIVE_EFFECT = "biolink:acts_upstream_of_negative_effect"
    HAS_PARTICIPANT = "biolink:has_participant"
    ACTS_UPSTREAM_OF_OR_WITHIN_NEGATIVE_EFFECT = "biolink:acts_upstream_of_or_within_negative_effect"
    PREVENTATIVE_FOR_CONDITION = "biolink:preventative_for_condition"
    DISRUPTS = "biolink:disrupts"
    CAUSED_BY = "biolink:caused_by"
    CONTRAINDICATED_IN = "biolink:contraindicated_in"


class MappingPredicate(Enum):
    """Mapping predicates"""

    EXACT_MATCH = "skos:exactMatch"
    CLOSE_MATCH = "skos:closeMatch"
    BROAD_MATCH = "skos:broadMatch"
