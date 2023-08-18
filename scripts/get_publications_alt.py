"""This script contains experimental methods for getting publications from Google Scholar and PubMed.

The goal is to use SerpAPI to search for publications by author,
then uses the Crossref API to search for DOIs,
and finally uses the PubMed API to search for PubMed IDs.
"""
import os
from pathlib import Path
from requests import get
from typing import List
from urllib.parse import quote_plus

from habanero import Crossref

CR = Crossref()
SERP_API_KEY = os.environ["SERP_API_KEY"]
OUTDIR = Path(__file__).parent.parent / "frontend" / "src" / "pages" / "about"
OUTFILE = OUTDIR / "publications.json"


def get_pubs_serp() -> List:
    """Search for Monarch publications using SerpAPI"""
    pubs = []
    start, finished = 0, False
    serp_url = (
        "https://serpapi.com/search.json?engine=google_scholar_author&author_id=zmUEDj0AAAAJ&hl=en&api_key="
        + SERP_API_KEY
    )
    while not finished:
        response = get(serp_url)
        results = response.json()
        if "articles" not in results or len(results["articles"]) == 0:
            print(f"No articles found: {results.keys()}")
            break
        num_results = len(results["articles"])
        for result in results["articles"]:
            pub = {"title": result["title"]}
            if "authors" in result:
                pub["authors"] = result["authors"]
            if "publication" in result:
                pub["journal"] = result["publication"]
            if "year" in result:
                pub["year"] = (result["year"][0],)
            pubs.append(pub)

        start += num_results
        serp_url = f"https://serpapi.com/search.json?engine=google_scholar_author&author_id=zmUEDj0AAAAJ&hl=en&api_key={SERP_API_KEY}&start={start}"
    return pubs


def get_pubmed_id(publication):
    """Search for the pubmed ID of a publication by title"""
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&term="
    url = f"{base_url}{quote_plus(publication['title'])}[title]"
    if "authors" in publication:
        url += f"+AND+{quote_plus(publication['authors'])}[author]"
    if "journal" in publication:
        url += f"+AND+{quote_plus(publication['journal'])}[journal]"
    if "year" in publication:
        url += f"+AND+{publication['year']}[pdat]"

    print(f"Requesting {url}")
    response = get(url)
    return response.json()


def search_for_doi(publication):
    """Search for the DOI of a publication via habanero/Crossref API"""
    title = publication["title"]
    first_author = publication["authors"].split(",")[0]
    year = publication["year"][0]
    results = CR.works(
        query_container_title=title,
        query_author=first_author,
        query_bibliographic=year,
    )
    print(
        f"Found DOI: {results['message']['total-results']}\n"
        f" for {publication['title']}\n"
        f" by {publication['authors']}\n"
        # f"result title: {result['title']}"
    )
    return results


def search_for_doi_alt(publication):
    base_url = "https://api.crossref.org/works?"
    query = f"query.bibliographic={quote_plus(publication['title'])}"
    if "year" in publication:
        query += f"+{str(publication['year'][0])}"
    if "authors" in publication:
        query += f"&query.author={quote_plus(publication['authors'].split(',')[0])}"
    url = f"{base_url}{query}"
    print(f"Requesting {url}")
    response = get(url)
    assert response.ok
    num_results = response.json()["message"]["total-results"]
    print(f"Found {num_results} results")
    results = response.json()["message"]["items"]
    return results


if __name__ == "__main__":
    ...
