from enum import Enum


class EntityCategory(Enum):
    """Entity categories"""

    GENE = "biolink:Gene"
    PHENOTYPIC_FEATURE = "biolink:PhenotypicFeature"
    GENOTYPE = "biolink:Genotype"
    ANATOMICAL_ENTITY = "biolink:AnatomicalEntity"
    BIOLOGICAL_PROCESS = "biolink:BiologicalProcess"
    DISEASE = "biolink:Disease"
    NAMED_THING = "biolink:NamedThing"
    PATHWAY = "biolink:Pathway"
    PROTEIN = "biolink:Protein"
    CHEMICAL_ENTITY = "biolink:ChemicalEntity"
    SEQUENCE_VARIANT = "biolink:SequenceVariant"
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
    GENE_TO_PHENOTYPIC_FEATURE_ASSOCIATION = "biolink:GeneToPhenotypicFeatureAssociation"
    ASSOCIATION = "biolink:Association"
    MACROMOLECULAR_MACHINE_TO_MOLECULAR_ACTIVITY_ASSOCIATION = (
        "biolink:MacromolecularMachineToMolecularActivityAssociation"
    )
    MACROMOLECULAR_MACHINE_TO_CELLULAR_COMPONENT_ASSOCIATION = (
        "biolink:MacromolecularMachineToCellularComponentAssociation"
    )
    GENE_TO_GENE_HOMOLOGY_ASSOCIATION = "biolink:GeneToGeneHomologyAssociation"
    GENOTYPE_TO_PHENOTYPIC_FEATURE_ASSOCIATION = "biolink:GenotypeToPhenotypicFeatureAssociation"
    DISEASE_TO_PHENOTYPIC_FEATURE_ASSOCIATION = "biolink:DiseaseToPhenotypicFeatureAssociation"
    GENE_TO_PATHWAY_ASSOCIATION = "biolink:GeneToPathwayAssociation"
    CHEMICAL_TO_PATHWAY_ASSOCIATION = "biolink:ChemicalToPathwayAssociation"
    VARIANT_TO_GENE_ASSOCIATION = "biolink:VariantToGeneAssociation"
    VARIANT_TO_DISEASE_ASSOCIATION = "biolink:VariantToDiseaseAssociation"
    GENOTYPE_TO_DISEASE_ASSOCIATION = "biolink:GenotypeToDiseaseAssociation"
    CORRELATED_GENE_TO_DISEASE_ASSOCIATION = "biolink:CorrelatedGeneToDiseaseAssociation"
    CHEMICAL_TO_DISEASE_OR_PHENOTYPIC_FEATURE_ASSOCIATION = "biolink:ChemicalToDiseaseOrPhenotypicFeatureAssociation"
    DISEASE_OR_PHENOTYPIC_FEATURE_TO_GENETIC_INHERITANCE_ASSOCIATION = (
        "biolink:DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation"
    )
    CAUSAL_GENE_TO_DISEASE_ASSOCIATION = "biolink:CausalGeneToDiseaseAssociation"
    DISEASE_OR_PHENOTYPIC_FEATURE_TO_LOCATION_ASSOCIATION = "biolink:DiseaseOrPhenotypicFeatureToLocationAssociation"
    CHEMICAL_OR_DRUG_OR_TREATMENT_TO_DISEASE_OR_PHENOTYPIC_FEATURE_ASSOCIATION = (
        "biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation"
    )
    VARIANT_TO_PHENOTYPIC_FEATURE_ASSOCIATION = "biolink:VariantToPhenotypicFeatureAssociation"


class AssociationPredicate(Enum):
    """Association predicates"""

    INTERACTS_WITH = "biolink:interacts_with"
    EXPRESSED_IN = "biolink:expressed_in"
    HAS_PHENOTYPE = "biolink:has_phenotype"
    ENABLES = "biolink:enables"
    ACTIVELY_INVOLVED_IN = "biolink:actively_involved_in"
    ORTHOLOGOUS_TO = "biolink:orthologous_to"
    SUBCLASS_OF = "biolink:subclass_of"
    LOCATED_IN = "biolink:located_in"
    RELATED_TO = "biolink:related_to"
    PARTICIPATES_IN = "biolink:participates_in"
    ACTS_UPSTREAM_OF_OR_WITHIN = "biolink:acts_upstream_of_or_within"
    IS_ACTIVE_IN = "biolink:is_active_in"
    PART_OF = "biolink:part_of"
    CAUSES = "biolink:causes"
    IS_SEQUENCE_VARIANT_OF = "biolink:is_sequence_variant_of"
    MODEL_OF = "biolink:model_of"
    ACTS_UPSTREAM_OF = "biolink:acts_upstream_of"
    TREATS_OR_APPLIED_OR_STUDIED_TO_TREAT = "biolink:treats_or_applied_or_studied_to_treat"
    HAS_MODE_OF_INHERITANCE = "biolink:has_mode_of_inheritance"
    GENE_ASSOCIATED_WITH_CONDITION = "biolink:gene_associated_with_condition"
    CONTRIBUTES_TO = "biolink:contributes_to"
    ASSOCIATED_WITH_INCREASED_LIKELIHOOD_OF = "biolink:associated_with_increased_likelihood_of"
    COLOCALIZES_WITH = "biolink:colocalizes_with"
    GENETICALLY_ASSOCIATED_WITH = "biolink:genetically_associated_with"
    DISEASE_HAS_LOCATION = "biolink:disease_has_location"
    ACTS_UPSTREAM_OF_POSITIVE_EFFECT = "biolink:acts_upstream_of_positive_effect"
    ACTS_UPSTREAM_OF_OR_WITHIN_POSITIVE_EFFECT = "biolink:acts_upstream_of_or_within_positive_effect"
    AMELIORATES_CONDITION = "biolink:ameliorates_condition"
    ACTS_UPSTREAM_OF_NEGATIVE_EFFECT = "biolink:acts_upstream_of_negative_effect"
    ACTS_UPSTREAM_OF_OR_WITHIN_NEGATIVE_EFFECT = "biolink:acts_upstream_of_or_within_negative_effect"
    PREVENTATIVE_FOR_CONDITION = "biolink:preventative_for_condition"
    CONTRAINDICATED_IN = "biolink:contraindicated_in"


class MappingPredicate(Enum):
    """Mapping predicates"""

    EXACT_MATCH = "skos:exactMatch"
    CLOSE_MATCH = "skos:closeMatch"
    BROAD_MATCH = "skos:broadMatch"
