
import pytest

@pytest.fixture
def node_json():
    return """
{
    "id": "MONDO:0020121",
    "category": "biolink:Disease",
    "name": "muscular dystrophy",
    "description": "Muscular dystrophy (MD) refers to a group of more than 30 genetic diseases characterized by progressive weakness and degeneration of the skeletal muscles that control movement. Some forms of MD are seen in newborns, infants or children, while others have late-onset and may not appear until middle age or later. The disorders differ in terms of the distribution and extent of muscle weakness (some forms of MD also affect cardiac muscle), age of onset, rate of progression, and pattern of inheritance. The prognosis for people with MD varies according to the type and progression of the disorder. There is no specific treatment to stop or reverse any form of MD. Treatment is supportive and may include physical therapy, respiratory therapy, speech therapy, orthopedic appliances used for support, corrective orthopedic surgery, and medicationsincluding corticosteroids, anticonvulsants (seizure medications), immunosuppressants, and antibiotics. Some individuals may need assisted ventilation to treat respiratory muscle weaknessor a pacemaker for cardiac (heart)abnormalities.",
    "xref": [
        "DOID:9884",
        "GARD:0007922",
        "ICD10CM:G71.0",
        "ICD9:359.1",
        "MEDGEN:44527",
        "MESH:D009136",
        "MedDRA:10028356",
        "NANDO:1200486",
        "NANDO:2100233",
        "NCIT:C84910",
        "Orphanet:98473",
        "SCTID:73297009",
        "UMLS:C0026850",
        "icd11.foundation:1464662404"
    ],
    "synonym": null,
    "exact_synonym": null,
    "broad_synonym": null,
    "narrow_synonym": null,
    "related_synonym": null,
    "deprecated": null,
    "in_taxon": null,
    "in_taxon_label": null,
    "iri": null,
    "same_as": null,
    "subsets": [
        "disease_grouping",
        "doid_rare",
        "gard_rare",
        "ncit_rare",
        "ordo_group_of_disorders",
        "otar",
        "rare"
    ],
    "file_source": "phenio_nodes",
    "provided_by": "phenio_nodes",
    "full_name": null,
    "symbol": null,
    "has_gene": null,
    "type": null,
    "has_attribute": null,
    "has_biological_sex": null,
    "synonyms": null,
    "namespace": "MONDO",
    "has_phenotype": null,
    "has_phenotype_label": null,
    "has_phenotype_count": 0,
    "has_phenotype_closure": null,
    "has_phenotype_closure_label": null,
    "has_descendant": null,
    "has_descendant_label": null,
    "has_descendant_count": 201,
    "uri": "http://purl.obolibrary.org/obo/MONDO_0020121",
    "inheritance": null,
    "causal_gene": [],
    "causes_disease": null,
    "node_relationships": [],
    "mappings": [
        {
            "id": "Orphanet:98473",
            "url": "https://www.orpha.net/en/disease/detail/98473"
        },
        {
            "id": "NCIT:C84910",
            "url": "http://purl.obolibrary.org/obo/NCIT_C84910"
        },
        {
            "id": "icd11.foundation:1464662404",
            "url": null
        },
        {
            "id": "MEDGEN:44527",
            "url": "http://identifiers.org/medgen/44527"
        },
        {
            "id": "UMLS:C0026850",
            "url": "http://identifiers.org/umls/C0026850"
        },
        {
            "id": "MESH:D009136",
            "url": "http://identifiers.org/mesh/D009136"
        },
        {
            "id": "DOID:9884",
            "url": "http://purl.obolibrary.org/obo/DOID_9884"
        },
        {
            "id": "ICD10CM:G71.0",
            "url": "https://www.icd10data.com/search?s=G71.0"
        },
        {
            "id": "SCTID:73297009",
            "url": "http://identifiers.org/snomedct/73297009"
        }
    ],
    "external_links": [
        {
            "id": "DOID:9884",
            "url": "http://purl.obolibrary.org/obo/DOID_9884"
        },
        {
            "id": "GARD:0007922",
            "url": "https://rarediseases.info.nih.gov/diseases/0007922/index"
        },
        {
            "id": "ICD10CM:G71.0",
            "url": "https://www.icd10data.com/search?s=G71.0"
        },
        {
            "id": "ICD9:359.1",
            "url": null
        },
        {
            "id": "MEDGEN:44527",
            "url": "http://identifiers.org/medgen/44527"
        },
        {
            "id": "MESH:D009136",
            "url": "http://identifiers.org/mesh/D009136"
        },
        {
            "id": "MedDRA:10028356",
            "url": null
        },
        {
            "id": "NANDO:1200486",
            "url": "http://identifiers.org/NANDO:1200486"
        },
        {
            "id": "NANDO:2100233",
            "url": "http://identifiers.org/NANDO:2100233"
        },
        {
            "id": "NCIT:C84910",
            "url": "http://purl.obolibrary.org/obo/NCIT_C84910"
        },
        {
            "id": "Orphanet:98473",
            "url": "https://www.orpha.net/en/disease/detail/98473"
        },
        {
            "id": "SCTID:73297009",
            "url": "http://identifiers.org/snomedct/73297009"
        },
        {
            "id": "UMLS:C0026850",
            "url": "http://identifiers.org/umls/C0026850"
        },
        {
            "id": "icd11.foundation:1464662404",
            "url": null
        }
    ],
    "provided_by_link": {
        "id": "phenio",
        "url": "https://monarch-app.monarchinitiative.org/Sources/phenio/"
    },
    "association_counts": [
        {
            "label": "Disease Model",
            "count": 246,
            "category": "biolink:GenotypeToDiseaseAssociation",
            "count_direct": 14,
            "count_with_orthologs": null
        },
        {
            "label": "Disease to Phenotype",
            "count": 4247,
            "category": "biolink:DiseaseToPhenotypicFeatureAssociation",
            "count_direct": 0,
            "count_with_orthologs": null
        },
        {
            "label": "Causal Gene",
            "count": 133,
            "category": "biolink:CausalGeneToDiseaseAssociation",
            "count_direct": 0,
            "count_with_orthologs": null
        },
        {
            "label": "Correlated Gene",
            "count": 156,
            "category": "biolink:CorrelatedGeneToDiseaseAssociation",
            "count_direct": 0,
            "count_with_orthologs": null
        },
        {
            "label": "Variant to Disease",
            "count": 701,
            "category": "biolink:VariantToDiseaseAssociation",
            "count_direct": 0,
            "count_with_orthologs": null
        },
        {
            "label": "Medical Action",
            "count": 6,
            "category": "biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation",
            "count_direct": 0,
            "count_with_orthologs": null
        },
        {
            "label": "Cases",
            "count": 136,
            "category": "biolink:CaseToDiseaseAssociation",
            "count_direct": 0,
            "count_with_orthologs": null
        }
    ],
    "cross_species_term_clique": null,
    "node_hierarchy": {
        "super_classes": [
            {
                "id": "MONDO:0005336",
                "category": "biolink:Disease",
                "name": "myopathy",
                "description": null,
                "xref": null,
                "synonym": null,
                "exact_synonym": null,
                "broad_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "deprecated": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "iri": null,
                "same_as": null,
                "subsets": null,
                "file_source": null,
                "provided_by": null,
                "full_name": null,
                "symbol": null,
                "has_gene": null,
                "type": null,
                "has_attribute": null,
                "has_biological_sex": null,
                "synonyms": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_count": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_descendant": null,
                "has_descendant_label": null,
                "has_descendant_count": null
            },
            {
                "id": "MONDO:0100546",
                "category": "biolink:Disease",
                "name": "hereditary neuromuscular disease",
                "description": null,
                "xref": null,
                "synonym": null,
                "exact_synonym": null,
                "broad_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "deprecated": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "iri": null,
                "same_as": null,
                "subsets": null,
                "file_source": null,
                "provided_by": null,
                "full_name": null,
                "symbol": null,
                "has_gene": null,
                "type": null,
                "has_attribute": null,
                "has_biological_sex": null,
                "synonyms": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_count": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_descendant": null,
                "has_descendant_label": null,
                "has_descendant_count": null
            },
            {
                "id": "MONDO:0700223",
                "category": "biolink:Disease",
                "name": "hereditary skeletal muscle disorder",
                "description": null,
                "xref": null,
                "synonym": null,
                "exact_synonym": null,
                "broad_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "deprecated": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "iri": null,
                "same_as": null,
                "subsets": null,
                "file_source": null,
                "provided_by": null,
                "full_name": null,
                "symbol": null,
                "has_gene": null,
                "type": null,
                "has_attribute": null,
                "has_biological_sex": null,
                "synonyms": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_count": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_descendant": null,
                "has_descendant_label": null,
                "has_descendant_count": null
            }
        ],
        "sub_classes": [
            {
                "id": "MONDO:0008028",
                "category": "biolink:Disease",
                "name": "muscular dystrophy, Barnes type",
                "description": null,
                "xref": null,
                "synonym": null,
                "exact_synonym": null,
                "broad_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "deprecated": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "iri": null,
                "same_as": null,
                "subsets": null,
                "file_source": null,
                "provided_by": null,
                "full_name": null,
                "symbol": null,
                "has_gene": null,
                "type": null,
                "has_attribute": null,
                "has_biological_sex": null,
                "synonyms": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_count": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_descendant": null,
                "has_descendant_label": null,
                "has_descendant_count": null
            },
            {
                "id": "MONDO:0010675",
                "category": "biolink:Disease",
                "name": "muscular dystrophy, cardiac type",
                "description": null,
                "xref": null,
                "synonym": null,
                "exact_synonym": null,
                "broad_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "deprecated": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "iri": null,
                "same_as": null,
                "subsets": null,
                "file_source": null,
                "provided_by": null,
                "full_name": null,
                "symbol": null,
                "has_gene": null,
                "type": null,
                "has_attribute": null,
                "has_biological_sex": null,
                "synonyms": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_count": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_descendant": null,
                "has_descendant_label": null,
                "has_descendant_count": null
            },
            {
                "id": "MONDO:0018949",
                "category": "biolink:Disease",
                "name": "distal myopathy",
                "description": null,
                "xref": null,
                "synonym": null,
                "exact_synonym": null,
                "broad_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "deprecated": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "iri": null,
                "same_as": null,
                "subsets": null,
                "file_source": null,
                "provided_by": null,
                "full_name": null,
                "symbol": null,
                "has_gene": null,
                "type": null,
                "has_attribute": null,
                "has_biological_sex": null,
                "synonyms": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_count": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_descendant": null,
                "has_descendant_label": null,
                "has_descendant_count": null
            },
            {
                "id": "MONDO:0016106",
                "category": "biolink:Disease",
                "name": "progressive muscular dystrophy",
                "description": null,
                "xref": null,
                "synonym": null,
                "exact_synonym": null,
                "broad_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "deprecated": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "iri": null,
                "same_as": null,
                "subsets": null,
                "file_source": null,
                "provided_by": null,
                "full_name": null,
                "symbol": null,
                "has_gene": null,
                "type": null,
                "has_attribute": null,
                "has_biological_sex": null,
                "synonyms": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_count": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_descendant": null,
                "has_descendant_label": null,
                "has_descendant_count": null
            },
            {
                "id": "MONDO:0023204",
                "category": "biolink:Disease",
                "name": "Fukuda-Miyanomae-Nakata syndrome",
                "description": null,
                "xref": null,
                "synonym": null,
                "exact_synonym": null,
                "broad_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "deprecated": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "iri": null,
                "same_as": null,
                "subsets": null,
                "file_source": null,
                "provided_by": null,
                "full_name": null,
                "symbol": null,
                "has_gene": null,
                "type": null,
                "has_attribute": null,
                "has_biological_sex": null,
                "synonyms": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_count": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_descendant": null,
                "has_descendant_label": null,
                "has_descendant_count": null
            },
            {
                "id": "MONDO:0019950",
                "category": "biolink:Disease",
                "name": "congenital muscular dystrophy",
                "description": null,
                "xref": null,
                "synonym": null,
                "exact_synonym": null,
                "broad_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "deprecated": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "iri": null,
                "same_as": null,
                "subsets": null,
                "file_source": null,
                "provided_by": null,
                "full_name": null,
                "symbol": null,
                "has_gene": null,
                "type": null,
                "has_attribute": null,
                "has_biological_sex": null,
                "synonyms": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_count": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_descendant": null,
                "has_descendant_label": null,
                "has_descendant_count": null
            },
            {
                "id": "MONDO:0700285",
                "category": "biolink:Disease",
                "name": "DMD-related muscular dystrophy",
                "description": null,
                "xref": null,
                "synonym": null,
                "exact_synonym": null,
                "broad_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "deprecated": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "iri": null,
                "same_as": null,
                "subsets": null,
                "file_source": null,
                "provided_by": null,
                "full_name": null,
                "symbol": null,
                "has_gene": null,
                "type": null,
                "has_attribute": null,
                "has_biological_sex": null,
                "synonyms": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_count": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_descendant": null,
                "has_descendant_label": null,
                "has_descendant_count": null
            },
            {
                "id": "MONDO:0010676",
                "category": "biolink:Disease",
                "name": "muscular dystrophy, Hemizygous lethal type",
                "description": null,
                "xref": null,
                "synonym": null,
                "exact_synonym": null,
                "broad_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "deprecated": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "iri": null,
                "same_as": null,
                "subsets": null,
                "file_source": null,
                "provided_by": null,
                "full_name": null,
                "symbol": null,
                "has_gene": null,
                "type": null,
                "has_attribute": null,
                "has_biological_sex": null,
                "synonyms": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_count": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_descendant": null,
                "has_descendant_label": null,
                "has_descendant_count": null
            },
            {
                "id": "MONDO:0010677",
                "category": "biolink:Disease",
                "name": "muscular dystrophy, Mabry type",
                "description": null,
                "xref": null,
                "synonym": null,
                "exact_synonym": null,
                "broad_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "deprecated": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "iri": null,
                "same_as": null,
                "subsets": null,
                "file_source": null,
                "provided_by": null,
                "full_name": null,
                "symbol": null,
                "has_gene": null,
                "type": null,
                "has_attribute": null,
                "has_biological_sex": null,
                "synonyms": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_count": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_descendant": null,
                "has_descendant_label": null,
                "has_descendant_count": null
            },
            {
                "id": "MONDO:0010678",
                "category": "biolink:Disease",
                "name": "muscular dystrophy, progressive Pectorodorsal",
                "description": null,
                "xref": null,
                "synonym": null,
                "exact_synonym": null,
                "broad_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "deprecated": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "iri": null,
                "same_as": null,
                "subsets": null,
                "file_source": null,
                "provided_by": null,
                "full_name": null,
                "symbol": null,
                "has_gene": null,
                "type": null,
                "has_attribute": null,
                "has_biological_sex": null,
                "synonyms": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_count": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_descendant": null,
                "has_descendant_label": null,
                "has_descendant_count": null
            },
            {
                "id": "MONDO:0100228",
                "category": "biolink:Disease",
                "name": "LAMA2-related muscular dystrophy",
                "description": null,
                "xref": null,
                "synonym": null,
                "exact_synonym": null,
                "broad_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "deprecated": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "iri": null,
                "same_as": null,
                "subsets": null,
                "file_source": null,
                "provided_by": null,
                "full_name": null,
                "symbol": null,
                "has_gene": null,
                "type": null,
                "has_attribute": null,
                "has_biological_sex": null,
                "synonyms": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_count": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_descendant": null,
                "has_descendant_label": null,
                "has_descendant_count": null
            }
        ]
    }
}
"""

@pytest.fixture
def node_tsv():
    return """
id	category	name	description	xref	synonym	exact_synonym	broad_synonym	narrow_synonym	related_synonym	deprecated	in_taxon	in_taxon_label	iri	same_as	subsets	file_source	provided_by	full_name	symbol	has_gene	type	has_attribute	has_biological_sex	synonyms	namespace	has_phenotype	has_phenotype_label	has_phenotype_count	has_phenotype_closure	has_phenotype_closure_label	has_descendant	has_descendant_label	has_descendant_count	uri	inheritance	causal_gene	causes_disease	node_relationships	mappings	external_links	provided_by_link	association_counts	cross_species_term_clique	node_hierarchy
MONDO:0020121	biolink:Disease	muscular dystrophy	Muscular dystrophy (MD) refers to a group of more than 30 genetic diseases characterized by progressive weakness and degeneration of the skeletal muscles that control movement. Some forms of MD are seen in newborns, infants or children, while others have late-onset and may not appear until middle age or later. The disorders differ in terms of the distribution and extent of muscle weakness (some forms of MD also affect cardiac muscle), age of onset, rate of progression, and pattern of inheritance. The prognosis for people with MD varies according to the type and progression of the disorder. There is no specific treatment to stop or reverse any form of MD. Treatment is supportive and may include physical therapy, respiratory therapy, speech therapy, orthopedic appliances used for support, corrective orthopedic surgery, and medicationsincluding corticosteroids, anticonvulsants (seizure medications), immunosuppressants, and antibiotics. Some individuals may need assisted ventilation to treat respiratory muscle weaknessor a pacemaker for cardiac (heart)abnormalities.	['DOID:9884', 'GARD:0007922', 'ICD10CM:G71.0', 'ICD9:359.1', 'MEDGEN:44527', 'MESH:D009136', 'MedDRA:10028356', 'NANDO:1200486', 'NANDO:2100233', 'NCIT:C84910', 'Orphanet:98473', 'SCTID:73297009', 'UMLS:C0026850', 'icd11.foundation:1464662404']	None	None	None	None	None	None	None	None	None	None	['disease_grouping', 'doid_rare', 'gard_rare', 'ncit_rare', 'ordo_group_of_disorders', 'otar', 'rare']	phenio_nodes	phenio_nodes	None	None	None	None	None	None	None	MONDO	None	None	0	None	None	None	None	201	http://purl.obolibrary.org/obo/MONDO_0020121	None	[]	None	[]	[{'id': 'Orphanet:98473', 'url': 'https://www.orpha.net/en/disease/detail/98473'}, {'id': 'NCIT:C84910', 'url': 'http://purl.obolibrary.org/obo/NCIT_C84910'}, {'id': 'icd11.foundation:1464662404', 'url': None}, {'id': 'MEDGEN:44527', 'url': 'http://identifiers.org/medgen/44527'}, {'id': 'UMLS:C0026850', 'url': 'http://identifiers.org/umls/C0026850'}, {'id': 'MESH:D009136', 'url': 'http://identifiers.org/mesh/D009136'}, {'id': 'DOID:9884', 'url': 'http://purl.obolibrary.org/obo/DOID_9884'}, {'id': 'ICD10CM:G71.0', 'url': 'https://www.icd10data.com/search?s=G71.0'}, {'id': 'SCTID:73297009', 'url': 'http://identifiers.org/snomedct/73297009'}]	[{'id': 'DOID:9884', 'url': 'http://purl.obolibrary.org/obo/DOID_9884'}, {'id': 'GARD:0007922', 'url': 'https://rarediseases.info.nih.gov/diseases/0007922/index'}, {'id': 'ICD10CM:G71.0', 'url': 'https://www.icd10data.com/search?s=G71.0'}, {'id': 'ICD9:359.1', 'url': None}, {'id': 'MEDGEN:44527', 'url': 'http://identifiers.org/medgen/44527'}, {'id': 'MESH:D009136', 'url': 'http://identifiers.org/mesh/D009136'}, {'id': 'MedDRA:10028356', 'url': None}, {'id': 'NANDO:1200486', 'url': 'http://identifiers.org/NANDO:1200486'}, {'id': 'NANDO:2100233', 'url': 'http://identifiers.org/NANDO:2100233'}, {'id': 'NCIT:C84910', 'url': 'http://purl.obolibrary.org/obo/NCIT_C84910'}, {'id': 'Orphanet:98473', 'url': 'https://www.orpha.net/en/disease/detail/98473'}, {'id': 'SCTID:73297009', 'url': 'http://identifiers.org/snomedct/73297009'}, {'id': 'UMLS:C0026850', 'url': 'http://identifiers.org/umls/C0026850'}, {'id': 'icd11.foundation:1464662404', 'url': None}]	{'id': 'phenio', 'url': 'https://monarch-app.monarchinitiative.org/Sources/phenio/'}	[{'label': 'Disease Model', 'count': 246, 'category': 'biolink:GenotypeToDiseaseAssociation', 'count_direct': 14, 'count_with_orthologs': None}, {'label': 'Disease to Phenotype', 'count': 4247, 'category': 'biolink:DiseaseToPhenotypicFeatureAssociation', 'count_direct': 0, 'count_with_orthologs': None}, {'label': 'Causal Gene', 'count': 133, 'category': 'biolink:CausalGeneToDiseaseAssociation', 'count_direct': 0, 'count_with_orthologs': None}, {'label': 'Correlated Gene', 'count': 156, 'category': 'biolink:CorrelatedGeneToDiseaseAssociation', 'count_direct': 0, 'count_with_orthologs': None}, {'label': 'Variant to Disease', 'count': 701, 'category': 'biolink:VariantToDiseaseAssociation', 'count_direct': 0, 'count_with_orthologs': None}, {'label': 'Medical Action', 'count': 6, 'category': 'biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation', 'count_direct': 0, 'count_with_orthologs': None}, {'label': 'Cases', 'count': 136, 'category': 'biolink:CaseToDiseaseAssociation', 'count_direct': 0, 'count_with_orthologs': None}]	None	{'super_classes': [{'id': 'MONDO:0005336', 'category': 'biolink:Disease', 'name': 'myopathy', 'description': None, 'xref': None, 'synonym': None, 'exact_synonym': None, 'broad_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'deprecated': None, 'in_taxon': None, 'in_taxon_label': None, 'iri': None, 'same_as': None, 'subsets': None, 'file_source': None, 'provided_by': None, 'full_name': None, 'symbol': None, 'has_gene': None, 'type': None, 'has_attribute': None, 'has_biological_sex': None, 'synonyms': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_count': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_descendant': None, 'has_descendant_label': None, 'has_descendant_count': None}, {'id': 'MONDO:0100546', 'category': 'biolink:Disease', 'name': 'hereditary neuromuscular disease', 'description': None, 'xref': None, 'synonym': None, 'exact_synonym': None, 'broad_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'deprecated': None, 'in_taxon': None, 'in_taxon_label': None, 'iri': None, 'same_as': None, 'subsets': None, 'file_source': None, 'provided_by': None, 'full_name': None, 'symbol': None, 'has_gene': None, 'type': None, 'has_attribute': None, 'has_biological_sex': None, 'synonyms': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_count': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_descendant': None, 'has_descendant_label': None, 'has_descendant_count': None}, {'id': 'MONDO:0700223', 'category': 'biolink:Disease', 'name': 'hereditary skeletal muscle disorder', 'description': None, 'xref': None, 'synonym': None, 'exact_synonym': None, 'broad_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'deprecated': None, 'in_taxon': None, 'in_taxon_label': None, 'iri': None, 'same_as': None, 'subsets': None, 'file_source': None, 'provided_by': None, 'full_name': None, 'symbol': None, 'has_gene': None, 'type': None, 'has_attribute': None, 'has_biological_sex': None, 'synonyms': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_count': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_descendant': None, 'has_descendant_label': None, 'has_descendant_count': None}], 'sub_classes': [{'id': 'MONDO:0008028', 'category': 'biolink:Disease', 'name': 'muscular dystrophy, Barnes type', 'description': None, 'xref': None, 'synonym': None, 'exact_synonym': None, 'broad_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'deprecated': None, 'in_taxon': None, 'in_taxon_label': None, 'iri': None, 'same_as': None, 'subsets': None, 'file_source': None, 'provided_by': None, 'full_name': None, 'symbol': None, 'has_gene': None, 'type': None, 'has_attribute': None, 'has_biological_sex': None, 'synonyms': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_count': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_descendant': None, 'has_descendant_label': None, 'has_descendant_count': None}, {'id': 'MONDO:0010675', 'category': 'biolink:Disease', 'name': 'muscular dystrophy, cardiac type', 'description': None, 'xref': None, 'synonym': None, 'exact_synonym': None, 'broad_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'deprecated': None, 'in_taxon': None, 'in_taxon_label': None, 'iri': None, 'same_as': None, 'subsets': None, 'file_source': None, 'provided_by': None, 'full_name': None, 'symbol': None, 'has_gene': None, 'type': None, 'has_attribute': None, 'has_biological_sex': None, 'synonyms': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_count': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_descendant': None, 'has_descendant_label': None, 'has_descendant_count': None}, {'id': 'MONDO:0018949', 'category': 'biolink:Disease', 'name': 'distal myopathy', 'description': None, 'xref': None, 'synonym': None, 'exact_synonym': None, 'broad_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'deprecated': None, 'in_taxon': None, 'in_taxon_label': None, 'iri': None, 'same_as': None, 'subsets': None, 'file_source': None, 'provided_by': None, 'full_name': None, 'symbol': None, 'has_gene': None, 'type': None, 'has_attribute': None, 'has_biological_sex': None, 'synonyms': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_count': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_descendant': None, 'has_descendant_label': None, 'has_descendant_count': None}, {'id': 'MONDO:0016106', 'category': 'biolink:Disease', 'name': 'progressive muscular dystrophy', 'description': None, 'xref': None, 'synonym': None, 'exact_synonym': None, 'broad_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'deprecated': None, 'in_taxon': None, 'in_taxon_label': None, 'iri': None, 'same_as': None, 'subsets': None, 'file_source': None, 'provided_by': None, 'full_name': None, 'symbol': None, 'has_gene': None, 'type': None, 'has_attribute': None, 'has_biological_sex': None, 'synonyms': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_count': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_descendant': None, 'has_descendant_label': None, 'has_descendant_count': None}, {'id': 'MONDO:0023204', 'category': 'biolink:Disease', 'name': 'Fukuda-Miyanomae-Nakata syndrome', 'description': None, 'xref': None, 'synonym': None, 'exact_synonym': None, 'broad_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'deprecated': None, 'in_taxon': None, 'in_taxon_label': None, 'iri': None, 'same_as': None, 'subsets': None, 'file_source': None, 'provided_by': None, 'full_name': None, 'symbol': None, 'has_gene': None, 'type': None, 'has_attribute': None, 'has_biological_sex': None, 'synonyms': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_count': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_descendant': None, 'has_descendant_label': None, 'has_descendant_count': None}, {'id': 'MONDO:0019950', 'category': 'biolink:Disease', 'name': 'congenital muscular dystrophy', 'description': None, 'xref': None, 'synonym': None, 'exact_synonym': None, 'broad_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'deprecated': None, 'in_taxon': None, 'in_taxon_label': None, 'iri': None, 'same_as': None, 'subsets': None, 'file_source': None, 'provided_by': None, 'full_name': None, 'symbol': None, 'has_gene': None, 'type': None, 'has_attribute': None, 'has_biological_sex': None, 'synonyms': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_count': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_descendant': None, 'has_descendant_label': None, 'has_descendant_count': None}, {'id': 'MONDO:0700285', 'category': 'biolink:Disease', 'name': 'DMD-related muscular dystrophy', 'description': None, 'xref': None, 'synonym': None, 'exact_synonym': None, 'broad_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'deprecated': None, 'in_taxon': None, 'in_taxon_label': None, 'iri': None, 'same_as': None, 'subsets': None, 'file_source': None, 'provided_by': None, 'full_name': None, 'symbol': None, 'has_gene': None, 'type': None, 'has_attribute': None, 'has_biological_sex': None, 'synonyms': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_count': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_descendant': None, 'has_descendant_label': None, 'has_descendant_count': None}, {'id': 'MONDO:0010676', 'category': 'biolink:Disease', 'name': 'muscular dystrophy, Hemizygous lethal type', 'description': None, 'xref': None, 'synonym': None, 'exact_synonym': None, 'broad_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'deprecated': None, 'in_taxon': None, 'in_taxon_label': None, 'iri': None, 'same_as': None, 'subsets': None, 'file_source': None, 'provided_by': None, 'full_name': None, 'symbol': None, 'has_gene': None, 'type': None, 'has_attribute': None, 'has_biological_sex': None, 'synonyms': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_count': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_descendant': None, 'has_descendant_label': None, 'has_descendant_count': None}, {'id': 'MONDO:0010677', 'category': 'biolink:Disease', 'name': 'muscular dystrophy, Mabry type', 'description': None, 'xref': None, 'synonym': None, 'exact_synonym': None, 'broad_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'deprecated': None, 'in_taxon': None, 'in_taxon_label': None, 'iri': None, 'same_as': None, 'subsets': None, 'file_source': None, 'provided_by': None, 'full_name': None, 'symbol': None, 'has_gene': None, 'type': None, 'has_attribute': None, 'has_biological_sex': None, 'synonyms': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_count': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_descendant': None, 'has_descendant_label': None, 'has_descendant_count': None}, {'id': 'MONDO:0010678', 'category': 'biolink:Disease', 'name': 'muscular dystrophy, progressive Pectorodorsal', 'description': None, 'xref': None, 'synonym': None, 'exact_synonym': None, 'broad_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'deprecated': None, 'in_taxon': None, 'in_taxon_label': None, 'iri': None, 'same_as': None, 'subsets': None, 'file_source': None, 'provided_by': None, 'full_name': None, 'symbol': None, 'has_gene': None, 'type': None, 'has_attribute': None, 'has_biological_sex': None, 'synonyms': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_count': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_descendant': None, 'has_descendant_label': None, 'has_descendant_count': None}, {'id': 'MONDO:0100228', 'category': 'biolink:Disease', 'name': 'LAMA2-related muscular dystrophy', 'description': None, 'xref': None, 'synonym': None, 'exact_synonym': None, 'broad_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'deprecated': None, 'in_taxon': None, 'in_taxon_label': None, 'iri': None, 'same_as': None, 'subsets': None, 'file_source': None, 'provided_by': None, 'full_name': None, 'symbol': None, 'has_gene': None, 'type': None, 'has_attribute': None, 'has_biological_sex': None, 'synonyms': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_count': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_descendant': None, 'has_descendant_label': None, 'has_descendant_count': None}]}
"""

@pytest.fixture
def node_yaml():
    return """
association_counts:
- category: biolink:GenotypeToDiseaseAssociation
  count: 246
  count_direct: 14
  count_with_orthologs: null
  label: Disease Model
- category: biolink:DiseaseToPhenotypicFeatureAssociation
  count: 4247
  count_direct: 0
  count_with_orthologs: null
  label: Disease to Phenotype
- category: biolink:CausalGeneToDiseaseAssociation
  count: 133
  count_direct: 0
  count_with_orthologs: null
  label: Causal Gene
- category: biolink:CorrelatedGeneToDiseaseAssociation
  count: 156
  count_direct: 0
  count_with_orthologs: null
  label: Correlated Gene
- category: biolink:VariantToDiseaseAssociation
  count: 701
  count_direct: 0
  count_with_orthologs: null
  label: Variant to Disease
- category: biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation
  count: 6
  count_direct: 0
  count_with_orthologs: null
  label: Medical Action
- category: biolink:CaseToDiseaseAssociation
  count: 136
  count_direct: 0
  count_with_orthologs: null
  label: Cases
broad_synonym: null
category: biolink:Disease
causal_gene: []
causes_disease: null
cross_species_term_clique: null
deprecated: null
description: Muscular dystrophy (MD) refers to a group of more than 30 genetic diseases
  characterized by progressive weakness and degeneration of the skeletal muscles that
  control movement. Some forms of MD are seen in newborns, infants or children, while
  others have late-onset and may not appear until middle age or later. The disorders
  differ in terms of the distribution and extent of muscle weakness (some forms of
  MD also affect cardiac muscle), age of onset, rate of progression, and pattern of
  inheritance. The prognosis for people with MD varies according to the type and progression
  of the disorder. There is no specific treatment to stop or reverse any form of MD.
  Treatment is supportive and may include physical therapy, respiratory therapy, speech
  therapy, orthopedic appliances used for support, corrective orthopedic surgery,
  and medicationsincluding corticosteroids, anticonvulsants (seizure medications),
  immunosuppressants, and antibiotics. Some individuals may need assisted ventilation
  to treat respiratory muscle weaknessor a pacemaker for cardiac (heart)abnormalities.
exact_synonym: null
external_links:
- id: DOID:9884
  url: http://purl.obolibrary.org/obo/DOID_9884
- id: GARD:0007922
  url: https://rarediseases.info.nih.gov/diseases/0007922/index
- id: ICD10CM:G71.0
  url: https://www.icd10data.com/search?s=G71.0
- id: ICD9:359.1
  url: null
- id: MEDGEN:44527
  url: http://identifiers.org/medgen/44527
- id: MESH:D009136
  url: http://identifiers.org/mesh/D009136
- id: MedDRA:10028356
  url: null
- id: NANDO:1200486
  url: http://identifiers.org/NANDO:1200486
- id: NANDO:2100233
  url: http://identifiers.org/NANDO:2100233
- id: NCIT:C84910
  url: http://purl.obolibrary.org/obo/NCIT_C84910
- id: Orphanet:98473
  url: https://www.orpha.net/en/disease/detail/98473
- id: SCTID:73297009
  url: http://identifiers.org/snomedct/73297009
- id: UMLS:C0026850
  url: http://identifiers.org/umls/C0026850
- id: icd11.foundation:1464662404
  url: null
file_source: phenio_nodes
full_name: null
has_attribute: null
has_biological_sex: null
has_descendant: null
has_descendant_count: 201
has_descendant_label: null
has_gene: null
has_phenotype: null
has_phenotype_closure: null
has_phenotype_closure_label: null
has_phenotype_count: 0
has_phenotype_label: null
id: MONDO:0020121
in_taxon: null
in_taxon_label: null
inheritance: null
iri: null
mappings:
- id: Orphanet:98473
  url: https://www.orpha.net/en/disease/detail/98473
- id: NCIT:C84910
  url: http://purl.obolibrary.org/obo/NCIT_C84910
- id: icd11.foundation:1464662404
  url: null
- id: MEDGEN:44527
  url: http://identifiers.org/medgen/44527
- id: UMLS:C0026850
  url: http://identifiers.org/umls/C0026850
- id: MESH:D009136
  url: http://identifiers.org/mesh/D009136
- id: DOID:9884
  url: http://purl.obolibrary.org/obo/DOID_9884
- id: ICD10CM:G71.0
  url: https://www.icd10data.com/search?s=G71.0
- id: SCTID:73297009
  url: http://identifiers.org/snomedct/73297009
name: muscular dystrophy
namespace: MONDO
narrow_synonym: null
node_hierarchy:
  sub_classes:
  - broad_synonym: null
    category: biolink:Disease
    deprecated: null
    description: null
    exact_synonym: null
    file_source: null
    full_name: null
    has_attribute: null
    has_biological_sex: null
    has_descendant: null
    has_descendant_count: null
    has_descendant_label: null
    has_gene: null
    has_phenotype: null
    has_phenotype_closure: null
    has_phenotype_closure_label: null
    has_phenotype_count: null
    has_phenotype_label: null
    id: MONDO:0008028
    in_taxon: null
    in_taxon_label: null
    iri: null
    name: muscular dystrophy, Barnes type
    namespace: null
    narrow_synonym: null
    provided_by: null
    related_synonym: null
    same_as: null
    subsets: null
    symbol: null
    synonym: null
    synonyms: null
    type: null
    xref: null
  - broad_synonym: null
    category: biolink:Disease
    deprecated: null
    description: null
    exact_synonym: null
    file_source: null
    full_name: null
    has_attribute: null
    has_biological_sex: null
    has_descendant: null
    has_descendant_count: null
    has_descendant_label: null
    has_gene: null
    has_phenotype: null
    has_phenotype_closure: null
    has_phenotype_closure_label: null
    has_phenotype_count: null
    has_phenotype_label: null
    id: MONDO:0010675
    in_taxon: null
    in_taxon_label: null
    iri: null
    name: muscular dystrophy, cardiac type
    namespace: null
    narrow_synonym: null
    provided_by: null
    related_synonym: null
    same_as: null
    subsets: null
    symbol: null
    synonym: null
    synonyms: null
    type: null
    xref: null
  - broad_synonym: null
    category: biolink:Disease
    deprecated: null
    description: null
    exact_synonym: null
    file_source: null
    full_name: null
    has_attribute: null
    has_biological_sex: null
    has_descendant: null
    has_descendant_count: null
    has_descendant_label: null
    has_gene: null
    has_phenotype: null
    has_phenotype_closure: null
    has_phenotype_closure_label: null
    has_phenotype_count: null
    has_phenotype_label: null
    id: MONDO:0018949
    in_taxon: null
    in_taxon_label: null
    iri: null
    name: distal myopathy
    namespace: null
    narrow_synonym: null
    provided_by: null
    related_synonym: null
    same_as: null
    subsets: null
    symbol: null
    synonym: null
    synonyms: null
    type: null
    xref: null
  - broad_synonym: null
    category: biolink:Disease
    deprecated: null
    description: null
    exact_synonym: null
    file_source: null
    full_name: null
    has_attribute: null
    has_biological_sex: null
    has_descendant: null
    has_descendant_count: null
    has_descendant_label: null
    has_gene: null
    has_phenotype: null
    has_phenotype_closure: null
    has_phenotype_closure_label: null
    has_phenotype_count: null
    has_phenotype_label: null
    id: MONDO:0016106
    in_taxon: null
    in_taxon_label: null
    iri: null
    name: progressive muscular dystrophy
    namespace: null
    narrow_synonym: null
    provided_by: null
    related_synonym: null
    same_as: null
    subsets: null
    symbol: null
    synonym: null
    synonyms: null
    type: null
    xref: null
  - broad_synonym: null
    category: biolink:Disease
    deprecated: null
    description: null
    exact_synonym: null
    file_source: null
    full_name: null
    has_attribute: null
    has_biological_sex: null
    has_descendant: null
    has_descendant_count: null
    has_descendant_label: null
    has_gene: null
    has_phenotype: null
    has_phenotype_closure: null
    has_phenotype_closure_label: null
    has_phenotype_count: null
    has_phenotype_label: null
    id: MONDO:0023204
    in_taxon: null
    in_taxon_label: null
    iri: null
    name: Fukuda-Miyanomae-Nakata syndrome
    namespace: null
    narrow_synonym: null
    provided_by: null
    related_synonym: null
    same_as: null
    subsets: null
    symbol: null
    synonym: null
    synonyms: null
    type: null
    xref: null
  - broad_synonym: null
    category: biolink:Disease
    deprecated: null
    description: null
    exact_synonym: null
    file_source: null
    full_name: null
    has_attribute: null
    has_biological_sex: null
    has_descendant: null
    has_descendant_count: null
    has_descendant_label: null
    has_gene: null
    has_phenotype: null
    has_phenotype_closure: null
    has_phenotype_closure_label: null
    has_phenotype_count: null
    has_phenotype_label: null
    id: MONDO:0019950
    in_taxon: null
    in_taxon_label: null
    iri: null
    name: congenital muscular dystrophy
    namespace: null
    narrow_synonym: null
    provided_by: null
    related_synonym: null
    same_as: null
    subsets: null
    symbol: null
    synonym: null
    synonyms: null
    type: null
    xref: null
  - broad_synonym: null
    category: biolink:Disease
    deprecated: null
    description: null
    exact_synonym: null
    file_source: null
    full_name: null
    has_attribute: null
    has_biological_sex: null
    has_descendant: null
    has_descendant_count: null
    has_descendant_label: null
    has_gene: null
    has_phenotype: null
    has_phenotype_closure: null
    has_phenotype_closure_label: null
    has_phenotype_count: null
    has_phenotype_label: null
    id: MONDO:0700285
    in_taxon: null
    in_taxon_label: null
    iri: null
    name: DMD-related muscular dystrophy
    namespace: null
    narrow_synonym: null
    provided_by: null
    related_synonym: null
    same_as: null
    subsets: null
    symbol: null
    synonym: null
    synonyms: null
    type: null
    xref: null
  - broad_synonym: null
    category: biolink:Disease
    deprecated: null
    description: null
    exact_synonym: null
    file_source: null
    full_name: null
    has_attribute: null
    has_biological_sex: null
    has_descendant: null
    has_descendant_count: null
    has_descendant_label: null
    has_gene: null
    has_phenotype: null
    has_phenotype_closure: null
    has_phenotype_closure_label: null
    has_phenotype_count: null
    has_phenotype_label: null
    id: MONDO:0010676
    in_taxon: null
    in_taxon_label: null
    iri: null
    name: muscular dystrophy, Hemizygous lethal type
    namespace: null
    narrow_synonym: null
    provided_by: null
    related_synonym: null
    same_as: null
    subsets: null
    symbol: null
    synonym: null
    synonyms: null
    type: null
    xref: null
  - broad_synonym: null
    category: biolink:Disease
    deprecated: null
    description: null
    exact_synonym: null
    file_source: null
    full_name: null
    has_attribute: null
    has_biological_sex: null
    has_descendant: null
    has_descendant_count: null
    has_descendant_label: null
    has_gene: null
    has_phenotype: null
    has_phenotype_closure: null
    has_phenotype_closure_label: null
    has_phenotype_count: null
    has_phenotype_label: null
    id: MONDO:0010677
    in_taxon: null
    in_taxon_label: null
    iri: null
    name: muscular dystrophy, Mabry type
    namespace: null
    narrow_synonym: null
    provided_by: null
    related_synonym: null
    same_as: null
    subsets: null
    symbol: null
    synonym: null
    synonyms: null
    type: null
    xref: null
  - broad_synonym: null
    category: biolink:Disease
    deprecated: null
    description: null
    exact_synonym: null
    file_source: null
    full_name: null
    has_attribute: null
    has_biological_sex: null
    has_descendant: null
    has_descendant_count: null
    has_descendant_label: null
    has_gene: null
    has_phenotype: null
    has_phenotype_closure: null
    has_phenotype_closure_label: null
    has_phenotype_count: null
    has_phenotype_label: null
    id: MONDO:0010678
    in_taxon: null
    in_taxon_label: null
    iri: null
    name: muscular dystrophy, progressive Pectorodorsal
    namespace: null
    narrow_synonym: null
    provided_by: null
    related_synonym: null
    same_as: null
    subsets: null
    symbol: null
    synonym: null
    synonyms: null
    type: null
    xref: null
  - broad_synonym: null
    category: biolink:Disease
    deprecated: null
    description: null
    exact_synonym: null
    file_source: null
    full_name: null
    has_attribute: null
    has_biological_sex: null
    has_descendant: null
    has_descendant_count: null
    has_descendant_label: null
    has_gene: null
    has_phenotype: null
    has_phenotype_closure: null
    has_phenotype_closure_label: null
    has_phenotype_count: null
    has_phenotype_label: null
    id: MONDO:0100228
    in_taxon: null
    in_taxon_label: null
    iri: null
    name: LAMA2-related muscular dystrophy
    namespace: null
    narrow_synonym: null
    provided_by: null
    related_synonym: null
    same_as: null
    subsets: null
    symbol: null
    synonym: null
    synonyms: null
    type: null
    xref: null
  super_classes:
  - broad_synonym: null
    category: biolink:Disease
    deprecated: null
    description: null
    exact_synonym: null
    file_source: null
    full_name: null
    has_attribute: null
    has_biological_sex: null
    has_descendant: null
    has_descendant_count: null
    has_descendant_label: null
    has_gene: null
    has_phenotype: null
    has_phenotype_closure: null
    has_phenotype_closure_label: null
    has_phenotype_count: null
    has_phenotype_label: null
    id: MONDO:0005336
    in_taxon: null
    in_taxon_label: null
    iri: null
    name: myopathy
    namespace: null
    narrow_synonym: null
    provided_by: null
    related_synonym: null
    same_as: null
    subsets: null
    symbol: null
    synonym: null
    synonyms: null
    type: null
    xref: null
  - broad_synonym: null
    category: biolink:Disease
    deprecated: null
    description: null
    exact_synonym: null
    file_source: null
    full_name: null
    has_attribute: null
    has_biological_sex: null
    has_descendant: null
    has_descendant_count: null
    has_descendant_label: null
    has_gene: null
    has_phenotype: null
    has_phenotype_closure: null
    has_phenotype_closure_label: null
    has_phenotype_count: null
    has_phenotype_label: null
    id: MONDO:0100546
    in_taxon: null
    in_taxon_label: null
    iri: null
    name: hereditary neuromuscular disease
    namespace: null
    narrow_synonym: null
    provided_by: null
    related_synonym: null
    same_as: null
    subsets: null
    symbol: null
    synonym: null
    synonyms: null
    type: null
    xref: null
  - broad_synonym: null
    category: biolink:Disease
    deprecated: null
    description: null
    exact_synonym: null
    file_source: null
    full_name: null
    has_attribute: null
    has_biological_sex: null
    has_descendant: null
    has_descendant_count: null
    has_descendant_label: null
    has_gene: null
    has_phenotype: null
    has_phenotype_closure: null
    has_phenotype_closure_label: null
    has_phenotype_count: null
    has_phenotype_label: null
    id: MONDO:0700223
    in_taxon: null
    in_taxon_label: null
    iri: null
    name: hereditary skeletal muscle disorder
    namespace: null
    narrow_synonym: null
    provided_by: null
    related_synonym: null
    same_as: null
    subsets: null
    symbol: null
    synonym: null
    synonyms: null
    type: null
    xref: null
node_relationships: []
provided_by: phenio_nodes
provided_by_link:
  id: phenio
  url: https://monarch-app.monarchinitiative.org/Sources/phenio/
related_synonym: null
same_as: null
subsets:
- disease_grouping
- doid_rare
- gard_rare
- ncit_rare
- ordo_group_of_disorders
- otar
- rare
symbol: null
synonym: null
synonyms: null
type: null
uri: http://purl.obolibrary.org/obo/MONDO_0020121
xref:
- DOID:9884
- GARD:0007922
- ICD10CM:G71.0
- ICD9:359.1
- MEDGEN:44527
- MESH:D009136
- MedDRA:10028356
- NANDO:1200486
- NANDO:2100233
- NCIT:C84910
- Orphanet:98473
- SCTID:73297009
- UMLS:C0026850
- icd11.foundation:1464662404

"""
