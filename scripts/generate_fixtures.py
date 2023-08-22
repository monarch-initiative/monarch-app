import argparse
import os
import sys
from pathlib import Path

from monarch_py.implementations.solr.solr_implementation import SolrImplementation
from monarch_py.implementations.solr.solr_query_utils import (
    build_association_query,
    build_association_counts_query,
    build_autocomplete_query,
    build_histopheno_query,
    build_search_query,
    build_association_table_query,
)
from monarch_py.service.solr_service import SolrService, core
from monarch_py.utils.utils import format_output


### Define variables
si = SolrImplementation()
solr_url = os.getenv("MONARCH_SOLR_URL", "http://localhost:8983/solr")
solr_entities = SolrService(base_url=solr_url, core=core.ENTITY)
solr_associations = SolrService(base_url=solr_url, core=core.ASSOCIATION)

root = Path(__file__).parent.parent
frontend_fixture_dir = Path(f"{root}/frontend/fixtures")
backend_fixture_dir = Path(f"{root}/backend/tests/fixtures")

node_id = "MONDO:0020121"
category = "biolink:DiseaseToPhenotypicFeatureAssociation"


### Writers


def write_frontend_fixture(key, value):
    format_output("json", value, f"{frontend_fixture_dir}/{key}.json")


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

    ### Generate main fixtures
    if any([backend, frontend, all_fixtures]):
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
        # fixtures['node-publication-abstract'] =
        # fixtures['node-publication-summary'] =
        # fixtures['ontologies'] =
        # fixtures['phenotype-explorer-compare'] =
        # fixtures['phenotype-explorer-search'] =
        fixtures["search"] = si.search(q="fanconi")
        # fixtures['text-annotator'] =
        # fixtures['uptime'] =

    ### Generate extra backend fixtures
    if backend or all_fixtures:        
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
        extra_fixtures["search-query"] = build_search_query(q="fanconi")

        # solr doc fixtures
        extra_fixtures["association-response"] = solr_associations.query(
            build_association_query(entity=[node_id])
        )
        extra_fixtures["association-counts-response"] = solr_associations.query(
            extra_fixtures["association-counts-query"]
        )
        extra_fixtures["association-table-response"] = solr_associations.query(
            build_association_table_query(entity=node_id, category=category)
        )
        extra_fixtures["autocomplete-response"] = solr_entities.query(extra_fixtures["autocomplete-query"])
        extra_fixtures["entity-response"] = solr_entities.get(node_id)
        extra_fixtures["histopheno-response"] = solr_associations.query(extra_fixtures["histopheno-query"])
        extra_fixtures["search-response"] = solr_entities.query(extra_fixtures["search-query"])

    ### Write frontend fixtures
    if frontend or all_fixtures:
        for key, value in fixtures.items():
            format_output("json", value, f"{frontend_fixture_dir}/{key}.json")

    ### Write backend fixtures
    if backend or all_fixtures:
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
        "-a", "--all", help="Generate all fixtures", default=True, action=argparse.BooleanOptionalAction
    )
    args = parser.parse_args()
    main(**vars(args))
