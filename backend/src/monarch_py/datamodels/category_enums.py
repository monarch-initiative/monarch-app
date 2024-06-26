from enum import Enum


class EntityCategory(Enum):
    """Entity categories"""

    SEQUENCE_VARIANT = "biolink:SequenceVariant"
    GENE = "biolink:Gene"
    GENOTYPE = "biolink:Genotype"
    PHENOTYPIC_FEATURE = "biolink:PhenotypicFeature"
    BIOLOGICAL_PROCESS_OR_ACTIVITY = "biolink:BiologicalProcessOrActivity"
    DISEASE = "biolink:Disease"
    GROSS_ANATOMICAL_STRUCTURE = "biolink:GrossAnatomicalStructure"
    CELL = "biolink:Cell"
    PATHWAY = "biolink:Pathway"
    NAMED_THING = "biolink:NamedThing"
    ANATOMICAL_ENTITY = "biolink:AnatomicalEntity"
    CELLULAR_COMPONENT = "biolink:CellularComponent"
    MOLECULAR_ENTITY = "biolink:MolecularEntity"
    BIOLOGICAL_PROCESS = "biolink:BiologicalProcess"
    MACROMOLECULAR_COMPLEX = "biolink:MacromolecularComplex"
    MOLECULAR_ACTIVITY = "biolink:MolecularActivity"
    PROTEIN = "biolink:Protein"
    CELLULAR_ORGANISM = "biolink:CellularOrganism"
    VERTEBRATE = "biolink:Vertebrate"
    VIRUS = "biolink:Virus"
    BEHAVIORAL_FEATURE = "biolink:BehavioralFeature"
    CHEMICAL_ENTITY = "biolink:ChemicalEntity"
    LIFE_STAGE = "biolink:LifeStage"
    PATHOLOGICAL_PROCESS = "biolink:PathologicalProcess"
    DRUG = "biolink:Drug"
    SMALL_MOLECULE = "biolink:SmallMolecule"
    ORGANISM_TAXON = "biolink:OrganismTaxon"
    INFORMATION_CONTENT_ENTITY = "biolink:InformationContentEntity"
    NUCLEIC_ACID_ENTITY = "biolink:NucleicAcidEntity"
    EVIDENCE_TYPE = "biolink:EvidenceType"
    RNAPRODUCT = "biolink:RNAProduct"
    TRANSCRIPT = "biolink:Transcript"
    FUNGUS = "biolink:Fungus"
    PLANT = "biolink:Plant"
    PROCESSED_MATERIAL = "biolink:ProcessedMaterial"
    ACTIVITY = "biolink:Activity"
    AGENT = "biolink:Agent"
    CONFIDENCE_LEVEL = "biolink:ConfidenceLevel"
    DATASET = "biolink:Dataset"
    ENVIRONMENTAL_FEATURE = "biolink:EnvironmentalFeature"
    GENETIC_INHERITANCE = "biolink:GeneticInheritance"
    HAPLOTYPE = "biolink:Haplotype"
    INVERTEBRATE = "biolink:Invertebrate"
    MAMMAL = "biolink:Mammal"
    POPULATION_OF_INDIVIDUAL_ORGANISMS = "biolink:PopulationOfIndividualOrganisms"
    PROTEIN_FAMILY = "biolink:ProteinFamily"
    PUBLICATION = "biolink:Publication"
    ACCESSIBLE_DNA_REGION = "biolink:AccessibleDnaRegion"
    BACTERIUM = "biolink:Bacterium"
    BIOLOGICAL_SEX = "biolink:BiologicalSex"
    CELL_LINE = "biolink:CellLine"
    CHEMICAL_EXPOSURE = "biolink:ChemicalExposure"
    CHEMICAL_MIXTURE = "biolink:ChemicalMixture"
    DATASET_DISTRIBUTION = "biolink:DatasetDistribution"
    DIAGNOSTIC_AID = "biolink:DiagnosticAid"
    DRUG_EXPOSURE = "biolink:DrugExposure"
    ENVIRONMENTAL_PROCESS = "biolink:EnvironmentalProcess"
    EVENT = "biolink:Event"
    EXON = "biolink:Exon"
    GENOME = "biolink:Genome"
    GENOTYPIC_SEX = "biolink:GenotypicSex"
    HUMAN = "biolink:Human"
    INDIVIDUAL_ORGANISM = "biolink:IndividualOrganism"
    MATERIAL_SAMPLE = "biolink:MaterialSample"
    MICRO_RNA = "biolink:MicroRNA"
    ORGANISMAL_ENTITY = "biolink:OrganismalEntity"
    PATENT = "biolink:Patent"
    PHENOTYPIC_SEX = "biolink:PhenotypicSex"
    POLYPEPTIDE = "biolink:Polypeptide"
    PROTEIN_DOMAIN = "biolink:ProteinDomain"
    REAGENT_TARGETED_GENE = "biolink:ReagentTargetedGene"
    REGULATORY_REGION = "biolink:RegulatoryRegion"
    SI_RNA = "biolink:SiRNA"
    SNV = "biolink:Snv"
    STUDY = "biolink:Study"
    STUDY_VARIABLE = "biolink:StudyVariable"
    TRANSCRIPTION_FACTOR_BINDING_SITE = "biolink:TranscriptionFactorBindingSite"
    TREATMENT = "biolink:Treatment"
    WEB_PAGE = "biolink:WebPage"
    ZYGOSITY = "biolink:Zygosity"


class AssociationCategory(Enum):
    """Association categories"""

    PAIRWISE_GENE_TO_GENE_INTERACTION = "biolink:PairwiseGeneToGeneInteraction"
    GENE_TO_EXPRESSION_SITE_ASSOCIATION = "biolink:GeneToExpressionSiteAssociation"
    VARIANT_TO_GENE_ASSOCIATION = "biolink:VariantToGeneAssociation"
    MACROMOLECULAR_MACHINE_TO_BIOLOGICAL_PROCESS_ASSOCIATION = (
        "biolink:MacromolecularMachineToBiologicalProcessAssociation"
    )
    GENE_TO_PHENOTYPIC_FEATURE_ASSOCIATION = "biolink:GeneToPhenotypicFeatureAssociation"
    MACROMOLECULAR_MACHINE_TO_MOLECULAR_ACTIVITY_ASSOCIATION = (
        "biolink:MacromolecularMachineToMolecularActivityAssociation"
    )
    MACROMOLECULAR_MACHINE_TO_CELLULAR_COMPONENT_ASSOCIATION = (
        "biolink:MacromolecularMachineToCellularComponentAssociation"
    )
    ASSOCIATION = "biolink:Association"
    GENE_TO_GENE_HOMOLOGY_ASSOCIATION = "biolink:GeneToGeneHomologyAssociation"
    GENOTYPE_TO_PHENOTYPIC_FEATURE_ASSOCIATION = "biolink:GenotypeToPhenotypicFeatureAssociation"
    DISEASE_TO_PHENOTYPIC_FEATURE_ASSOCIATION = "biolink:DiseaseToPhenotypicFeatureAssociation"
    GENE_TO_PATHWAY_ASSOCIATION = "biolink:GeneToPathwayAssociation"
    DISEASE_OR_PHENOTYPIC_FEATURE_TO_LOCATION_ASSOCIATION = "biolink:DiseaseOrPhenotypicFeatureToLocationAssociation"
    CHEMICAL_TO_PATHWAY_ASSOCIATION = "biolink:ChemicalToPathwayAssociation"
    GENOTYPE_TO_DISEASE_ASSOCIATION = "biolink:GenotypeToDiseaseAssociation"
    CORRELATED_GENE_TO_DISEASE_ASSOCIATION = "biolink:CorrelatedGeneToDiseaseAssociation"
    DISEASE_OR_PHENOTYPIC_FEATURE_TO_GENETIC_INHERITANCE_ASSOCIATION = (
        "biolink:DiseaseOrPhenotypicFeatureToGeneticInheritanceAssociation"
    )
    VARIANT_TO_DISEASE_ASSOCIATION = "biolink:VariantToDiseaseAssociation"
    CAUSAL_GENE_TO_DISEASE_ASSOCIATION = "biolink:CausalGeneToDiseaseAssociation"
    CHEMICAL_TO_DISEASE_OR_PHENOTYPIC_FEATURE_ASSOCIATION = "biolink:ChemicalToDiseaseOrPhenotypicFeatureAssociation"


class AssociationPredicate(Enum):
    """Association predicates"""

    INTERACTS_WITH = "biolink:interacts_with"
    EXPRESSED_IN = "biolink:expressed_in"
    HAS_PHENOTYPE = "biolink:has_phenotype"
    IS_SEQUENCE_VARIANT_OF = "biolink:is_sequence_variant_of"
    ENABLES = "biolink:enables"
    ACTIVELY_INVOLVED_IN = "biolink:actively_involved_in"
    ORTHOLOGOUS_TO = "biolink:orthologous_to"
    LOCATED_IN = "biolink:located_in"
    SUBCLASS_OF = "biolink:subclass_of"
    RELATED_TO = "biolink:related_to"
    PARTICIPATES_IN = "biolink:participates_in"
    ACTS_UPSTREAM_OF_OR_WITHIN = "biolink:acts_upstream_of_or_within"
    ACTIVE_IN = "biolink:active_in"
    PART_OF = "biolink:part_of"
    MODEL_OF = "biolink:model_of"
    CAUSES = "biolink:causes"
    ACTS_UPSTREAM_OF = "biolink:acts_upstream_of"
    HAS_MODE_OF_INHERITANCE = "biolink:has_mode_of_inheritance"
    CONTRIBUTES_TO = "biolink:contributes_to"
    GENE_ASSOCIATED_WITH_CONDITION = "biolink:gene_associated_with_condition"
    TREATS_OR_APPLIED_OR_STUDIED_TO_TREAT = "biolink:treats_or_applied_or_studied_to_treat"
    COLOCALIZES_WITH = "biolink:colocalizes_with"
    ACTS_UPSTREAM_OF_POSITIVE_EFFECT = "biolink:acts_upstream_of_positive_effect"
    ACTS_UPSTREAM_OF_OR_WITHIN_POSITIVE_EFFECT = "biolink:acts_upstream_of_or_within_positive_effect"
    ACTS_UPSTREAM_OF_NEGATIVE_EFFECT = "biolink:acts_upstream_of_negative_effect"
    ACTS_UPSTREAM_OF_OR_WITHIN_NEGATIVE_EFFECT = "biolink:acts_upstream_of_or_within_negative_effect"


class MappingPredicate(Enum):
    """Mapping predicates"""

    EXACT_MATCH = "skos:exactMatch"
    BROAD_MATCH = "skos:broadMatch"
