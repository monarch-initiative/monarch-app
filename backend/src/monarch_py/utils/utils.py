import sys
from typing import List

import bs4
import requests
from rich.console import Console

from monarch_py.datamodels.model import ExpandedCurie, Release
from monarch_py.service.curie_service import converter

KG_URL = "https://data.monarchinitiative.org/monarch-kg"
KG_DEV_URL = "https://data.monarchinitiative.org/monarch-kg-dev"
SOLR_DATA_URL = f"{KG_DEV_URL}/latest/solr.tar.gz"
SQL_DATA_URL = f"{KG_DEV_URL}/latest/monarch-kg.db.gz"


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
    expanded_curies = [ExpandedCurie(id=curie, url=get_link_for_curie(curie)) for curie in field if ":" in curie]
    return expanded_curies


def get_link_for_curie(curie: str) -> ExpandedCurie:
    url = converter.expand(curie.replace("PMID", "PUBMED"))
    if curie.startswith("GARD:"):
        url += "/index"
    return url


def get_provided_by_link(provided_by: str) -> ExpandedCurie:
    """Returns a link to the provided_by resource."""
    base_url = "https://monarch-initiative.github.io/monarch-ingest/Sources"
    pb = provided_by.replace("_nodes", "").replace("_edges", "").split("_")
    slug = f"{pb[0]}/#{'_'.join(pb[1:])}"
    return ExpandedCurie(
        id=provided_by.replace("_nodes", "").replace("_edges", "") if provided_by else None, url=f"{base_url}/{slug}"
    )


### Release info methods ###


def get_release_versions(dev: bool = False, limit: int = 0, print_info: bool = False):
    url = f"{KG_DEV_URL if dev else KG_URL}/index.html"
    res = requests.get(url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    directories = soup.select("h5 + ul > li > a")
    releases = [
        {"version": directory.text, "url": directory["href"]}
        for directory in directories
        if directory.text not in ["..", "kgx"]
        # if directory.text != ".."]
    ]
    releases.reverse()
    if limit:
        releases = releases[:limit]
    if print_info:
        for release in releases:
            console.print(f"Version: {release['version']:11s}{' ':—<3} URL: {release['url']}")
    return releases


def get_release_metadata(release: str, dev: bool = False):
    release_url = f"{KG_DEV_URL if dev else KG_URL}/{release}"
    release_info = Release(
        version=release,
        url=f"{release_url}/index.html",
        kg=f"{release_url}/monarch-kg.tar.gz",
        sqlite=f"{release_url}/monarch-kg.db.gz",
        solr=f"{release_url}/solr.tar.gz",
        neo4j=f"{release_url}/monarch-kg.neo4j.dump",
        metadata=f"{release_url}/metadata.yaml",
        graph_stats=f"{release_url}/merged_graph_stats.yaml",
        qc_report=f"{release_url}/qc_report.yaml",
    )
    return release_info


def print_release_info(release_info: Release):
    for key, value in release_info.model_dump().items():
        console.print(f"{key+' ':—<12} {value}")
