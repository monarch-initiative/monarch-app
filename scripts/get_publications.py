"""This script is intended to assist in updating the publications page of the Monarch website.

It uses the scholarly package to search for publications citing the Monarch Initiative and 
metadata (counts of publications citing Monarch) from Google Scholar.

It then writes the results to a json file, as well as a report containing:
    - the total number of publications found by scholarly
    - publications with no link (to be manually added)
    - duplicates returned by scholarly
    - publications that are already in the publications.json file
"""
import argparse
import json
import sys
from pathlib import Path
from typing import List

from scholarly import scholarly  # type: ignore
import pprint

pp = pprint.PrettyPrinter(indent=2, sort_dicts=False).pprint

outdir = Path(__file__).parent.parent / "frontend" / "src" / "pages" / "about"
script_dir = Path(__file__).parent

pubs_file = outdir / "publications.json"
new_pubs_file = script_dir / "new_pubs.json"
report_file = script_dir / "pubs_report.txt"
scholarly_file = script_dir / "scholarly_output.json"

# These either aren't publications, are known duplicates, or have bad/missing info
EXCLUDE = [
]


def get_citation_metadata():
    """Get citation metadata from google scholar

    See https://scholarly.readthedocs.io/en/latest/DataTypes.html?highlight=hindex for details
    """
    author = scholarly.search_author_id(id="zmUEDj0AAAAJ")
    scholarly.fill(author, sections=["basics", "indices", "counts", "publications"])  # type: ignore
    total = (
        author["citedby"]
        # - len([pub for pub in author["publications"] if pub["bib"]["title"] in EXCLUDE])
        - len([pub for pub in author["publications"] if int(pub["bib"]["pub_year"]) < 2012])
    )
    citation_info = {
        "total": total,  # type: ignore
        "num_publications": len(author["publications"]),  # type: ignore
        "last_5_yrs": author["citedby5y"],  # type: ignore
        "cites_per_year": author["cites_per_year"],  # type: ignore
        "hindex": author["hindex"],  # type: ignore
        "hindex5y": author["hindex5y"],  # type: ignore
        "i10index": author["i10index"],  # type: ignore
        "i10index5y": author["i10index5y"],  # type: ignore
    }
    return citation_info


def get_pubs_from_scholarly():
    """Search for Monarch publications using scholarly"""
    author = scholarly.search_author_id(id="zmUEDj0AAAAJ")
    scholarly.fill(author, sections=["publications"], sortby="year")  # type: ignore
    publications = author["publications"]  # type: ignore
    pubs = []
    for p in publications:
        scholarly.fill(p, sections=["bib"])  # type: ignore
        bib = p["bib"]  # type: ignore
        # if bib["title"] in EXCLUDE:  # type: ignore
        #     continue
        if "pub_year" not in bib or int(bib["pub_year"]) < 2012:
            continue
        title = bib["title"]  # type: ignore
        authors = ", ".join(bib["author"].split(" and "))  # type: ignore
        year = int(bib["pub_year"])
        journal = (
            bib["journal"]
            if "journal" in bib
            else bib["publisher"]
            if "publisher" in bib
            else bib["citation"]
            if "citation" in bib
            else ""
        )
        issue = ""
        if "volume" in bib:
            issue += f"{bib['volume']}"
        if "number" in bib:
            issue += f"({bib['number']})"
        if "pages" in bib:
            issue += f":{bib['pages']}"
        link = f"{p['pub_url']}" if ("pub_url" in p and "scholar.google" not in p["pub_url"]) else ""
        pubs.append(
            {
                "title": title,
                "authors": authors,
                "year": year,
                "journal": journal,
                "issue": issue,
                "link": link,
            }
        )
    return pubs


def pick_best(pub1, pub2):
    """Return publication with most info from two publications"""
    new_pub = {"title": pub1["title"]}
    # pick year from publication with link
    if pub1["link"]:
        new_pub["year"] = pub1["year"]
    else:
        new_pub["year"] = pub2["year"]
    # pick longer (non-empty) from each
    for k, v in pub1.items():
        if k in ["year", "title"]:
            continue
        new_pub[k] = v if len(v) > len(pub2[k]) else pub2[k]
    return new_pub


def check_for_dups(publication_list: List[dict]):
    """Check for duplicate publications from scholarly and pick best info from each"""
    checked = []
    duplicates = []
    for pub in publication_list:
        if pub["title"].lower() not in [p["title"].lower() for p in checked]:
            checked.append(pub)
        else:
            for ind, p in enumerate(checked):
                if p["title"].lower() == pub["title"].lower():
                    duplicates.append(pub["title"])
                    checked[ind] = pick_best(p, pub)
                    break
    return checked, duplicates


def find_existing(current_data, new_data):
    """Find publications in scholarly_data that are already in publications.json"""
    existing_titles = [pub["title"].lower() for pub in current_data]
    dups = [pub["title"] for pub in new_data if pub["title"].lower() in existing_titles]
    filtered = [pub for pub in new_data if pub["title"].lower() not in existing_titles]
    ### The below returns a different list than the above, but I'm not sure why ###
    # dups = []
    # for ind, pub in enumerate(new_data):
    #     if pub["title"].lower() in existing_titles:
    #         new_data.pop(ind)
    #         dups.append(pub["title"])
    return filtered, dups


def write_citations(publications: List[dict], metadata: dict):
    """Write JSON file with citations for each publication"""
    # group by year
    pubs_sorted = []
    for pub in publications:
        if pub["year"] not in [year["year"] for year in pubs_sorted]:
            pubs_sorted.append({"year": pub["year"], "items": [pub]})
        else:
            for year in pubs_sorted:
                if year["year"] == pub["year"]:
                    year["items"].insert(0, pub)
                    break
    output = {"metadata": metadata, "publications": pubs_sorted}
    # write to output file
    with open(new_pubs_file, "w") as f:
        json.dump(output, f, indent=2)


def write_report(report: List[str]):
    """Write report of publications with no link or with Google Scholar link"""
    with open(report_file, "w") as f:
        f.write("\n".join(report))


def main(update: bool):
    """Main function"""
    report = []
    metadata = get_citation_metadata()

    # Get publications from scholarly or existing file
    Path(scholarly_file).touch()
    with open(scholarly_file, "r+") as f:
        if args.update:
            scholarly_data = get_pubs_from_scholarly()
            json.dump(scholarly_data, f, indent=2)
        else:
            scholarly_data = json.load(f)
    report.append(f"{'-'*120}\nFound {len(scholarly_data)} publications in Google Scholar")

    # Check for duplicate publications in scholarly_data
    checked, dups = check_for_dups(scholarly_data)
    if dups:
        report.append(
            f"{'-'*120}\nFound (and removed) {len(scholarly_data) - len(checked)} duplicate publications in scholarly_data:"
        )
        for pub in dups:
            report.append(f"\n\t{pub}")
        scholarly_data = checked

    # Flag publications with no link (to manually edit in publications.json later)
    nolinks = [pub["title"] for pub in scholarly_data if not pub["link"]]  # type: ignore
    if nolinks:
        report.append(f"{'-'*120}\nFound {len(nolinks)} publications with no link:")
        for pub in nolinks:
            report.append(f"\n\t{pub}")

    # Filter out publications already in publications.json
    if not Path(pubs_file).exists():
        report.append(f"{'-'*120}\nNo publications.json file found. Creating one now...")
        with open(pubs_file, "w") as f:
            json.dump({"metadata": {}, "publications": []}, f, indent=2)
    with open(pubs_file, "r") as f:
        current_data = json.load(f)
    current_pubs = [pub for year in current_data["publications"] for pub in year["items"]]
    filtered, dups = find_existing(current_pubs, scholarly_data)
    if dups:
        report.append(
            f"{'-'*120}\nFound {len(dups)} publications already in publications.json ({len(filtered)} new publications)\nDuplicates:"
        )
        for pub in dups:
            report.append(f"\n\t{pub}")

    citations = filtered
    return citations, metadata, report


if __name__ == "__main__":
    ### Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="Debug mode", action="store_true", default=False)
    parser.add_argument(
        "-u", "--update", help="Update scholarly_output.json", default=True, action=argparse.BooleanOptionalAction
    )
    args = parser.parse_args()

    # if args.debug:
    #     get_citation_metadata()
    #     sys.exit()

    citations, metadata, report = main(args.update)
    write_citations(citations, metadata)
    write_report(report)
