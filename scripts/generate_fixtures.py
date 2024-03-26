"""
Generate fixtures for monarch-app. 
Requires a running instance of both Solr and semsimian_server.
"""
import argparse
import json
import os
import sys
from pathlib import Path

from monarch_py.api.semsim import _compare, _search, _post_multicompare
from monarch_py.api.additional_models import SemsimSearchGroup, SemsimMultiCompareObject, SemsimMultiCompareRequest
from monarch_py.datamodels.category_enums import (
    AssociationCategory,
    AssociationPredicate,
    EntityCategory,
)
from monarch_py.datamodels.model import Association, HistoBin, Node, SearchResult
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
from monarch_py.utils.format_utils import format_output, to_json, to_tsv, to_yaml


### Define variables

si = SolrImplementation()
solr_url = os.getenv("MONARCH_SOLR_URL", "http://localhost:8983/solr")
solr_entities = SolrService(base_url=solr_url, core=core.ENTITY)
solr_associations = SolrService(base_url=solr_url, core=core.ASSOCIATION)
solr_mappings = SolrService(base_url=solr_url, core=core.SSSOM)

root = Path(__file__).parent.parent
frontend_fixture_dir = Path(root) / "frontend" / "fixtures"
backend_fixture_dir = Path(root) / "backend" / "tests" / "fixtures"

NODE_ID = "MONDO:0020121"
CATEGORY = AssociationCategory.DISEASE_TO_PHENOTYPIC_FEATURE_ASSOCIATION


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
        contents = value.model_dump()
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


def write_header_fixtures():
    association_headers = list(Association.model_fields)
    histobin_headers = list(HistoBin.model_fields)
    node_headers = list(Node.model_fields)
    search_headers = list(SearchResult.model_fields)
    file_contents = f"""
import pytest

@pytest.fixture
def association_headers():
    return {association_headers}

@pytest.fixture
def histobin_headers():
    return {histobin_headers}

@pytest.fixture
def node_headers():
    return {node_headers}

@pytest.fixture
def search_headers():
    return {search_headers}
"""
    with open(f"{backend_fixture_dir}/object_headers.py", "w") as f:
        f.write(file_contents)


def write_output_format_fixtures():
    json_output = to_json(si.get_entity(id=NODE_ID, extra=True), print_output=False)
    tsv_output = to_tsv(si.get_entity(id=NODE_ID, extra=True), print_output=False)
    yaml_output = to_yaml(si.get_entity(id=NODE_ID, extra=True), print_output=False)
    file_contents = f"""
import pytest

@pytest.fixture
def node_json():
    return \"\"\"\n{json_output}\n\"\"\"

@pytest.fixture
def node_tsv():
    return \"\"\"\n{tsv_output}\n\"\"\"

@pytest.fixture
def node_yaml():
    return \"\"\"\n{yaml_output}\n\"\"\"
"""
    with open(f"{backend_fixture_dir}/object_formatted.py", "w") as f:
        f.write(file_contents)


### Main
def main(
    backend: bool = False,
    frontend: bool = False,
    metadata: bool = False,
    all_fixtures: bool = False,
):
    """Generate fixtures for monarch-app"""

    if not any([backend, frontend, metadata, all]):
        print(
            "Please specify which fixtures to generate. Options are: `backend`, `frontend`, `metadata`, `all`"
        )
        sys.exit(1)

    ### Check if Solr is available
    if not SolrImplementation().solr_is_available():
        raise Exception(
            "Solr is not available. Please try running `monarch solr start` and try again."
        )

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
        node_ffs = si.search(q="*:*", facet_fields=["category"], limit=0).facet_fields[
            0
        ]  # type: ignore
        node_counts_total = sum([f.count for f in node_ffs.facet_values])  # type: ignore
        for fv in [f for f in node_ffs.facet_values if f.label in targets]:  # type: ignore
            node_counts[fv.label] = fv.count

        association_counts = {}
        association_ffs = si.get_association_facets(
            facet_fields=["category"]
        ).facet_fields[0]  # type: ignore
        for fv in [f for f in association_ffs.facet_values if f.label in targets]:  # type: ignore
            association_counts[fv.label] = fv.count
        association_counts_total = sum([f.count for f in association_ffs.facet_values])  # type: ignore
        gene_to_disease = (
            association_counts["biolink:CorrelatedGeneToDiseaseAssociation"]
            + association_counts["biolink:CausalGeneToDiseaseAssociation"]
        )

        counts = {"node": [], "association": []}
        for node_count in [
            {
                "label": "Genes",
                "icon": "category-gene",
                "count": node_counts["biolink:Gene"],
            },
            {
                "label": "Phenotypes",
                "icon": "category-phenotypic-quality",
                "count": node_counts["biolink:PhenotypicFeature"],
            },
            {
                "label": "Diseases",
                "icon": "category-disease",
                "count": node_counts["biolink:Disease"],
            },
            {"label": "Total Nodes", "icon": "node", "count": node_counts_total},
        ]:
            counts["node"].append(node_count)

        for association_count in [
            {
                "label": "Gene to Disease",
                "icon": "category-gene",
                "icon2": "category-disease",
                "count": gene_to_disease,
            },
            {
                "label": "Gene to Phenotype",
                "icon": "category-gene",
                "icon2": "category-phenotypic-quality",
                "count": association_counts[
                    "biolink:GeneToPhenotypicFeatureAssociation"
                ],
            },
            {
                "label": "Disease to Phenotype",
                "icon": "category-disease",
                "icon2": "category-phenotypic-quality",
                "count": association_counts[
                    "biolink:DiseaseToPhenotypicFeatureAssociation"
                ],
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
        fixtures["associations"] = si.get_associations(entity=[NODE_ID])
        fixtures["associations-compact"] = si.get_associations(
            entity=[NODE_ID], compact=True
        )
        fixtures["association-counts"] = si.get_association_counts(entity=NODE_ID)
        fixtures["association-table"] = si.get_association_table(
            entity=NODE_ID, category=CATEGORY, offset=0, limit=5
        )
        # fixtures['association-evidence'] =
        fixtures["autocomplete"] = si.autocomplete("fanc")
        # fixtures['datasets'] =
        # fixtures['feedback'] =
        fixtures["histopheno"] = si.get_histopheno(NODE_ID)
        fixtures["entity"] = si.get_entity(id=NODE_ID, extra=False)
        fixtures["node"] = si.get_entity(id=NODE_ID, extra=True)
        fixtures["mappings"] = si.get_mappings(entity_id=[NODE_ID])
        # fixtures['node-publication-abstract'] =
        # fixtures['node-publication-summary'] =
        # fixtures['ontologies'] =
        fixtures["phenotype-explorer-compare"] = _compare(
            subjects="MP:0010771,MP:0002169", objects="HP:0004325"
        )
        fixtures["phenotype-explorer-multi-compare"] = _post_multicompare(
            request=SemsimMultiCompareRequest(
                subjects=["MP:0010771", "MP:0002169"],
                object_sets=[
                    SemsimMultiCompareObject(
                        id="test1", label="Test1", phenotypes=["HP:0004325"]
                    ),
                    SemsimMultiCompareObject(
                        id="test2", label="Test2", phenotypes=["HP:0000093"]
                    ),
                ],
                metric="jaccard_similarity",
            )
        )
        fixtures["phenotype-explorer-search"] = _search(
            termset="HP:0002104,HP:0012378,HP:0012378,HP:0012378",
            group=SemsimSearchGroup.ZFIN,
            limit=10,
        )
        fixtures["search"] = si.search(q="fanconi")
        # fixtures['text-annotator'] =
        # fixtures['uptime'] =

    ### Generate extra backend fixtures
    if backend or all_fixtures:
        print(f"{'-'*120}\n\tGenerating extra backend fixtures...")
        extra_fixtures["association-counts-query"] = build_association_counts_query(
            entity=NODE_ID
        )
        extra_fixtures["association-query-params"] = {
            "category": [CATEGORY.value],
            "subject": ["TEST:0000001"],
            "subject_closure": "TEST:0000003",
            "subject_category": [EntityCategory.GENE.value],
            "subject_namespace": "TEST",
            "subject_taxon": ["NCBITaxon:1111"],
            "predicate": [AssociationPredicate.CAUSES.value],
            "object": ["TEST:0000002"],
            "object_closure": "TEST:0000004",
            "object_category": [EntityCategory.DISEASE.value],
            "object_namespace": "TEST",
            "object_taxon": ["NCBITaxon:2222"],
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
        extra_fixtures["histopheno-query"] = build_histopheno_query(
            subject_closure=NODE_ID
        )
        extra_fixtures["mapping-query"] = build_mapping_query(entity_id=[NODE_ID])
        extra_fixtures["search-query"] = build_search_query(q="fanconi")

        # solr doc fixtures
        extra_fixtures["association-response"] = solr_associations.query(
            build_association_query(entity=[NODE_ID])
        )
        extra_fixtures["association-counts-response"] = solr_associations.query(
            extra_fixtures["association-counts-query"]
        )
        extra_fixtures["association-table-response"] = solr_associations.query(
            build_association_table_query(entity=[NODE_ID], category=CATEGORY.value)
        )
        extra_fixtures["autocomplete-response"] = solr_entities.query(
            extra_fixtures["autocomplete-query"]
        )
        extra_fixtures["entity-response"] = solr_entities.get(NODE_ID)
        extra_fixtures["histopheno-response"] = solr_associations.query(
            extra_fixtures["histopheno-query"]
        )
        extra_fixtures["mapping-response"] = solr_mappings.query(
            extra_fixtures["mapping-query"]
        )
        extra_fixtures["search-response"] = solr_entities.query(
            extra_fixtures["search-query"]
        )

        # output fixtures
        write_header_fixtures()
        write_output_format_fixtures()

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
        "-f",
        "--frontend",
        help="Generate frontend fixtures",
        default=False,
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "-b",
        "--backend",
        help="Generate backend fixtures",
        default=False,
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "-m",
        "--metadata",
        help="Generate metadata fixtures",
        default=False,
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "-a",
        "--all-fixtures",
        help="Generate all fixtures",
        default=False,
        action=argparse.BooleanOptionalAction,
    )
    args = parser.parse_args()
    main(**vars(args))
