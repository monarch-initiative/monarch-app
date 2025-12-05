"""
This script is intended to assist in updating the publications page of the Monarch website.

It uses the scholarly package to search for publications citing the Monarch Initiative and
metadata (counts of publications citing Monarch) from Google Scholar.
"""

from collections import defaultdict
from functools import cache, reduce
import itertools
import json
from pathlib import Path
import re
import sys
from dataclasses import asdict, dataclass, replace, fields
from loguru import logger
from typing import DefaultDict, List, Optional
from typing_extensions import Annotated

import typer
from scholarly import Author, scholarly

app = typer.Typer()

# https://scholar.google.com/citations?user=zmUEDj0AAAAJ
MONARCH_GOOGLE_SCHOLAR_ID = "zmUEDj0AAAAJ"

KNOWN_LINKS = {
    "Metrics to Assess Value of Biomedical Digital Repositories": "https://zenodo.org/record/203295",
    "The Monarch Initiative: Insights across species reveal human disease mechanisms": "https://www.biorxiv.org/content/10.1101/055756v1",
    "k-BOOM: a Bayesian approach to ontology structure inference, with applications in disease ontology construction.  bioRxiv 2019: 048843": "https://www.biorxiv.org/content/10.1101/048843v3",
    "The Human Phenotype Ontology in 2024: phenotypes around the world": "https://doi.org/10.1093/nar/gkad1005",
    "Metrics to assess value of biomedical digital repositories: response to RFI NOT-OD-16-133": "https://zenodo.org/records/203295",
    "The GA4GH Phenopacket schema: A computable representation of clinical data for precision medicine": "https://www.medrxiv.org/content/10.1101/2021.11.27.21266944v1",
    "Evaluation of phenotype-driven gene prioritization methods for Mendelian diseases": "https://academic.oup.com/bib/article/23/2/bbac019/6521702",
    "The case for open science: rare diseases": "https://academic.oup.com/jamiaopen/article/3/3/472/5904414",
    "The Unified Phenotype Ontology (uPheno): A framework for cross-species integrative phenomics": "https://academic.oup.com/genetics/article/229/3/iyaf027/8058751",
    "Towards a standard benchmark for variant and gene prioritisation algorithms: PhEval-Phenotypic inference Evaluation framework": "https://bmcbioinformatics.biomedcentral.com/articles/10.1186/s12859-025-06105-4",
}


script_dir = Path(__file__).parent
default_metadata_file = script_dir / "metadata.json"
default_scholarly_data = script_dir / "scholarly_output.json"
default_publications_file = (
    script_dir.parent / "frontend/src/data/publications.json"
)


@dataclass
class MonarchPublication:
    """
    A publication from Google Scholar.
    """

    title: str
    authors: str
    year: int
    journal: str
    issue: str
    link: Optional[str]

    def key(self):
        """
        Return a unique key for a publication.

        This key is the title, as lowercase, with any non-alphanumeric characters removed.
        """
        return title_to_key(self.title)


def title_to_key(title: str) -> str:
    return re.sub(r"\W", "", title.lower())


def replace_links(pubs: list[MonarchPublication]) -> None:
    """
    Given a list of publications, replace the links of publications whose values are set in the KNOWN_LINKS dictionary
    defined at the top of this file.

    Edits are done in-place, potentially mutating the members of the list.
    """
    links_by_title = {pub.key(): pub for pub in pubs}

    for title, link in KNOWN_LINKS.items():
        key = title_to_key(title)
        if key in links_by_title:
            links_by_title[key].link = link


@cache
def get_scholarly_author() -> Author:
    """
    Fetch the scholarly.Author entity representing the Monarch Initiative from Google Scholar.
    """
    author = scholarly.search_author_id(id=MONARCH_GOOGLE_SCHOLAR_ID)
    scholarly.fill(author, sections=["basics", "indices", "counts", "publications"])  # type: ignore
    return author


def fetch_citation_metadata() -> dict[str, int]:
    """
    Get citation metadata from Google Scholar.

    See https://scholarly.readthedocs.io/en/latest/DataTypes.html?highlight=hindex for details
    """
    author = get_scholarly_author()

    citation_info = {
        "total": author["citedby"],  # type: ignore
        "num_publications": len(author["publications"]),  # type: ignore
        "last_5_yrs": author["citedby5y"],  # type: ignore
        "cites_per_year": author["cites_per_year"],  # type: ignore
        "hindex": author["hindex"],  # type: ignore
        "hindex5y": author["hindex5y"],  # type: ignore
        "i10index": author["i10index"],  # type: ignore
        "i10index5y": author["i10index5y"],  # type: ignore
    }

    return citation_info


def fetch_scholarly_publications() -> List[MonarchPublication]:
    """
    Search for Monarch publications from Google Scholar.
    """
    author = get_scholarly_author()
    publications = author["publications"]  # type: ignore
    pubs: List[MonarchPublication] = []

    for p in publications:
        scholarly.fill(p, sections=["bib"])  # type: ignore

        bib = p["bib"]  # type: ignore

        title = bib["title"]  # type: ignore
        authors = ", ".join(bib["author"].split(" and "))  # type: ignore
        year = int(bib["pub_year"])  # type: ignore

        journal = ""
        if "journal" in bib:
            journal = bib["journal"]
        elif "publisher" in bib:
            journal = bib["publisher"]
        elif "citation" in bib:
            journal = bib["citation"]

        issue = ""
        if "volume" in bib:
            issue += f"{bib['volume']}"
        if "number" in bib:
            issue += f"({bib['number']})"
        if "pages" in bib:
            issue += f":{bib['pages']}"

        link = p.get("pub_url", None)

        # Don't count links from Google Scholar as valid.
        if link and "scholar.google.com" in link:
            link = None

        pubs.append(
            MonarchPublication(
                title=title,
                authors=authors,
                year=year,
                journal=journal,
                issue=issue,
                link=link,
            )
        )

    return pubs


def combine_publications(pub1: MonarchPublication, pub2: MonarchPublication) -> MonarchPublication:
    """
    Given two publications, combine their metadata.

    Return publication with most info from two publications
    """
    # Use the first publication as the original source of truth.
    new_pub = replace(pub1)

    # If the second publication has a link, and the first one does not, then use the second publication as the source
    # of truth for both `link` and `year`.
    if not pub1.link and pub2.link:
        new_pub.link = pub2.link
        new_pub.year = pub2.year

    # pick longer (non-empty) from each
    for f in fields(pub1):
        if f.name in ["year", "title"]:
            continue
        val1 = getattr(pub1, f.name)
        val2 = getattr(pub2, f.name)
        if val1 is None:
            if val2 is not None:
                setattr(new_pub, f.name, val2)
        elif len(val2) > len(val1):
            setattr(new_pub, f.name, val2)

    return new_pub


def dedup_publications(publication_list: List[MonarchPublication]) -> List[MonarchPublication]:
    """
    Check for duplicate publications from scholarly and pick best info from each.
    """
    publication_list = sorted(publication_list, key=lambda p: p.key())
    pubs_by_key = itertools.groupby(publication_list, key=lambda p: p.key())

    deduped: List[MonarchPublication] = []

    for key, pubs in pubs_by_key:
        pubs_list = list(pubs)
        if len(pubs_list) == 1:
            pub = pubs_list[0]
        else:
            logger.info(f"Found {len(pubs_list)} records for {key}")
            pub = reduce(combine_publications, pubs)
        deduped.append(pub)

    return deduped


def extend_current_pubs(
    current_pubs: List[MonarchPublication], scholarly_pubs: List[MonarchPublication]
) -> List[MonarchPublication]:
    """
    Combine a list of current publications and new publications and merge them into one list.
    """
    existing_by_key = {pub.key(): pub for pub in current_pubs}

    new_pubs_ct = 0
    updated_pubs_ct = 0
    existing_pubs_ct = 0

    new_pubs: list[MonarchPublication] = []

    for pub in scholarly_pubs:
        existing_pub = existing_by_key.get(pub.key(), None)

        # If the year has been updated in Google Scholar, use that year.
        if existing_pub:
            if pub.year > existing_pub.year:
                logger.info(
                    f"Updating publication year for {pub.title} from {existing_pub.year} to {pub.year}"
                )
                existing_pub.year = pub.year
                updated_pubs_ct += 1
            else:
                existing_pubs_ct += 1
        else:
            new_pubs.append(pub)
            new_pubs_ct += 1

    logger.info(f"Untouched publications: {existing_pubs_ct}")
    logger.info(f"Updated publications: {updated_pubs_ct}")
    logger.info(f"New publications: {new_pubs_ct}")

    combined_pubs = current_pubs[:]
    combined_pubs.extend(new_pubs)

    return combined_pubs


def add_scholarly_publications(
    scholarly_file: Path, existing_publications_file: Optional[Path]
) -> List[MonarchPublication]:
    """
    Add scholarly publications to an existing publications.json file.
    """

    with open(scholarly_file) as fd:
        scholarly_pubs = [MonarchPublication(**pub_dict) for pub_dict in json.load(fd)]

    if existing_publications_file is not None:
        with open(existing_publications_file) as fd:
            current_data = json.load(fd)
            current_pubs = [
                MonarchPublication(**pub)
                for year in current_data["publications"]
                for pub in year["items"]
            ]
    else:
        current_pubs = []

    # Check for duplicate publications in scholarly_data
    scholarly_pubs = dedup_publications(scholarly_pubs)

    # Add known missing links
    replace_links(scholarly_pubs)

    # Bail out if there are any missing links after adding replacements
    missing_links = [pub for pub in scholarly_pubs if not pub.link]
    if missing_links:
        for pub in missing_links:
            logger.error(f"No link for {pub.title}. Add in script before continuing.")
        sys.exit(1)

    logger.info(f"Existing publications in system: {len(current_pubs)}")
    logger.info(f"Publications from Google Scholar: {len(scholarly_pubs)}")

    # Return the scholarly publications to the current publications
    return extend_current_pubs(current_pubs, scholarly_pubs)


@app.command()
def update(
    metadata_file: Annotated[
        Path,
        typer.Argument(
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ] = default_metadata_file,
    publications_file: Annotated[
        Path,
        typer.Argument(
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ] = default_scholarly_data,
    existing_data_file: Annotated[
        Optional[Path],
        typer.Argument(
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ] = default_publications_file,
    output_file: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ] = default_publications_file,
    update_data: bool = False,
) -> None:
    """
    Update the publications.json file.
    """
    if update_data:
        fetch_metadata()
        fetch_publications()

    if not metadata_file.exists():
        print(
            "No metadata file exists. Create it by passing the `--update-data` flag, or running `get_publications.py fetch_metadata`."
        )
        raise typer.Exit(code=1)

    if not publications_file.exists():
        print(
            "No publications file exists. Create it by passing the `--update-data` flag, or running `get_publications.py fetch_scholarly_publications`."
        )
        raise typer.Exit(code=1)

    pubs = add_scholarly_publications(publications_file, existing_data_file)

    # Convert publications to a dict and sort in such an order that the most recent year is first
    pubs_by_year: DefaultDict[int, List[MonarchPublication]] = defaultdict(list)
    for pub in pubs:
        pubs_by_year[pub.year].append(pub)

    publications_by_year = sorted(
        [{"year": k, "items": [asdict(p) for p in v]} for k, v in pubs_by_year.items()],
        key=lambda p: p["year"],
        reverse=True,
    )

    with metadata_file.open("r") as fd:
        metadata = json.load(fd)

    output = json.dumps(
        {
            "metadata": metadata,
            "publications": publications_by_year,
        },
        indent=2,
    )

    with output_file.open("w") as fd:
        fd.write(output)
        fd.write("\n")


@app.command()
def fetch_metadata(
    outfile: Annotated[Path, typer.Option("--output", "-o")] = default_metadata_file,
) -> None:
    """
    Fetch the latest citation metadata from Google Scholar.
    """
    citation_metadata = fetch_citation_metadata()
    output = json.dumps(citation_metadata, indent=2)

    with open(outfile, "w") as fd:
        fd.write(output)
        fd.write("\n")


@app.command()
def fetch_publications(
    outfile: Annotated[Path, typer.Option("--output", "-o")] = default_scholarly_data,
) -> None:
    """
    Fetch the latest publication list from Google Scholar.
    """
    publications = fetch_scholarly_publications()
    output = json.dumps([asdict(pub) for pub in publications], indent=2)

    with open(outfile, "w") as fd:
        fd.write(output)
        fd.write("\n")


if __name__ == "__main__":
    app()
