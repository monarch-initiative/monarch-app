import pytest


@pytest.fixture
def association_counts_query():
    return {
        "q": "*:*",
        "rows": 20,
        "start": 0,
        "facet": True,
        "facet_min_count": 1,
        "facet_fields": [],
        "facet_queries": [
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
        "filter_queries": [
            'subject:"MONDO:0020121" OR subject_closure:"MONDO:0020121" OR object:"MONDO:0020121" OR object_closure:"MONDO:0020121"'
        ],
        "query_fields": None,
        "def_type": "edismax",
        "q_op": "AND",
        "mm": "100%",
        "boost": None,
        "sort": None,
    }
