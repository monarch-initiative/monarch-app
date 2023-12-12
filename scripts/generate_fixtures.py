"""
Generate fixtures for monarch-app. 
Requires a running instance of both Solr and semsimian_server.
"""

import argparse
import json
import os
import sys
from pathlib import Path

from monarch_py.api.semsim import _compare, _search
from monarch_py.implementations.solr.solr_implementation import SolrImplementation
from monarch_py.implementations.solr.solr_query_utils import (
    build_association_query,
    build_association_counts_query,
    build_association_table_query,
    build_autocomplete_query,
    build_histopheno_query,
    build_mapping_query,
    build_search_query,
)
from monarch_py.service.solr_service import SolrService, core
from monarch_py.utils.utils import format_output

# from pprint import pprint as pp

### Define variables

si = SolrImplementation()
solr_url = os.getenv("MONARCH_SOLR_URL", "http://localhost:8983/solr")
solr_entities = SolrService(base_url=solr_url, core=core.ENTITY)
solr_associations = SolrService(base_url=solr_url, core=core.ASSOCIATION)
solr_mappings = SolrService(base_url=solr_url, core=core.SSSOM)

root = Path(__file__).parent.parent
frontend_fixture_dir = Path(root) / "frontend" / "fixtures"
backend_fixture_dir = Path(root) / "backend" / "tests" / "fixtures"

node_id = "MONDO:0020121"
category = "biolink:DiseaseToPhenotypicFeatureAssociation"


### Writers
def write_frontend_fixture(key, value):
    file = f"{frontend_fixture_dir}/{key}.json"
    try:
        format_output("json", value, file)
    except AttributeError:
        with open(file, "w") as f:
            json.dump(value, f, indent=4)


def write_backend_fixture(key, value):
    try:
        contents = value.dict()
    except AttributeError:
        contents = value
    filename = f"{backend_fixture_dir}/{key.replace('-', '_')}.py"
    file_contents = f"""
import pytest

@pytest.fixture
def {key.replace('-','_')}():
    return {contents}
"""
    with open(f"{filename}", "w") as f:
        f.write(file_contents)


### Helpers
def get_fv_label(category: str) -> str:
    targets = [
        "biolink:Gene",
        "biolink:PhenotypicQuality",
        "biolink:Disease",
        "biolink:GeneToPhenotypicFeatureAssociation",
        "biolink:DiseaseToPhenotypicFeatureAssociation",
        "biolink:CorrelatedGeneToDiseaseAssociation",
        "biolink:CausalGeneToDiseaseAssociation",
    ]
    return "Test Label"


def get_fv_icon(category: str) -> str:
    return "Test Icon"


def main(
    backend: bool = False,
    frontend: bool = False,
    metadata: bool = False,
    all_fixtures: bool = False,
):
    """Generate fixtures for monarch-app"""

    if not any([backend, frontend, metadata, all]):
        print("Please specify which fixtures to generate. Options are: `backend`, `frontend`, `metadata`, `all`")
        sys.exit(1)

    ### Check if Solr is available
    if not SolrImplementation().solr_is_available():
        raise Exception("Solr is not available. Please try running `monarch solr start` and try again.")

    fixtures = {}
    extra_fixtures = {}

    ### Generate metadata fixtures
    if metadata or all_fixtures:
        print(f"{'-'*120}\n\tGenerating metadata fixtures...")
        targets = [
            "biolink:Gene",
            "biolink:PhenotypicFeature",
            "biolink:Disease",
            "biolink:GeneToPhenotypicFeatureAssociation",
            "biolink:DiseaseToPhenotypicFeatureAssociation",
            "biolink:CorrelatedGeneToDiseaseAssociation",
            "biolink:CausalGeneToDiseaseAssociation",
        ]
        counts = []
        node_counts = {}
        node_ffs = si.search(q="*:*", facet_fields=["category"], limit=0).facet_fields[0]  # type: ignore
        node_counts_total = sum([f.count for f in node_ffs.facet_values])  # type: ignore
        for fv in [f for f in node_ffs.facet_values if f.label in targets]:  # type: ignore
            node_counts[fv.label] = fv.count

        association_counts = {}
        association_ffs = si.get_association_facets(facet_fields=["category"]).facet_fields[0]  # type: ignore
        for fv in [f for f in association_ffs.facet_values if f.label in targets]:  # type: ignore
            association_counts[fv.label] = fv.count
        association_counts_total = sum([f.count for f in association_ffs.facet_values])  # type: ignore
        gene_to_disease = (
            association_counts["biolink:CorrelatedGeneToDiseaseAssociation"]
            + association_counts["biolink:CausalGeneToDiseaseAssociation"]
        )

        counts = {"node": [], "association": []}
        for node_count in [
            {"label": "Genes", "icon": "category-gene", "count": node_counts["biolink:Gene"]},
            {
                "label": "Phenotypes",
                "icon": "category-phenotypic-quality",
                "count": node_counts["biolink:PhenotypicFeature"],
            },
            {"label": "Diseases", "icon": "category-disease", "count": node_counts["biolink:Disease"]},
            {"label": "Total Nodes", "icon": "node", "count": node_counts_total},
        ]:
            counts["node"].append(node_count)

        for association_count in [
            {
                "label": "Gene to Disease",
                "icon": "association-gene-to-disease",
                "count": gene_to_disease,
            },
            {
                "label": "Gene to Phenotype",
                "icon": "association-gene-to-phenotype",
                "count": association_counts["biolink:GeneToPhenotypicFeatureAssociation"],
            },
            {
                "label": "Disease to Phenotype",
                "icon": "association-disease-to-phenotype",
                "count": association_counts["biolink:DiseaseToPhenotypicFeatureAssociation"],
            },
            {
                "label": "Total Associations",
                "icon": "association",
                "count": association_counts_total,
            },
        ]:
            counts["association"].append(association_count)

        with open(root / "frontend" / "src" / "pages" / "metadata.json", "w") as f:
            json.dump(counts, f, indent=2)

    ### Generate core fixtures
    if any([backend, frontend, all_fixtures]):
        print(f"{'-'*120}\n\tGenerating core fixtures...")
        fixtures["associations"] = si.get_associations(entity=[node_id])
        fixtures["association-counts"] = si.get_association_counts(entity=node_id)
        fixtures["association-table"] = si.get_association_table(entity=node_id, category=category, offset=0, limit=5)
        # fixtures['association-evidence'] =
        fixtures["autocomplete"] = si.autocomplete("fanc")
        # fixtures['datasets'] =
        # fixtures['feedback'] =
        fixtures["histopheno"] = si.get_histopheno(node_id)
        fixtures["entity"] = si.get_entity(id=node_id, extra=False)
        fixtures["node"] = si.get_entity(id=node_id, extra=True)
        fixtures["mappings"] = si.get_mappings(entity_id=node_id)
        # fixtures['node-publication-abstract'] =
        # fixtures['node-publication-summary'] =
        # fixtures['ontologies'] =
        fixtures["phenotype-explorer-compare"] = _compare(subjects="MP:0010771,MP:0002169", objects="HP:0004325")
        fixtures["phenotype-explorer-search"] = _search(termset="HP:0000001,HP:0000002", prefix="ZFIN", limit=10)
        fixtures["search"] = si.search(q="fanconi")
        # fixtures['text-annotator'] =
        # fixtures['uptime'] =

    ### Generate extra backend fixtures
    if backend or all_fixtures:
        print(f"{'-'*120}\n\tGenerating extra backend fixtures...")
        extra_fixtures["association-counts-query"] = build_association_counts_query(entity=node_id)
        extra_fixtures["association-query-params"] = {
            "category": ["biolink:TestCase"],
            "predicate": ["biolink:is_a_test_case", "biolink:is_an_example"],
            "subject": ["TEST:0000001"],
            "object": ["TEST:0000002"],
            "subject_closure": "TEST:0000003",
            "object_closure": "TEST:0000004",
            "entity": ["TEST:0000005"],
            "q": "test:q",
            "offset": 100,
            "limit": 100,
        }
        extra_fixtures["association-query-direct"] = build_association_query(
            **extra_fixtures["association-query-params"], direct=True
        )
        extra_fixtures["association-query-indirect"] = build_association_query(
            **extra_fixtures["association-query-params"], direct=False
        )
        extra_fixtures["autocomplete-query"] = build_autocomplete_query(q="fanc")
        extra_fixtures["histopheno-query"] = build_histopheno_query(subject_closure=node_id)
        extra_fixtures["mapping-query"] = build_mapping_query(entity_id=[node_id])
        extra_fixtures["search-query"] = build_search_query(q="fanconi")

        # solr doc fixtures
        extra_fixtures["association-response"] = solr_associations.query(build_association_query(entity=[node_id]))
        extra_fixtures["association-counts-response"] = solr_associations.query(
            extra_fixtures["association-counts-query"]
        )
        extra_fixtures["association-table-response"] = solr_associations.query(
            build_association_table_query(entity=node_id, category=category)
        )
        extra_fixtures["autocomplete-response"] = solr_entities.query(extra_fixtures["autocomplete-query"])
        extra_fixtures["entity-response"] = solr_entities.get(node_id)
        extra_fixtures["histopheno-response"] = solr_associations.query(extra_fixtures["histopheno-query"])
        extra_fixtures["mapping-response"] = solr_mappings.query(extra_fixtures["mapping-query"])
        extra_fixtures["search-response"] = solr_entities.query(extra_fixtures["search-query"])

    ### Write frontend fixtures
    if any([frontend, metadata, all_fixtures]):
        for key, value in fixtures.items():
            write_frontend_fixture(key, value)

    ### Write backend fixtures
    if any([backend, metadata, all_fixtures]):
        backend_fixtures = {**fixtures, **extra_fixtures}
        for key, value in backend_fixtures.items():
            write_backend_fixture(key, value)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate fixtures for monarch-app")
    parser.add_argument(
        "-f", "--frontend", help="Generate frontend fixtures", default=False, action=argparse.BooleanOptionalAction
    )
    parser.add_argument(
        "-b", "--backend", help="Generate backend fixtures", default=False, action=argparse.BooleanOptionalAction
    )
    parser.add_argument(
        "-m", "--metadata", help="Generate metadata fixtures", default=False, action=argparse.BooleanOptionalAction
    )
    parser.add_argument(
        "-a", "--all-fixtures", help="Generate all fixtures", default=False, action=argparse.BooleanOptionalAction
    )
    args = parser.parse_args()
    main(**vars(args))
