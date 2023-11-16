import pytest


@pytest.fixture
def association_counts_response():
    return {
        "responseHeader": {
            "QTime": 2,
            "params": {
                "facet.query": [
                    '(category:"biolink:DiseaseToPhenotypicFeatureAssociation") AND (subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121")',
                    '(category:"biolink:GeneToPhenotypicFeatureAssociation") AND (subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121")',
                    '(category:"biolink:PairwiseGeneToGeneInteraction") AND (subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121")',
                    '(category:"biolink:GeneToPathwayAssociation") AND (subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121")',
                    '(category:"biolink:GeneToExpressionSiteAssociation") AND (subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121")',
                    '(category:"biolink:GeneToGeneHomologyAssociation") AND (subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121")',
                    '(category:"biolink:ChemicalToPathwayAssociation") AND (subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121")',
                    '(category:"biolink:MacromolecularMachineToMolecularActivityAssociation") AND (subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121")',
                    '(category:"biolink:MacromolecularMachineToCellularComponentAssociation") AND (subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121")',
                    '(category:"biolink:MacromolecularMachineToBiologicalProcessAssociation") AND (subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121")',
                    '(category:"biolink:CausalGeneToDiseaseAssociation") AND (subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121")',
                    '(category:"biolink:CorrelatedGeneToDiseaseAssociation") AND (subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121")',
                    '(category:"biolink:DiseaseToPhenotypicFeatureAssociation") AND (object:"MONDO:0020121" OR object_closure:"MONDO:0020121")',
                    '(category:"biolink:GeneToPhenotypicFeatureAssociation") AND (object:"MONDO:0020121" OR object_closure:"MONDO:0020121")',
                    '(category:"biolink:PairwiseGeneToGeneInteraction") AND (object:"MONDO:0020121" OR object_closure:"MONDO:0020121")',
                    '(category:"biolink:GeneToPathwayAssociation") AND (object:"MONDO:0020121" OR object_closure:"MONDO:0020121")',
                    '(category:"biolink:GeneToExpressionSiteAssociation") AND (object:"MONDO:0020121" OR object_closure:"MONDO:0020121")',
                    '(category:"biolink:GeneToGeneHomologyAssociation") AND (object:"MONDO:0020121" OR object_closure:"MONDO:0020121")',
                    '(category:"biolink:ChemicalToPathwayAssociation") AND (object:"MONDO:0020121" OR object_closure:"MONDO:0020121")',
                    '(category:"biolink:MacromolecularMachineToMolecularActivityAssociation") AND (object:"MONDO:0020121" OR object_closure:"MONDO:0020121")',
                    '(category:"biolink:MacromolecularMachineToCellularComponentAssociation") AND (object:"MONDO:0020121" OR object_closure:"MONDO:0020121")',
                    '(category:"biolink:MacromolecularMachineToBiologicalProcessAssociation") AND (object:"MONDO:0020121" OR object_closure:"MONDO:0020121")',
                    '(category:"biolink:CausalGeneToDiseaseAssociation") AND (object:"MONDO:0020121" OR object_closure:"MONDO:0020121")',
                    '(category:"biolink:CorrelatedGeneToDiseaseAssociation") AND (object:"MONDO:0020121" OR object_closure:"MONDO:0020121")',
                ],
                "mm": "100%",
                "q": "*:*",
                "defType": "edismax",
                "facet_min_count": "1",
                "start": "0",
                "q.op": "AND",
                "fq": 'subject:"MONDO\\:0020121" OR subject_closure:"MONDO\\:0020121" OR object:"MONDO\\:0020121" OR object_closure:"MONDO\\:0020121"',
                "rows": "20",
                "facet": "true",
            },
        },
        "response": {
            "num_found": 13,
            "start": 0,
            "docs": [
                {
                    "id": "urn:uuid:49869d87-15e7-4413-9734-5ede7ffe74a5",
                    "predicate": "biolink:subclass_of",
                    "category": "biolink:Association",
                    "aggregator_knowledge_source": ["infores:phenio"],
                    "primary_knowledge_source": "infores:mondo",
                    "provided_by": "phenio_edges",
                    "subject": "MONDO:0016106",
                    "object": "MONDO:0020121",
                    "subject_label": "progressive muscular dystrophy",
                    "subject_category": "biolink:Disease",
                    "subject_namespace": "MONDO",
                    "subject_closure": [
                        "[BFO:0000017, MONDO:0003847, MONDO:0003939, MONDO:0700096, MONDO:0005071, MONDO:0005336, BFO:0000020, BFO:0000016, MONDO:0002081, OGMS:0000031, MONDO:0016106, MONDO:0020120, MONDO:0019056, BFO:0000001, MONDO:0000001, BFO:0000002, MONDO:0700223, MONDO:0020121]"
                    ],
                    "subject_closure_label": [
                        "[nervous system disorder, human disease, realizable entity, musculoskeletal system disorder, disposition, muscular dystrophy, disease, specifically dependent continuant, hereditary disease, muscle tissue disorder, entity, continuant, progressive muscular dystrophy, skeletal muscle disorder, neuromuscular disease, disease, hereditary skeletal muscle disorder, myopathy]"
                    ],
                    "object_label": "muscular dystrophy",
                    "object_category": "biolink:Disease",
                    "object_namespace": "MONDO",
                    "object_closure": [
                        "[BFO:0000017, MONDO:0003847, MONDO:0003939, BFO:0000001, MONDO:0700096, MONDO:0005071, MONDO:0005336, BFO:0000016, MONDO:0002081, OGMS:0000031, MONDO:0020120, MONDO:0019056, MONDO:0000001, MONDO:0700223, MONDO:0020121, BFO:0000002, BFO:0000020]"
                    ],
                    "object_closure_label": [
                        "[nervous system disorder, human disease, continuant, realizable entity, specifically dependent continuant, musculoskeletal system disorder, disposition, muscular dystrophy, disease, hereditary disease, muscle tissue disorder, skeletal muscle disorder, neuromuscular disease, disease, entity, hereditary skeletal muscle disorder, myopathy]"
                    ],
                    "grouping_key": "MONDO:0016106🍪🍪biolink:subclass_of🍪MONDO:0020121",
                },
                {
                    "id": "urn:uuid:f48c5307-430c-47d3-a725-2e2a5a742502",
                    "predicate": "biolink:subclass_of",
                    "category": "biolink:Association",
                    "aggregator_knowledge_source": ["infores:phenio"],
                    "primary_knowledge_source": "infores:mondo",
                    "provided_by": "phenio_edges",
                    "subject": "MONDO:0018949",
                    "object": "MONDO:0020121",
                    "subject_label": "distal myopathy",
                    "subject_category": "biolink:Disease",
                    "subject_namespace": "MONDO",
                    "subject_closure": [
                        "[BFO:0000017, MONDO:0003847, MONDO:0003939, BFO:0000001, MONDO:0700096, MONDO:0005071, MONDO:0005336, BFO:0000020, BFO:0000016, MONDO:0002081, OGMS:0000031, MONDO:0020120, MONDO:0019056, MONDO:0000001, BFO:0000002, MONDO:0700223, MONDO:0020121, MONDO:0018949]"
                    ],
                    "subject_closure_label": [
                        "[nervous system disorder, human disease, realizable entity, musculoskeletal system disorder, disposition, muscular dystrophy, disease, specifically dependent continuant, hereditary disease, muscle tissue disorder, continuant, skeletal muscle disorder, neuromuscular disease, disease, entity, distal myopathy, hereditary skeletal muscle disorder, myopathy]"
                    ],
                    "object_label": "muscular dystrophy",
                    "object_category": "biolink:Disease",
                    "object_namespace": "MONDO",
                    "object_closure": [
                        "[BFO:0000017, MONDO:0003847, MONDO:0003939, BFO:0000001, MONDO:0700096, MONDO:0005071, MONDO:0005336, BFO:0000016, MONDO:0002081, OGMS:0000031, MONDO:0020120, MONDO:0019056, MONDO:0000001, MONDO:0700223, MONDO:0020121, BFO:0000002, BFO:0000020]"
                    ],
                    "object_closure_label": [
                        "[nervous system disorder, human disease, continuant, realizable entity, specifically dependent continuant, musculoskeletal system disorder, disposition, muscular dystrophy, disease, hereditary disease, muscle tissue disorder, skeletal muscle disorder, neuromuscular disease, disease, entity, hereditary skeletal muscle disorder, myopathy]"
                    ],
                    "grouping_key": "MONDO:0018949🍪🍪biolink:subclass_of🍪MONDO:0020121",
                },
                {
                    "id": "urn:uuid:fd38c580-a50d-4fcb-8dc0-8791447c2a56",
                    "predicate": "biolink:subclass_of",
                    "category": "biolink:Association",
                    "aggregator_knowledge_source": ["infores:phenio"],
                    "primary_knowledge_source": "infores:mondo",
                    "provided_by": "phenio_edges",
                    "subject": "MONDO:0019950",
                    "object": "MONDO:0020121",
                    "subject_label": "congenital muscular dystrophy",
                    "subject_category": "biolink:Disease",
                    "subject_namespace": "MONDO",
                    "subject_closure": [
                        "[MONDO:0002320, BFO:0000017, MONDO:0003847, MONDO:0003939, BFO:0000001, MONDO:0700096, MONDO:0005071, MONDO:0005336, MONDO:0019950, BFO:0000016, MONDO:0002081, OGMS:0000031, MONDO:0020120, MONDO:0019056, MONDO:0000001, BFO:0000002, MONDO:0700223, MONDO:0020121, BFO:0000020]"
                    ],
                    "subject_closure_label": [
                        "[nervous system disorder, human disease, congenital nervous system disorder, realizable entity, specifically dependent continuant, musculoskeletal system disorder, disposition, muscular dystrophy, disease, hereditary disease, muscle tissue disorder, continuant, skeletal muscle disorder, neuromuscular disease, disease, entity, hereditary skeletal muscle disorder, myopathy, congenital muscular dystrophy]"
                    ],
                    "object_label": "muscular dystrophy",
                    "object_category": "biolink:Disease",
                    "object_namespace": "MONDO",
                    "object_closure": [
                        "[BFO:0000017, MONDO:0003847, MONDO:0003939, BFO:0000001, MONDO:0700096, MONDO:0005071, MONDO:0005336, BFO:0000016, MONDO:0002081, OGMS:0000031, MONDO:0020120, MONDO:0019056, MONDO:0000001, MONDO:0700223, MONDO:0020121, BFO:0000002, BFO:0000020]"
                    ],
                    "object_closure_label": [
                        "[nervous system disorder, human disease, continuant, realizable entity, specifically dependent continuant, musculoskeletal system disorder, disposition, muscular dystrophy, disease, hereditary disease, muscle tissue disorder, skeletal muscle disorder, neuromuscular disease, disease, entity, hereditary skeletal muscle disorder, myopathy]"
                    ],
                    "grouping_key": "MONDO:0019950🍪🍪biolink:subclass_of🍪MONDO:0020121",
                },
                {
                    "id": "urn:uuid:64946d45-656f-4149-899e-dbb7cd4cf5b4",
                    "predicate": "biolink:subclass_of",
                    "category": "biolink:Association",
                    "aggregator_knowledge_source": ["infores:phenio"],
                    "primary_knowledge_source": "infores:mondo",
                    "provided_by": "phenio_edges",
                    "subject": "MONDO:0020121",
                    "object": "MONDO:0019056",
                    "subject_label": "muscular dystrophy",
                    "subject_category": "biolink:Disease",
                    "subject_namespace": "MONDO",
                    "subject_closure": [
                        "[BFO:0000017, MONDO:0003847, MONDO:0003939, BFO:0000001, MONDO:0700096, MONDO:0005071, MONDO:0005336, BFO:0000016, MONDO:0002081, OGMS:0000031, MONDO:0020120, MONDO:0019056, MONDO:0000001, MONDO:0700223, MONDO:0020121, BFO:0000002, BFO:0000020]"
                    ],
                    "subject_closure_label": [
                        "[nervous system disorder, human disease, continuant, realizable entity, specifically dependent continuant, musculoskeletal system disorder, disposition, muscular dystrophy, disease, hereditary disease, muscle tissue disorder, skeletal muscle disorder, neuromuscular disease, disease, entity, hereditary skeletal muscle disorder, myopathy]"
                    ],
                    "object_label": "neuromuscular disease",
                    "object_category": "biolink:Disease",
                    "object_namespace": "MONDO",
                    "object_closure": [
                        "[BFO:0000017, BFO:0000001, MONDO:0700096, MONDO:0005071, BFO:0000020, BFO:0000016, OGMS:0000031, MONDO:0019056, MONDO:0000001, BFO:0000002]"
                    ],
                    "object_closure_label": [
                        "[nervous system disorder, human disease, realizable entity, disposition, disease, specifically dependent continuant, continuant, neuromuscular disease, disease, entity]"
                    ],
                    "grouping_key": "MONDO:0020121🍪🍪biolink:subclass_of🍪MONDO:0019056",
                },
                {
                    "id": "urn:uuid:620dce90-accb-4d07-ae53-5d4f6dc6d387",
                    "predicate": "biolink:subclass_of",
                    "category": "biolink:Association",
                    "aggregator_knowledge_source": ["infores:phenio"],
                    "primary_knowledge_source": "infores:mondo",
                    "provided_by": "phenio_edges",
                    "subject": "MONDO:0020121",
                    "object": "MONDO:0700223",
                    "subject_label": "muscular dystrophy",
                    "subject_category": "biolink:Disease",
                    "subject_namespace": "MONDO",
                    "subject_closure": [
                        "[BFO:0000017, MONDO:0003847, MONDO:0003939, BFO:0000001, MONDO:0700096, MONDO:0005071, MONDO:0005336, BFO:0000016, MONDO:0002081, OGMS:0000031, MONDO:0020120, MONDO:0019056, MONDO:0000001, MONDO:0700223, MONDO:0020121, BFO:0000002, BFO:0000020]"
                    ],
                    "subject_closure_label": [
                        "[nervous system disorder, human disease, continuant, realizable entity, specifically dependent continuant, musculoskeletal system disorder, disposition, muscular dystrophy, disease, hereditary disease, muscle tissue disorder, skeletal muscle disorder, neuromuscular disease, disease, entity, hereditary skeletal muscle disorder, myopathy]"
                    ],
                    "object_label": "hereditary skeletal muscle disorder",
                    "object_category": "biolink:Disease",
                    "object_namespace": "MONDO",
                    "object_closure": [
                        "[BFO:0000001, BFO:0000017, MONDO:0003847, MONDO:0003939, MONDO:0700096, BFO:0000016, MONDO:0002081, OGMS:0000031, MONDO:0020120, MONDO:0000001, MONDO:0700223, BFO:0000002, BFO:0000020]"
                    ],
                    "object_closure_label": [
                        "[human disease, entity, continuant, realizable entity, specifically dependent continuant, musculoskeletal system disorder, disposition, disease, hereditary disease, muscle tissue disorder, skeletal muscle disorder, disease, hereditary skeletal muscle disorder]"
                    ],
                    "grouping_key": "MONDO:0020121🍪🍪biolink:subclass_of🍪MONDO:0700223",
                },
                {
                    "id": "urn:uuid:b7b29c2e-4fd6-4c14-93a2-565a68f1f1dc",
                    "predicate": "biolink:subclass_of",
                    "category": "biolink:Association",
                    "aggregator_knowledge_source": ["infores:phenio"],
                    "primary_knowledge_source": "infores:mondo",
                    "provided_by": "phenio_edges",
                    "subject": "MONDO:0020121",
                    "object": "MONDO:0005336",
                    "subject_label": "muscular dystrophy",
                    "subject_category": "biolink:Disease",
                    "subject_namespace": "MONDO",
                    "subject_closure": [
                        "[BFO:0000017, MONDO:0003847, MONDO:0003939, BFO:0000001, MONDO:0700096, MONDO:0005071, MONDO:0005336, BFO:0000016, MONDO:0002081, OGMS:0000031, MONDO:0020120, MONDO:0019056, MONDO:0000001, MONDO:0700223, MONDO:0020121, BFO:0000002, BFO:0000020]"
                    ],
                    "subject_closure_label": [
                        "[nervous system disorder, human disease, continuant, realizable entity, specifically dependent continuant, musculoskeletal system disorder, disposition, muscular dystrophy, disease, hereditary disease, muscle tissue disorder, skeletal muscle disorder, neuromuscular disease, disease, entity, hereditary skeletal muscle disorder, myopathy]"
                    ],
                    "object_label": "myopathy",
                    "object_category": "biolink:Disease",
                    "object_namespace": "MONDO",
                    "object_closure": [
                        "[BFO:0000017, MONDO:0003939, BFO:0000001, MONDO:0700096, MONDO:0005336, BFO:0000016, MONDO:0002081, OGMS:0000031, MONDO:0020120, MONDO:0000001, BFO:0000002, BFO:0000020]"
                    ],
                    "object_closure_label": [
                        "[human disease, continuant, realizable entity, specifically dependent continuant, musculoskeletal system disorder, disposition, disease, muscle tissue disorder, skeletal muscle disorder, disease, entity, myopathy]"
                    ],
                    "grouping_key": "MONDO:0020121🍪🍪biolink:subclass_of🍪MONDO:0005336",
                },
                {
                    "id": "urn:uuid:03e216a5-ae14-42e6-88a7-c23768cfe8d5",
                    "predicate": "biolink:subclass_of",
                    "category": "biolink:Association",
                    "aggregator_knowledge_source": ["infores:phenio"],
                    "primary_knowledge_source": "infores:mondo",
                    "provided_by": "phenio_edges",
                    "subject": "MONDO:0023204",
                    "object": "MONDO:0020121",
                    "subject_label": "Fukuda-Miyanomae-Nakata syndrome",
                    "subject_category": "biolink:Disease",
                    "subject_namespace": "MONDO",
                    "subject_closure": [
                        "[BFO:0000017, MONDO:0003847, MONDO:0003939, MONDO:0700096, MONDO:0005071, MONDO:0005336, MONDO:0002254, BFO:0000020, BFO:0000016, MONDO:0002081, OGMS:0000031, MONDO:0023204, MONDO:0020120, MONDO:0019056, BFO:0000001, MONDO:0000001, BFO:0000002, MONDO:0700223, MONDO:0020121]"
                    ],
                    "subject_closure_label": [
                        "[nervous system disorder, human disease, realizable entity, musculoskeletal system disorder, disposition, muscular dystrophy, disease, specifically dependent continuant, hereditary disease, muscle tissue disorder, entity, continuant, Fukuda-Miyanomae-Nakata syndrome, skeletal muscle disorder, neuromuscular disease, syndromic disease, disease, hereditary skeletal muscle disorder, myopathy]"
                    ],
                    "object_label": "muscular dystrophy",
                    "object_category": "biolink:Disease",
                    "object_namespace": "MONDO",
                    "object_closure": [
                        "[BFO:0000017, MONDO:0003847, MONDO:0003939, BFO:0000001, MONDO:0700096, MONDO:0005071, MONDO:0005336, BFO:0000016, MONDO:0002081, OGMS:0000031, MONDO:0020120, MONDO:0019056, MONDO:0000001, MONDO:0700223, MONDO:0020121, BFO:0000002, BFO:0000020]"
                    ],
                    "object_closure_label": [
                        "[nervous system disorder, human disease, continuant, realizable entity, specifically dependent continuant, musculoskeletal system disorder, disposition, muscular dystrophy, disease, hereditary disease, muscle tissue disorder, skeletal muscle disorder, neuromuscular disease, disease, entity, hereditary skeletal muscle disorder, myopathy]"
                    ],
                    "grouping_key": "MONDO:0023204🍪🍪biolink:subclass_of🍪MONDO:0020121",
                },
                {
                    "id": "urn:uuid:62735729-6a66-4993-9390-8306e92fb7cb",
                    "predicate": "biolink:subclass_of",
                    "category": "biolink:Association",
                    "aggregator_knowledge_source": ["infores:phenio"],
                    "primary_knowledge_source": "infores:mondo",
                    "provided_by": "phenio_edges",
                    "subject": "MONDO:0100228",
                    "object": "MONDO:0020121",
                    "subject_label": "LAMA2-related muscular dystrophy",
                    "subject_category": "biolink:Disease",
                    "subject_namespace": "MONDO",
                    "subject_closure": [
                        "[BFO:0000017, MONDO:0003847, MONDO:0003939, BFO:0000001, MONDO:0016139, MONDO:0700096, MONDO:0100228, MONDO:0005071, MONDO:0005336, BFO:0000020, BFO:0000016, MONDO:0002081, OGMS:0000031, MONDO:0020120, MONDO:0019056, MONDO:0000001, MONDO:0700223, MONDO:0016149, MONDO:0020121, BFO:0000002]"
                    ],
                    "subject_closure_label": [
                        "[qualitative or quantitative defects of merosin, LAMA2-related muscular dystrophy, nervous system disorder, qualitative or quantitative protein defects in neuromuscular diseases, human disease, continuant, realizable entity, musculoskeletal system disorder, disposition, muscular dystrophy, disease, specifically dependent continuant, hereditary disease, muscle tissue disorder, skeletal muscle disorder, neuromuscular disease, disease, entity, hereditary skeletal muscle disorder, myopathy]"
                    ],
                    "object_label": "muscular dystrophy",
                    "object_category": "biolink:Disease",
                    "object_namespace": "MONDO",
                    "object_closure": [
                        "[BFO:0000017, MONDO:0003847, MONDO:0003939, BFO:0000001, MONDO:0700096, MONDO:0005071, MONDO:0005336, BFO:0000016, MONDO:0002081, OGMS:0000031, MONDO:0020120, MONDO:0019056, MONDO:0000001, MONDO:0700223, MONDO:0020121, BFO:0000002, BFO:0000020]"
                    ],
                    "object_closure_label": [
                        "[nervous system disorder, human disease, continuant, realizable entity, specifically dependent continuant, musculoskeletal system disorder, disposition, muscular dystrophy, disease, hereditary disease, muscle tissue disorder, skeletal muscle disorder, neuromuscular disease, disease, entity, hereditary skeletal muscle disorder, myopathy]"
                    ],
                    "grouping_key": "MONDO:0100228🍪🍪biolink:subclass_of🍪MONDO:0020121",
                },
                {
                    "id": "urn:uuid:b8e9536a-167c-4cc0-858e-f55a2e1d3cdc",
                    "predicate": "biolink:subclass_of",
                    "category": "biolink:Association",
                    "aggregator_knowledge_source": ["infores:phenio"],
                    "primary_knowledge_source": "infores:mondo",
                    "provided_by": "phenio_edges",
                    "subject": "MONDO:0008028",
                    "object": "MONDO:0020121",
                    "subject_label": "muscular dystrophy, Barnes type",
                    "subject_category": "biolink:Disease",
                    "subject_namespace": "MONDO",
                    "subject_closure": [
                        "[BFO:0000001, BFO:0000017, MONDO:0003847, MONDO:0003939, MONDO:0700096, MONDO:0005071, BFO:0000002, MONDO:0005336, BFO:0000020, BFO:0000016, MONDO:0002081, OGMS:0000031, MONDO:0020120, MONDO:0019056, MONDO:0000001, MONDO:0700223, MONDO:0020121, MONDO:0008028]"
                    ],
                    "subject_closure_label": [
                        "[continuant, nervous system disorder, human disease, entity, realizable entity, musculoskeletal system disorder, disposition, muscular dystrophy, muscular dystrophy, Barnes type, disease, specifically dependent continuant, hereditary disease, muscle tissue disorder, skeletal muscle disorder, neuromuscular disease, disease, hereditary skeletal muscle disorder, myopathy]"
                    ],
                    "object_label": "muscular dystrophy",
                    "object_category": "biolink:Disease",
                    "object_namespace": "MONDO",
                    "object_closure": [
                        "[BFO:0000017, MONDO:0003847, MONDO:0003939, BFO:0000001, MONDO:0700096, MONDO:0005071, MONDO:0005336, BFO:0000016, MONDO:0002081, OGMS:0000031, MONDO:0020120, MONDO:0019056, MONDO:0000001, MONDO:0700223, MONDO:0020121, BFO:0000002, BFO:0000020]"
                    ],
                    "object_closure_label": [
                        "[nervous system disorder, human disease, continuant, realizable entity, specifically dependent continuant, musculoskeletal system disorder, disposition, muscular dystrophy, disease, hereditary disease, muscle tissue disorder, skeletal muscle disorder, neuromuscular disease, disease, entity, hereditary skeletal muscle disorder, myopathy]"
                    ],
                    "grouping_key": "MONDO:0008028🍪🍪biolink:subclass_of🍪MONDO:0020121",
                },
                {
                    "id": "urn:uuid:d7f7a1e1-8fb2-4fd4-b419-a2852ad671ee",
                    "predicate": "biolink:subclass_of",
                    "category": "biolink:Association",
                    "aggregator_knowledge_source": ["infores:phenio"],
                    "primary_knowledge_source": "infores:mondo",
                    "provided_by": "phenio_edges",
                    "subject": "MONDO:0010675",
                    "object": "MONDO:0020121",
                    "subject_label": "muscular dystrophy, cardiac type",
                    "subject_category": "biolink:Disease",
                    "subject_namespace": "MONDO",
                    "subject_closure": [
                        "[BFO:0000017, MONDO:0003847, MONDO:0003939, MONDO:0010675, MONDO:0700096, MONDO:0005071, MONDO:0005336, BFO:0000020, BFO:0000016, MONDO:0002081, OGMS:0000031, MONDO:0020120, MONDO:0019056, BFO:0000001, MONDO:0000001, BFO:0000002, MONDO:0700223, MONDO:0020121]"
                    ],
                    "subject_closure_label": [
                        "[nervous system disorder, muscular dystrophy, cardiac type, human disease, realizable entity, musculoskeletal system disorder, disposition, muscular dystrophy, disease, specifically dependent continuant, hereditary disease, muscle tissue disorder, entity, continuant, skeletal muscle disorder, neuromuscular disease, disease, hereditary skeletal muscle disorder, myopathy]"
                    ],
                    "object_label": "muscular dystrophy",
                    "object_category": "biolink:Disease",
                    "object_namespace": "MONDO",
                    "object_closure": [
                        "[BFO:0000017, MONDO:0003847, MONDO:0003939, BFO:0000001, MONDO:0700096, MONDO:0005071, MONDO:0005336, BFO:0000016, MONDO:0002081, OGMS:0000031, MONDO:0020120, MONDO:0019056, MONDO:0000001, MONDO:0700223, MONDO:0020121, BFO:0000002, BFO:0000020]"
                    ],
                    "object_closure_label": [
                        "[nervous system disorder, human disease, continuant, realizable entity, specifically dependent continuant, musculoskeletal system disorder, disposition, muscular dystrophy, disease, hereditary disease, muscle tissue disorder, skeletal muscle disorder, neuromuscular disease, disease, entity, hereditary skeletal muscle disorder, myopathy]"
                    ],
                    "grouping_key": "MONDO:0010675🍪🍪biolink:subclass_of🍪MONDO:0020121",
                },
                {
                    "id": "urn:uuid:da357064-920d-425c-afaa-0e2f9cf43a1a",
                    "predicate": "biolink:subclass_of",
                    "category": "biolink:Association",
                    "aggregator_knowledge_source": ["infores:phenio"],
                    "primary_knowledge_source": "infores:mondo",
                    "provided_by": "phenio_edges",
                    "subject": "MONDO:0010676",
                    "object": "MONDO:0020121",
                    "subject_label": "muscular dystrophy, Hemizygous lethal type",
                    "subject_category": "biolink:Disease",
                    "subject_namespace": "MONDO",
                    "subject_closure": [
                        "[BFO:0000001, BFO:0000017, MONDO:0003847, MONDO:0003939, MONDO:0700096, MONDO:0005071, MONDO:0005336, BFO:0000020, BFO:0000016, MONDO:0002081, OGMS:0000031, MONDO:0020120, MONDO:0019056, MONDO:0010676, MONDO:0000001, BFO:0000002, MONDO:0700223, MONDO:0020121]"
                    ],
                    "subject_closure_label": [
                        "[muscular dystrophy, Hemizygous lethal type, nervous system disorder, human disease, entity, realizable entity, musculoskeletal system disorder, disposition, muscular dystrophy, disease, specifically dependent continuant, hereditary disease, muscle tissue disorder, continuant, skeletal muscle disorder, neuromuscular disease, disease, hereditary skeletal muscle disorder, myopathy]"
                    ],
                    "object_label": "muscular dystrophy",
                    "object_category": "biolink:Disease",
                    "object_namespace": "MONDO",
                    "object_closure": [
                        "[BFO:0000017, MONDO:0003847, MONDO:0003939, BFO:0000001, MONDO:0700096, MONDO:0005071, MONDO:0005336, BFO:0000016, MONDO:0002081, OGMS:0000031, MONDO:0020120, MONDO:0019056, MONDO:0000001, MONDO:0700223, MONDO:0020121, BFO:0000002, BFO:0000020]"
                    ],
                    "object_closure_label": [
                        "[nervous system disorder, human disease, continuant, realizable entity, specifically dependent continuant, musculoskeletal system disorder, disposition, muscular dystrophy, disease, hereditary disease, muscle tissue disorder, skeletal muscle disorder, neuromuscular disease, disease, entity, hereditary skeletal muscle disorder, myopathy]"
                    ],
                    "grouping_key": "MONDO:0010676🍪🍪biolink:subclass_of🍪MONDO:0020121",
                },
                {
                    "id": "urn:uuid:62dc8f15-f267-419e-aca4-b37045e4b830",
                    "predicate": "biolink:subclass_of",
                    "category": "biolink:Association",
                    "aggregator_knowledge_source": ["infores:phenio"],
                    "primary_knowledge_source": "infores:mondo",
                    "provided_by": "phenio_edges",
                    "subject": "MONDO:0010677",
                    "object": "MONDO:0020121",
                    "subject_label": "muscular dystrophy, Mabry type",
                    "subject_category": "biolink:Disease",
                    "subject_namespace": "MONDO",
                    "subject_closure": [
                        "[BFO:0000017, MONDO:0003847, MONDO:0003939, BFO:0000001, MONDO:0010677, MONDO:0700096, MONDO:0005071, MONDO:0005336, BFO:0000016, MONDO:0002081, OGMS:0000031, MONDO:0020120, MONDO:0019056, MONDO:0000001, MONDO:0700223, MONDO:0020121, BFO:0000002, BFO:0000020]"
                    ],
                    "subject_closure_label": [
                        "[nervous system disorder, muscular dystrophy, Mabry type, human disease, continuant, realizable entity, specifically dependent continuant, musculoskeletal system disorder, disposition, muscular dystrophy, disease, hereditary disease, muscle tissue disorder, skeletal muscle disorder, neuromuscular disease, disease, entity, hereditary skeletal muscle disorder, myopathy]"
                    ],
                    "object_label": "muscular dystrophy",
                    "object_category": "biolink:Disease",
                    "object_namespace": "MONDO",
                    "object_closure": [
                        "[BFO:0000017, MONDO:0003847, MONDO:0003939, BFO:0000001, MONDO:0700096, MONDO:0005071, MONDO:0005336, BFO:0000016, MONDO:0002081, OGMS:0000031, MONDO:0020120, MONDO:0019056, MONDO:0000001, MONDO:0700223, MONDO:0020121, BFO:0000002, BFO:0000020]"
                    ],
                    "object_closure_label": [
                        "[nervous system disorder, human disease, continuant, realizable entity, specifically dependent continuant, musculoskeletal system disorder, disposition, muscular dystrophy, disease, hereditary disease, muscle tissue disorder, skeletal muscle disorder, neuromuscular disease, disease, entity, hereditary skeletal muscle disorder, myopathy]"
                    ],
                    "grouping_key": "MONDO:0010677🍪🍪biolink:subclass_of🍪MONDO:0020121",
                },
                {
                    "id": "urn:uuid:ce4acbb5-efe5-4497-84b0-a841a7c79e79",
                    "predicate": "biolink:subclass_of",
                    "category": "biolink:Association",
                    "aggregator_knowledge_source": ["infores:phenio"],
                    "primary_knowledge_source": "infores:mondo",
                    "provided_by": "phenio_edges",
                    "subject": "MONDO:0010678",
                    "object": "MONDO:0020121",
                    "subject_label": "muscular dystrophy, progressive Pectorodorsal",
                    "subject_category": "biolink:Disease",
                    "subject_namespace": "MONDO",
                    "subject_closure": [
                        "[BFO:0000017, MONDO:0003847, MONDO:0003939, MONDO:0700096, MONDO:0005071, MONDO:0005336, BFO:0000020, BFO:0000016, MONDO:0002081, OGMS:0000031, MONDO:0020120, MONDO:0019056, BFO:0000001, MONDO:0000001, BFO:0000002, MONDO:0700223, MONDO:0020121, MONDO:0010678]"
                    ],
                    "subject_closure_label": [
                        "[nervous system disorder, human disease, realizable entity, musculoskeletal system disorder, disposition, muscular dystrophy, muscular dystrophy, progressive Pectorodorsal, disease, specifically dependent continuant, hereditary disease, muscle tissue disorder, entity, continuant, skeletal muscle disorder, neuromuscular disease, disease, hereditary skeletal muscle disorder, myopathy]"
                    ],
                    "object_label": "muscular dystrophy",
                    "object_category": "biolink:Disease",
                    "object_namespace": "MONDO",
                    "object_closure": [
                        "[BFO:0000017, MONDO:0003847, MONDO:0003939, BFO:0000001, MONDO:0700096, MONDO:0005071, MONDO:0005336, BFO:0000016, MONDO:0002081, OGMS:0000031, MONDO:0020120, MONDO:0019056, MONDO:0000001, MONDO:0700223, MONDO:0020121, BFO:0000002, BFO:0000020]"
                    ],
                    "object_closure_label": [
                        "[nervous system disorder, human disease, continuant, realizable entity, specifically dependent continuant, musculoskeletal system disorder, disposition, muscular dystrophy, disease, hereditary disease, muscle tissue disorder, skeletal muscle disorder, neuromuscular disease, disease, entity, hereditary skeletal muscle disorder, myopathy]"
                    ],
                    "grouping_key": "MONDO:0010678🍪🍪biolink:subclass_of🍪MONDO:0020121",
                },
            ],
        },
        "facet_counts": {
            "facet_fields": {},
            "facet_queries": {
                '(category:"biolink:DiseaseToPhenotypicFeatureAssociation") AND (subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121")': 0,
                '(category:"biolink:GeneToPhenotypicFeatureAssociation") AND (subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121")': 0,
                '(category:"biolink:PairwiseGeneToGeneInteraction") AND (subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121")': 0,
                '(category:"biolink:GeneToPathwayAssociation") AND (subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121")': 0,
                '(category:"biolink:GeneToExpressionSiteAssociation") AND (subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121")': 0,
                '(category:"biolink:GeneToGeneHomologyAssociation") AND (subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121")': 0,
                '(category:"biolink:ChemicalToPathwayAssociation") AND (subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121")': 0,
                '(category:"biolink:MacromolecularMachineToMolecularActivityAssociation") AND (subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121")': 0,
                '(category:"biolink:MacromolecularMachineToCellularComponentAssociation") AND (subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121")': 0,
                '(category:"biolink:MacromolecularMachineToBiologicalProcessAssociation") AND (subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121")': 0,
                '(category:"biolink:CausalGeneToDiseaseAssociation") AND (subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121")': 0,
                '(category:"biolink:CorrelatedGeneToDiseaseAssociation") AND (subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121")': 0,
                '(category:"biolink:DiseaseToPhenotypicFeatureAssociation") AND (object:"MONDO:0020121" OR object_closure:"MONDO:0020121")': 0,
                '(category:"biolink:GeneToPhenotypicFeatureAssociation") AND (object:"MONDO:0020121" OR object_closure:"MONDO:0020121")': 0,
                '(category:"biolink:PairwiseGeneToGeneInteraction") AND (object:"MONDO:0020121" OR object_closure:"MONDO:0020121")': 0,
                '(category:"biolink:GeneToPathwayAssociation") AND (object:"MONDO:0020121" OR object_closure:"MONDO:0020121")': 0,
                '(category:"biolink:GeneToExpressionSiteAssociation") AND (object:"MONDO:0020121" OR object_closure:"MONDO:0020121")': 0,
                '(category:"biolink:GeneToGeneHomologyAssociation") AND (object:"MONDO:0020121" OR object_closure:"MONDO:0020121")': 0,
                '(category:"biolink:ChemicalToPathwayAssociation") AND (object:"MONDO:0020121" OR object_closure:"MONDO:0020121")': 0,
                '(category:"biolink:MacromolecularMachineToMolecularActivityAssociation") AND (object:"MONDO:0020121" OR object_closure:"MONDO:0020121")': 0,
                '(category:"biolink:MacromolecularMachineToCellularComponentAssociation") AND (object:"MONDO:0020121" OR object_closure:"MONDO:0020121")': 0,
                '(category:"biolink:MacromolecularMachineToBiologicalProcessAssociation") AND (object:"MONDO:0020121" OR object_closure:"MONDO:0020121")': 0,
                '(category:"biolink:CausalGeneToDiseaseAssociation") AND (object:"MONDO:0020121" OR object_closure:"MONDO:0020121")': 0,
                '(category:"biolink:CorrelatedGeneToDiseaseAssociation") AND (object:"MONDO:0020121" OR object_closure:"MONDO:0020121")': 0,
            },
        },
    }
