import pytest


@pytest.fixture
def entity():
    return {
        "id": "MONDO:0020121",
        "category": "biolink:Disease",
        "name": "muscular dystrophy",
        "full_name": None,
        "deprecated": None,
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
            "icd11.foundation:1464662404",
        ],
        "provided_by": "phenio_nodes",
        "in_taxon": None,
        "in_taxon_label": None,
        "symbol": None,
        "synonym": None,
        "broad_synonym": None,
        "exact_synonym": None,
        "narrow_synonym": None,
        "related_synonym": None,
        "subsets": ["disease_grouping", "gard_rare", "ordo_group_of_disorders", "otar", "rare"],
        "uri": "http://purl.obolibrary.org/obo/MONDO_0020121",
        "iri": None,
        "namespace": "MONDO",
        "has_phenotype": None,
        "has_phenotype_label": None,
        "has_phenotype_closure": None,
        "has_phenotype_closure_label": None,
        "has_phenotype_count": 0,
    }
