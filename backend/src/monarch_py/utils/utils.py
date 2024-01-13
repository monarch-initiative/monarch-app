import sys
from typing import List

from rich.console import Console
from monarch_py.datamodels.model import ExpandedCurie
from monarch_py.service.curie_service import converter

MONARCH_DATA_URL = "https://data.monarchinitiative.org/monarch-kg-dev"
SOLR_DATA_URL = f"{MONARCH_DATA_URL}/latest/solr.tar.gz"
SQL_DATA_URL = f"{MONARCH_DATA_URL}/latest/monarch-kg.db.gz"


console = Console(
    color_system="truecolor",
    stderr=True,
    style="pink1",
)


def strip_json(doc: dict, *fields_to_remove: str):
    for field in fields_to_remove:
        try:
            del doc[field]
        except KeyError:
            pass
    return doc


def escape(value: str) -> str:
    return value.replace(":", r"\:")


def dict_factory(cursor, row):
    """Converts a sqlite3 row to a dictionary."""
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


def compare_dicts(dict1, dict2):
    """Compare two dictionaries"""
    return all([k in dict2 for k in dict1]) and all([dict1[k] == dict2[k] for k in dict2])


def dict_diff(d1, d2) -> dict:
    """Return the difference between two dictionaries"""
    difference = {}
    for k in d1.keys():
        if d1[k] != d2[k]:
            difference[f"Dict-1-{k}"] = d1[k]
            difference[f"Dict-2-{k}"] = d2[k]
    return difference


def set_log_level(log_level: str):
    """Sets the log level for the application."""
    import loguru

    loguru.logger.remove()
    loguru.logger.add(sys.stderr, level=log_level)


### URL fetching methods ###


def get_links_for_field(field: List[str]) -> List[ExpandedCurie]:
    # TODO should be able to remove curie.replace("PMID", "PUBMED")) since the converter should handle prefix synonyms
    return [ExpandedCurie(id=curie, url=converter.expand(curie.replace("PMID", "PUBMED"))) for curie in field]


def get_provided_by_link(provided_by: str) -> ExpandedCurie:
    """Returns a link to the provided_by resource."""
    base_url = "https://monarch-initiative.github.io/monarch-ingest/Sources"
    pb = provided_by.replace("_nodes", "").replace("_edges", "").split("_")
    slug = f"{pb[0]}/#{'_'.join(pb[1:])}"
    return ExpandedCurie(
        id=provided_by.replace("_nodes", "").replace("_edges", "") if provided_by else None, url=f"{base_url}/{slug}"
    )
