import os
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


def get_github_release_dates():
    """Get GitHub releases with their deployment dates."""
    try:
        res = requests.get("https://api.github.com/repos/monarch-initiative/monarch-app/releases?per_page=100")
        res.raise_for_status()
        releases = res.json()

        # Create mapping of version to deployment date
        release_dates = {}
        for release in releases:
            tag_name = release.get("tag_name", "")
            published_at = release.get("published_at")
            if published_at:
                # Extract version from tag (e.g., "v1.17.0" -> "1.17.0")
                version = tag_name.lstrip("v")
                release_dates[version] = published_at

        return release_dates
    except Exception:
        return {}


def map_kg_to_deployment_date(kg_version: str, github_releases: dict) -> str:
    """Map a KG version to its deployment date from GitHub releases.

    Finds the first app release that happened after the KG build date.
    """
    if not kg_version or not github_releases:
        return None

    # Extract date from KG version (format: YYYY-MM-DD)
    if len(kg_version) >= 10 and kg_version.count("-") == 2:
        kg_date = kg_version[:10]  # Get YYYY-MM-DD part

        try:
            from datetime import datetime, timedelta, timezone

            kg_datetime = datetime.strptime(kg_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)

            # Find releases after this KG date, sorted by date
            matching_releases = []
            for version, published_at in github_releases.items():
                release_datetime = datetime.fromisoformat(published_at.replace("Z", "+00:00"))

                # If release is after KG date and within reasonable timeframe (60 days)
                if kg_datetime <= release_datetime <= kg_datetime + timedelta(days=60):
                    matching_releases.append((release_datetime, published_at))

            # Return the earliest matching release
            if matching_releases:
                matching_releases.sort()
                return matching_releases[0][1]

        except ValueError:
            pass

    return None


def get_release_versions(dev: bool = False, limit: int = 0, print_info: bool = False):
    url = f"{KG_DEV_URL if dev else KG_URL}/index.html"
    res = requests.get(url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    directories = soup.select("h5 + ul > li > a")

    # Get GitHub release dates for deployment mapping
    github_releases = get_github_release_dates()

    releases = []
    for directory in directories:
        if directory.text not in ["..", "kgx"]:
            version = directory.text
            deployment_date = map_kg_to_deployment_date(version, github_releases)

            release_info = {
                "version": version,
                "url": directory["href"],
                "release_date": version if version.count("-") == 2 and len(version) >= 10 else None,
                "deployment_date": deployment_date,
            }
            releases.append(release_info)

    releases.reverse()
    if limit:
        releases = releases[:limit]
    if print_info:
        for release in releases:
            deployment_info = f"Deployed: {release.get('deployment_date', 'N/A')}"
            console.print(f"Version: {release['version']:11s}{' ':—<3} URL: {release['url']} {deployment_info}")
    return releases


def get_release_metadata(release: str, dev: bool = False):
    release_url = f"{KG_DEV_URL if dev else KG_URL}/{release}"

    # Get deployment date for this release
    github_releases = get_github_release_dates()
    deployment_date = map_kg_to_deployment_date(release, github_releases)

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
        release_date=release if release.count("-") == 2 and len(release) >= 10 else None,
        deployment_date=deployment_date,
    )
    return release_info


def print_release_info(release_info: Release):
    for key, value in release_info.model_dump().items():
        console.print(f"{key+' ':—<12} {value}")


def get_current_deployment_info():
    """Get information about the currently deployed KG version in production.

    This reads environment variables set during deployment to provide
    the actual production deployment information.
    """
    kg_version = os.getenv("MONARCH_KG_VERSION")
    deployment_date = os.getenv("KG_DEPLOYMENT_DATE")
    api_version = os.getenv("MONARCH_API_VERSION")

    return {
        "kg_version": kg_version,
        "deployment_date": deployment_date,
        "api_version": api_version,
        "release_date": kg_version if kg_version and kg_version.count("-") == 2 and len(kg_version) >= 10 else None,
    }
