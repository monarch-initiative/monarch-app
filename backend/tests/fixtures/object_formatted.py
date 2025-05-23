import pytest


@pytest.fixture
def node_json():
    return """
{
    "id": "MONDO:0020121",
    "category": "biolink:Disease",
    "name": "muscular dystrophy",
    "full_name": null,
    "deprecated": null,
    "description": "Muscular dystrophy (MD) refers to a group of more than 30 genetic diseases characterized by progressive weakness and degeneration of the skeletal muscles that control movement. Some forms of MD are seen in newborns, infants or children, while others have late-onset and may not appear until middle age or later. The disorders differ in terms of the distribution and extent of muscle weakness (some forms of MD also affect cardiac muscle), age of onset, rate of progression, and pattern of inheritance. The prognosis for people with MD varies according to the type and progression of the disorder. There is no specific treatment to stop or reverse any form of MD. Treatment is supportive and may include physical therapy, respiratory therapy, speech therapy, orthopedic appliances used for support, corrective orthopedic surgery, and medicationsincluding corticosteroids, anticonvulsants (seizure medications), immunosuppressants, and antibiotics. Some individuals may need assisted ventilation to treat respiratory muscle weaknessor a pacemaker for cardiac (heart)abnormalities.",
    "xref": [
        "DOID:9884",
        "GARD:7922",
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
    "provided_by": "phenio_nodes",
    "in_taxon": null,
    "in_taxon_label": null,
    "symbol": null,
    "synonym": null,
    "broad_synonym": null,
    "exact_synonym": null,
    "narrow_synonym": null,
    "related_synonym": null,
    "subsets": [
        "disease_grouping",
        "gard_rare",
        "ordo_group_of_disorders",
        "otar",
        "rare"
    ],
    "uri": "http://purl.obolibrary.org/obo/MONDO_0020121",
    "iri": null,
    "namespace": "MONDO",
    "has_phenotype": null,
    "has_phenotype_label": null,
    "has_phenotype_closure": null,
    "has_phenotype_closure_label": null,
    "has_phenotype_count": 0,
    "inheritance": null,
    "causal_gene": [],
    "causes_disease": null,
    "mappings": [
        {
            "id": "DOID:9884",
            "url": "http://purl.obolibrary.org/obo/DOID_9884"
        },
        {
            "id": "ICD10CM:G71.0",
            "url": "https://icd.codes/icd10cm/G71.0"
        },
        {
            "id": "MEDGEN:44527",
            "url": "http://identifiers.org/medgen/44527"
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
        },
        {
            "id": "MESH:D009136",
            "url": "http://identifiers.org/mesh/D009136"
        }
    ],
    "external_links": [
        {
            "id": "DOID:9884",
            "url": "http://purl.obolibrary.org/obo/DOID_9884"
        },
        {
            "id": "GARD:7922",
            "url": "https://rarediseases.info.nih.gov/diseases/7922/index"
        },
        {
            "id": "ICD10CM:G71.0",
            "url": "https://icd.codes/icd10cm/G71.0"
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
            "url": "http://identifiers.org/NANDO/1200486"
        },
        {
            "id": "NANDO:2100233",
            "url": "http://identifiers.org/NANDO/2100233"
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
        "url": "https://monarch-initiative.github.io/monarch-ingest/Sources/phenio/#"
    },
    "association_counts": [
        {
            "label": "Disease to Phenotype",
            "count": 4192,
            "category": "biolink:DiseaseToPhenotypicFeatureAssociation"
        },
        {
            "label": "Gene to Phenotype",
            "count": 6475,
            "category": "biolink:GeneToPhenotypicFeatureAssociation"
        },
        {
            "label": "Causal Gene",
            "count": 126,
            "category": "biolink:CausalGeneToDiseaseAssociation"
        },
        {
            "label": "Correlated Gene",
            "count": 149,
            "category": "biolink:CorrelatedGeneToDiseaseAssociation"
        },
        {
            "label": "Variant to Disease",
            "count": 211,
            "category": "biolink:VariantToDiseaseAssociation"
        },
        {
            "label": "Disease Model",
            "count": 242,
            "category": "biolink:GenotypeToDiseaseAssociation"
        },
        {
            "label": "Medical Action",
            "count": 4,
            "category": "biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation"
        }
    ],
    "node_hierarchy": {
        "super_classes": [
            {
                "id": "MONDO:0005336",
                "category": "biolink:Disease",
                "name": "myopathy",
                "full_name": null,
                "deprecated": null,
                "description": null,
                "xref": null,
                "provided_by": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "symbol": null,
                "synonym": null,
                "broad_synonym": null,
                "exact_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "subsets": null,
                "uri": null,
                "iri": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_phenotype_count": null
            },
            {
                "id": "MONDO:0100546",
                "category": "biolink:Disease",
                "name": "hereditary neuromuscular disease",
                "full_name": null,
                "deprecated": null,
                "description": null,
                "xref": null,
                "provided_by": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "symbol": null,
                "synonym": null,
                "broad_synonym": null,
                "exact_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "subsets": null,
                "uri": null,
                "iri": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_phenotype_count": null
            },
            {
                "id": "MONDO:0700223",
                "category": "biolink:Disease",
                "name": "hereditary skeletal muscle disorder",
                "full_name": null,
                "deprecated": null,
                "description": null,
                "xref": null,
                "provided_by": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "symbol": null,
                "synonym": null,
                "broad_synonym": null,
                "exact_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "subsets": null,
                "uri": null,
                "iri": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_phenotype_count": null
            }
        ],
        "sub_classes": [
            {
                "id": "MONDO:0010675",
                "category": "biolink:Disease",
                "name": "muscular dystrophy, cardiac type",
                "full_name": null,
                "deprecated": null,
                "description": null,
                "xref": null,
                "provided_by": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "symbol": null,
                "synonym": null,
                "broad_synonym": null,
                "exact_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "subsets": null,
                "uri": null,
                "iri": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_phenotype_count": null
            },
            {
                "id": "MONDO:0010676",
                "category": "biolink:Disease",
                "name": "muscular dystrophy, Hemizygous lethal type",
                "full_name": null,
                "deprecated": null,
                "description": null,
                "xref": null,
                "provided_by": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "symbol": null,
                "synonym": null,
                "broad_synonym": null,
                "exact_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "subsets": null,
                "uri": null,
                "iri": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_phenotype_count": null
            },
            {
                "id": "MONDO:0010677",
                "category": "biolink:Disease",
                "name": "muscular dystrophy, Mabry type",
                "full_name": null,
                "deprecated": null,
                "description": null,
                "xref": null,
                "provided_by": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "symbol": null,
                "synonym": null,
                "broad_synonym": null,
                "exact_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "subsets": null,
                "uri": null,
                "iri": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_phenotype_count": null
            },
            {
                "id": "MONDO:0010678",
                "category": "biolink:Disease",
                "name": "muscular dystrophy, progressive Pectorodorsal",
                "full_name": null,
                "deprecated": null,
                "description": null,
                "xref": null,
                "provided_by": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "symbol": null,
                "synonym": null,
                "broad_synonym": null,
                "exact_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "subsets": null,
                "uri": null,
                "iri": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_phenotype_count": null
            },
            {
                "id": "MONDO:0008028",
                "category": "biolink:Disease",
                "name": "muscular dystrophy, Barnes type",
                "full_name": null,
                "deprecated": null,
                "description": null,
                "xref": null,
                "provided_by": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "symbol": null,
                "synonym": null,
                "broad_synonym": null,
                "exact_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "subsets": null,
                "uri": null,
                "iri": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_phenotype_count": null
            },
            {
                "id": "MONDO:0016106",
                "category": "biolink:Disease",
                "name": "progressive muscular dystrophy",
                "full_name": null,
                "deprecated": null,
                "description": null,
                "xref": null,
                "provided_by": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "symbol": null,
                "synonym": null,
                "broad_synonym": null,
                "exact_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "subsets": null,
                "uri": null,
                "iri": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_phenotype_count": null
            },
            {
                "id": "MONDO:0018949",
                "category": "biolink:Disease",
                "name": "distal myopathy",
                "full_name": null,
                "deprecated": null,
                "description": null,
                "xref": null,
                "provided_by": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "symbol": null,
                "synonym": null,
                "broad_synonym": null,
                "exact_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "subsets": null,
                "uri": null,
                "iri": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_phenotype_count": null
            },
            {
                "id": "MONDO:0019950",
                "category": "biolink:Disease",
                "name": "congenital muscular dystrophy",
                "full_name": null,
                "deprecated": null,
                "description": null,
                "xref": null,
                "provided_by": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "symbol": null,
                "synonym": null,
                "broad_synonym": null,
                "exact_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "subsets": null,
                "uri": null,
                "iri": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_phenotype_count": null
            },
            {
                "id": "MONDO:0023204",
                "category": "biolink:Disease",
                "name": "Fukuda-Miyanomae-Nakata syndrome",
                "full_name": null,
                "deprecated": null,
                "description": null,
                "xref": null,
                "provided_by": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "symbol": null,
                "synonym": null,
                "broad_synonym": null,
                "exact_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "subsets": null,
                "uri": null,
                "iri": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_phenotype_count": null
            },
            {
                "id": "MONDO:0100228",
                "category": "biolink:Disease",
                "name": "LAMA2-related muscular dystrophy",
                "full_name": null,
                "deprecated": null,
                "description": null,
                "xref": null,
                "provided_by": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "symbol": null,
                "synonym": null,
                "broad_synonym": null,
                "exact_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "subsets": null,
                "uri": null,
                "iri": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_phenotype_count": null
            },
            {
                "id": "MONDO:0700285",
                "category": "biolink:Disease",
                "name": "DMD-related muscular dystrophy",
                "full_name": null,
                "deprecated": null,
                "description": null,
                "xref": null,
                "provided_by": null,
                "in_taxon": null,
                "in_taxon_label": null,
                "symbol": null,
                "synonym": null,
                "broad_synonym": null,
                "exact_synonym": null,
                "narrow_synonym": null,
                "related_synonym": null,
                "subsets": null,
                "uri": null,
                "iri": null,
                "namespace": null,
                "has_phenotype": null,
                "has_phenotype_label": null,
                "has_phenotype_closure": null,
                "has_phenotype_closure_label": null,
                "has_phenotype_count": null
            }
        ]
    }
}
"""


@pytest.fixture
def node_tsv():
    return """
id	category	name	full_name	deprecated	description	xref	provided_by	in_taxon	in_taxon_label	symbol	synonym	broad_synonym	exact_synonym	narrow_synonym	related_synonym	subsets	uri	iri	namespace	has_phenotype	has_phenotype_label	has_phenotype_closure	has_phenotype_closure_label	has_phenotype_count	inheritance	causal_gene	causes_disease	mappings	external_links	provided_by_link	association_counts	node_hierarchy
MONDO:0020121	biolink:Disease	muscular dystrophy	None	None	Muscular dystrophy (MD) refers to a group of more than 30 genetic diseases characterized by progressive weakness and degeneration of the skeletal muscles that control movement. Some forms of MD are seen in newborns, infants or children, while others have late-onset and may not appear until middle age or later. The disorders differ in terms of the distribution and extent of muscle weakness (some forms of MD also affect cardiac muscle), age of onset, rate of progression, and pattern of inheritance. The prognosis for people with MD varies according to the type and progression of the disorder. There is no specific treatment to stop or reverse any form of MD. Treatment is supportive and may include physical therapy, respiratory therapy, speech therapy, orthopedic appliances used for support, corrective orthopedic surgery, and medicationsincluding corticosteroids, anticonvulsants (seizure medications), immunosuppressants, and antibiotics. Some individuals may need assisted ventilation to treat respiratory muscle weaknessor a pacemaker for cardiac (heart)abnormalities.	['DOID:9884', 'GARD:7922', 'ICD10CM:G71.0', 'ICD9:359.1', 'MEDGEN:44527', 'MESH:D009136', 'MedDRA:10028356', 'NANDO:1200486', 'NANDO:2100233', 'NCIT:C84910', 'Orphanet:98473', 'SCTID:73297009', 'UMLS:C0026850', 'icd11.foundation:1464662404']	phenio_nodes	None	None	None	None	None	None	None	None	['disease_grouping', 'gard_rare', 'ordo_group_of_disorders', 'otar', 'rare']	http://purl.obolibrary.org/obo/MONDO_0020121	None	MONDO	None	None	None	None	0	None	[]	None	[{'id': 'DOID:9884', 'url': 'http://purl.obolibrary.org/obo/DOID_9884'}, {'id': 'ICD10CM:G71.0', 'url': 'https://icd.codes/icd10cm/G71.0'}, {'id': 'MEDGEN:44527', 'url': 'http://identifiers.org/medgen/44527'}, {'id': 'NCIT:C84910', 'url': 'http://purl.obolibrary.org/obo/NCIT_C84910'}, {'id': 'Orphanet:98473', 'url': 'https://www.orpha.net/en/disease/detail/98473'}, {'id': 'SCTID:73297009', 'url': 'http://identifiers.org/snomedct/73297009'}, {'id': 'UMLS:C0026850', 'url': 'http://identifiers.org/umls/C0026850'}, {'id': 'icd11.foundation:1464662404', 'url': None}, {'id': 'MESH:D009136', 'url': 'http://identifiers.org/mesh/D009136'}]	[{'id': 'DOID:9884', 'url': 'http://purl.obolibrary.org/obo/DOID_9884'}, {'id': 'GARD:7922', 'url': 'https://rarediseases.info.nih.gov/diseases/7922/index'}, {'id': 'ICD10CM:G71.0', 'url': 'https://icd.codes/icd10cm/G71.0'}, {'id': 'ICD9:359.1', 'url': None}, {'id': 'MEDGEN:44527', 'url': 'http://identifiers.org/medgen/44527'}, {'id': 'MESH:D009136', 'url': 'http://identifiers.org/mesh/D009136'}, {'id': 'MedDRA:10028356', 'url': None}, {'id': 'NANDO:1200486', 'url': 'http://identifiers.org/NANDO/1200486'}, {'id': 'NANDO:2100233', 'url': 'http://identifiers.org/NANDO/2100233'}, {'id': 'NCIT:C84910', 'url': 'http://purl.obolibrary.org/obo/NCIT_C84910'}, {'id': 'Orphanet:98473', 'url': 'https://www.orpha.net/en/disease/detail/98473'}, {'id': 'SCTID:73297009', 'url': 'http://identifiers.org/snomedct/73297009'}, {'id': 'UMLS:C0026850', 'url': 'http://identifiers.org/umls/C0026850'}, {'id': 'icd11.foundation:1464662404', 'url': None}]	{'id': 'phenio', 'url': 'https://monarch-initiative.github.io/monarch-ingest/Sources/phenio/#'}	[{'label': 'Disease to Phenotype', 'count': 4192, 'category': 'biolink:DiseaseToPhenotypicFeatureAssociation'}, {'label': 'Gene to Phenotype', 'count': 6475, 'category': 'biolink:GeneToPhenotypicFeatureAssociation'}, {'label': 'Causal Gene', 'count': 126, 'category': 'biolink:CausalGeneToDiseaseAssociation'}, {'label': 'Correlated Gene', 'count': 149, 'category': 'biolink:CorrelatedGeneToDiseaseAssociation'}, {'label': 'Variant to Disease', 'count': 211, 'category': 'biolink:VariantToDiseaseAssociation'}, {'label': 'Disease Model', 'count': 242, 'category': 'biolink:GenotypeToDiseaseAssociation'}, {'label': 'Medical Action', 'count': 4, 'category': 'biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation'}]	{'super_classes': [{'id': 'MONDO:0005336', 'category': 'biolink:Disease', 'name': 'myopathy', 'full_name': None, 'deprecated': None, 'description': None, 'xref': None, 'provided_by': None, 'in_taxon': None, 'in_taxon_label': None, 'symbol': None, 'synonym': None, 'broad_synonym': None, 'exact_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'subsets': None, 'uri': None, 'iri': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_phenotype_count': None}, {'id': 'MONDO:0100546', 'category': 'biolink:Disease', 'name': 'hereditary neuromuscular disease', 'full_name': None, 'deprecated': None, 'description': None, 'xref': None, 'provided_by': None, 'in_taxon': None, 'in_taxon_label': None, 'symbol': None, 'synonym': None, 'broad_synonym': None, 'exact_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'subsets': None, 'uri': None, 'iri': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_phenotype_count': None}, {'id': 'MONDO:0700223', 'category': 'biolink:Disease', 'name': 'hereditary skeletal muscle disorder', 'full_name': None, 'deprecated': None, 'description': None, 'xref': None, 'provided_by': None, 'in_taxon': None, 'in_taxon_label': None, 'symbol': None, 'synonym': None, 'broad_synonym': None, 'exact_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'subsets': None, 'uri': None, 'iri': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_phenotype_count': None}], 'sub_classes': [{'id': 'MONDO:0010675', 'category': 'biolink:Disease', 'name': 'muscular dystrophy, cardiac type', 'full_name': None, 'deprecated': None, 'description': None, 'xref': None, 'provided_by': None, 'in_taxon': None, 'in_taxon_label': None, 'symbol': None, 'synonym': None, 'broad_synonym': None, 'exact_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'subsets': None, 'uri': None, 'iri': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_phenotype_count': None}, {'id': 'MONDO:0010676', 'category': 'biolink:Disease', 'name': 'muscular dystrophy, Hemizygous lethal type', 'full_name': None, 'deprecated': None, 'description': None, 'xref': None, 'provided_by': None, 'in_taxon': None, 'in_taxon_label': None, 'symbol': None, 'synonym': None, 'broad_synonym': None, 'exact_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'subsets': None, 'uri': None, 'iri': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_phenotype_count': None}, {'id': 'MONDO:0010677', 'category': 'biolink:Disease', 'name': 'muscular dystrophy, Mabry type', 'full_name': None, 'deprecated': None, 'description': None, 'xref': None, 'provided_by': None, 'in_taxon': None, 'in_taxon_label': None, 'symbol': None, 'synonym': None, 'broad_synonym': None, 'exact_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'subsets': None, 'uri': None, 'iri': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_phenotype_count': None}, {'id': 'MONDO:0010678', 'category': 'biolink:Disease', 'name': 'muscular dystrophy, progressive Pectorodorsal', 'full_name': None, 'deprecated': None, 'description': None, 'xref': None, 'provided_by': None, 'in_taxon': None, 'in_taxon_label': None, 'symbol': None, 'synonym': None, 'broad_synonym': None, 'exact_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'subsets': None, 'uri': None, 'iri': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_phenotype_count': None}, {'id': 'MONDO:0008028', 'category': 'biolink:Disease', 'name': 'muscular dystrophy, Barnes type', 'full_name': None, 'deprecated': None, 'description': None, 'xref': None, 'provided_by': None, 'in_taxon': None, 'in_taxon_label': None, 'symbol': None, 'synonym': None, 'broad_synonym': None, 'exact_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'subsets': None, 'uri': None, 'iri': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_phenotype_count': None}, {'id': 'MONDO:0016106', 'category': 'biolink:Disease', 'name': 'progressive muscular dystrophy', 'full_name': None, 'deprecated': None, 'description': None, 'xref': None, 'provided_by': None, 'in_taxon': None, 'in_taxon_label': None, 'symbol': None, 'synonym': None, 'broad_synonym': None, 'exact_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'subsets': None, 'uri': None, 'iri': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_phenotype_count': None}, {'id': 'MONDO:0018949', 'category': 'biolink:Disease', 'name': 'distal myopathy', 'full_name': None, 'deprecated': None, 'description': None, 'xref': None, 'provided_by': None, 'in_taxon': None, 'in_taxon_label': None, 'symbol': None, 'synonym': None, 'broad_synonym': None, 'exact_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'subsets': None, 'uri': None, 'iri': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_phenotype_count': None}, {'id': 'MONDO:0019950', 'category': 'biolink:Disease', 'name': 'congenital muscular dystrophy', 'full_name': None, 'deprecated': None, 'description': None, 'xref': None, 'provided_by': None, 'in_taxon': None, 'in_taxon_label': None, 'symbol': None, 'synonym': None, 'broad_synonym': None, 'exact_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'subsets': None, 'uri': None, 'iri': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_phenotype_count': None}, {'id': 'MONDO:0023204', 'category': 'biolink:Disease', 'name': 'Fukuda-Miyanomae-Nakata syndrome', 'full_name': None, 'deprecated': None, 'description': None, 'xref': None, 'provided_by': None, 'in_taxon': None, 'in_taxon_label': None, 'symbol': None, 'synonym': None, 'broad_synonym': None, 'exact_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'subsets': None, 'uri': None, 'iri': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_phenotype_count': None}, {'id': 'MONDO:0100228', 'category': 'biolink:Disease', 'name': 'LAMA2-related muscular dystrophy', 'full_name': None, 'deprecated': None, 'description': None, 'xref': None, 'provided_by': None, 'in_taxon': None, 'in_taxon_label': None, 'symbol': None, 'synonym': None, 'broad_synonym': None, 'exact_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'subsets': None, 'uri': None, 'iri': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_phenotype_count': None}, {'id': 'MONDO:0700285', 'category': 'biolink:Disease', 'name': 'DMD-related muscular dystrophy', 'full_name': None, 'deprecated': None, 'description': None, 'xref': None, 'provided_by': None, 'in_taxon': None, 'in_taxon_label': None, 'symbol': None, 'synonym': None, 'broad_synonym': None, 'exact_synonym': None, 'narrow_synonym': None, 'related_synonym': None, 'subsets': None, 'uri': None, 'iri': None, 'namespace': None, 'has_phenotype': None, 'has_phenotype_label': None, 'has_phenotype_closure': None, 'has_phenotype_closure_label': None, 'has_phenotype_count': None}]}
"""


@pytest.fixture
def node_yaml():
    return """
association_counts:
- category: biolink:DiseaseToPhenotypicFeatureAssociation
  count: 4192
  label: Disease to Phenotype
- category: biolink:GeneToPhenotypicFeatureAssociation
  count: 6475
  label: Gene to Phenotype
- category: biolink:CausalGeneToDiseaseAssociation
  count: 126
  label: Causal Gene
- category: biolink:CorrelatedGeneToDiseaseAssociation
  count: 149
  label: Correlated Gene
- category: biolink:VariantToDiseaseAssociation
  count: 211
  label: Variant to Disease
- category: biolink:GenotypeToDiseaseAssociation
  count: 242
  label: Disease Model
- category: biolink:ChemicalOrDrugOrTreatmentToDiseaseOrPhenotypicFeatureAssociation
  count: 4
  label: Medical Action
broad_synonym: null
category: biolink:Disease
causal_gene: []
causes_disease: null
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
- id: GARD:7922
  url: https://rarediseases.info.nih.gov/diseases/7922/index
- id: ICD10CM:G71.0
  url: https://icd.codes/icd10cm/G71.0
- id: ICD9:359.1
  url: null
- id: MEDGEN:44527
  url: http://identifiers.org/medgen/44527
- id: MESH:D009136
  url: http://identifiers.org/mesh/D009136
- id: MedDRA:10028356
  url: null
- id: NANDO:1200486
  url: http://identifiers.org/NANDO/1200486
- id: NANDO:2100233
  url: http://identifiers.org/NANDO/2100233
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
full_name: null
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
- id: DOID:9884
  url: http://purl.obolibrary.org/obo/DOID_9884
- id: ICD10CM:G71.0
  url: https://icd.codes/icd10cm/G71.0
- id: MEDGEN:44527
  url: http://identifiers.org/medgen/44527
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
- id: MESH:D009136
  url: http://identifiers.org/mesh/D009136
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
    full_name: null
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
    subsets: null
    symbol: null
    synonym: null
    uri: null
    xref: null
  - broad_synonym: null
    category: biolink:Disease
    deprecated: null
    description: null
    exact_synonym: null
    full_name: null
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
    subsets: null
    symbol: null
    synonym: null
    uri: null
    xref: null
  - broad_synonym: null
    category: biolink:Disease
    deprecated: null
    description: null
    exact_synonym: null
    full_name: null
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
    subsets: null
    symbol: null
    synonym: null
    uri: null
    xref: null
  - broad_synonym: null
    category: biolink:Disease
    deprecated: null
    description: null
    exact_synonym: null
    full_name: null
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
    subsets: null
    symbol: null
    synonym: null
    uri: null
    xref: null
  - broad_synonym: null
    category: biolink:Disease
    deprecated: null
    description: null
    exact_synonym: null
    full_name: null
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
    subsets: null
    symbol: null
    synonym: null
    uri: null
    xref: null
  - broad_synonym: null
    category: biolink:Disease
    deprecated: null
    description: null
    exact_synonym: null
    full_name: null
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
    subsets: null
    symbol: null
    synonym: null
    uri: null
    xref: null
  - broad_synonym: null
    category: biolink:Disease
    deprecated: null
    description: null
    exact_synonym: null
    full_name: null
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
    subsets: null
    symbol: null
    synonym: null
    uri: null
    xref: null
  - broad_synonym: null
    category: biolink:Disease
    deprecated: null
    description: null
    exact_synonym: null
    full_name: null
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
    subsets: null
    symbol: null
    synonym: null
    uri: null
    xref: null
  - broad_synonym: null
    category: biolink:Disease
    deprecated: null
    description: null
    exact_synonym: null
    full_name: null
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
    subsets: null
    symbol: null
    synonym: null
    uri: null
    xref: null
  - broad_synonym: null
    category: biolink:Disease
    deprecated: null
    description: null
    exact_synonym: null
    full_name: null
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
    subsets: null
    symbol: null
    synonym: null
    uri: null
    xref: null
  - broad_synonym: null
    category: biolink:Disease
    deprecated: null
    description: null
    exact_synonym: null
    full_name: null
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
    subsets: null
    symbol: null
    synonym: null
    uri: null
    xref: null
  super_classes:
  - broad_synonym: null
    category: biolink:Disease
    deprecated: null
    description: null
    exact_synonym: null
    full_name: null
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
    subsets: null
    symbol: null
    synonym: null
    uri: null
    xref: null
  - broad_synonym: null
    category: biolink:Disease
    deprecated: null
    description: null
    exact_synonym: null
    full_name: null
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
    subsets: null
    symbol: null
    synonym: null
    uri: null
    xref: null
  - broad_synonym: null
    category: biolink:Disease
    deprecated: null
    description: null
    exact_synonym: null
    full_name: null
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
    subsets: null
    symbol: null
    synonym: null
    uri: null
    xref: null
provided_by: phenio_nodes
provided_by_link:
  id: phenio
  url: https://monarch-initiative.github.io/monarch-ingest/Sources/phenio/#
related_synonym: null
subsets:
- disease_grouping
- gard_rare
- ordo_group_of_disorders
- otar
- rare
symbol: null
synonym: null
uri: http://purl.obolibrary.org/obo/MONDO_0020121
xref:
- DOID:9884
- GARD:7922
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
