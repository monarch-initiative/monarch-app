"""
This script uses the scholarly package query Google Scholar for 
titles of publications by the Monarch Initiative.

It then searches for the pubmed ID of each publication,
and finally uses manubot to generate citations for each publication.
"""
import json
import os
import sys
from pathlib import Path
from typing import List, Dict
from urllib.parse import quote_plus
from requests import get

from scholarly import scholarly
from habanero import Crossref
import manubot
import pprint

pp = pprint.PrettyPrinter(indent=2).pprint

CR = Crossref()
SERP_API_KEY = os.environ["SERP_API_KEY"]
OUTDIR = Path(__file__).parent.parent / "frontend" / "src" / "pages" / "about"
OUTFILE = OUTDIR / "publications.json"


def check_missing_fields(pub: dict) -> List[str]:
    """Check for missing fields in the publication"""
    ...


def get_pub_titles_scholarly():
    """Search for Monarch publications using scholarly"""
    # return
    titles = []
    author = scholarly.search_author_id(id="zmUEDj0AAAAJ")
    scholarly.fill(author, sections=["publications"], sortby="year")
    publications = author["publications"]
    for p in publications:
        scholarly.fill(p, sections=["bib"])
        pp(p["bib"])
        titles.append(p["bib"]["title"])
    return titles


def get_pubs() -> List:
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
            if 'authors' in result:
                pub["authors"] = result["authors"]
            if 'publication' in result:
                pub["journal"] = result["publication"]
            if 'year' in result:
                pub["year"] = result["year"][0],
            pubs.append(pub)

        start += num_results
        serp_url = f"https://serpapi.com/search.json?engine=google_scholar_author&author_id=zmUEDj0AAAAJ&hl=en&api_key={SERP_API_KEY}&start={start}"
    return pubs


def get_pubmed_id(publication):
    """Search for the pubmed ID of a publication by title"""
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&term="
    url = f"{base_url}{quote_plus(publication['title'])}[title]"
    if 'authors' in publication:
        url += f"+AND+{quote_plus(publication['authors'])}[author]"
    if 'journal' in publication:
        url += f"+AND+{quote_plus(publication['journal'])}[journal]"
    if 'year' in publication:
        url += f"+AND+{publication['year']}[pdat]"

    print(f"Requesting {url}")
    response = get(url)
    pp(response.json())
    return response.json()


def search_for_doi_alt(publication):
    base_url = "https://api.crossref.org/works?"
    query = f"query.bibliographic={quote_plus(publication['title'])}"
    if 'year' in publication:
        query += f"+{str(publication['year'][0])}"
    if 'authors' in publication:
        query += f"&query.author={quote_plus(publication['authors'].split(',')[0])}"
    url = f"{base_url}{query}"
    print(f"Requesting {url}")
    response = get(url)
    assert response.ok
    num_results = response.json()["message"]["total-results"]
    print(f"Found {num_results} results")
    results = response.json()["message"]["items"]
    return results


def search_for_doi(publication):
    """Search for the DOI of a publication via habanero/Crossref API"""
    title = publication["title"]
    first_author = publication["authors"].split(',')[0]
    year = publication["year"][0]
    results = CR.works(
        query_container_title = title,
        query_author = first_author,
        query_bibliographic = year,
    )
    print(
        f"Found DOI: {results['message']['total-results']}\n"
        f" for {publication['title']}\n"
        f" by {publication['authors']}\n"
        # f"result title: {result['title']}"
        )
    return results


def get_all_dois(pubs):
    """Get the DOI of each publication"""
    for pub in pubs:
        doi = search_for_doi(pub)
        if doi:
            pub["doi"] = doi
    return pubs

def get_pubmed_ids(pubs):
    """Get the pubmed IDs of a list of publications"""
    failed = []
    pubmed_ids = {}
    for pub in pubs:
        title = pub["title"]
        pubmed_ids[title] = get_pubmed_id(pub)
        if pubmed_ids[title]["esearchresult"]["count"] == "0":
            failed.append(title)
    if failed:
        print(f"Failed to find pubmed IDs for the following publications:")
        for pub in failed:
            print(f"\t{pub}")
    return pubmed_ids


def generate_citation(pubmed_id: str):
    return "citation"
    link = f"[Link]({p['pub_url']})" if "pub_url" in p else "No link found"
    pub_year = bib["pub_year"] if "pub_year" in bib else "Unknown"
    journal = (
        bib["journal"]
        if "journal" in bib
        else bib["publisher"]
        if "publisher" in bib
        else bib["citation"]
        if "citation" in bib
        else "No journal found"
    )
    issue = ""
    if "volume" in bib:
        issue += f"{bib['volume']}"
    if "number" in bib:
        issue += f"({bib['number']})"
    if "pages" in bib:
        issue += f":{bib['pages']}"

    try:
        pub = {
            "title": bib["title"],
            "authors": ", ".join(bib["author"].split(" and ")),
            "journal": journal,
            "pub_year": pub_year,
            "issue": issue,
            "link": link
            # 'link': f"[Link]({p['pub_url']})" if 'pub_url' in p else f"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={bib['title'].replace(' ', '+')}&btnG=&oq={bib['title'].replace(' ', '+')}",
        }
    except KeyError:
        pp(p)
        raise

    if any(i["year"] == pub_year for i in pubs_by_year):
        pubs_by_year[-1]["items"].append(pub)
    else:
        pubs_by_year.append({"year": pub_year, "items": [pub]})


def get_publications_by_year() -> Dict:
    """Sort publications into groups by year"""
    ...


if __name__ == "__main__":
    pubs = [
    {
        "title": "The Human Phenotype Ontology: a tool for annotating and analyzing human hereditary disease",
        "authors": "PN Robinson, S Köhler, S Bauer, D Seelow, D Horn, S Mundlos",
        "journal": "The American Journal of Human Genetics 83 (5), 610-615, 2008",
        "year": ("2008",),
    },
    {
        "title": "The Human Phenotype Ontology project: linking molecular biology and disease through phenotype data",
        "authors": "S Köhler, SC Doelken, CJ Mungall, S Bauer, HV Firth, I Bailleul-Forestier, ...",
        "journal": "Nucleic acids research 42 (D1), D966-D974, 2014",
        "year": ("2014",),
    },
    {
        "title": "The human phenotype ontology in 2017",
        "authors": "S Köhler, NA Vasilevsky, M Engelstad, E Foster, J McMurry, S Aymé, ...",
        "journal": "Nucleic acids research 45 (D1), D865-D876, 2017",
        "year": ("2017",),
    },
    {
        "title": "Uberon, an integrative multi-species anatomy ontology",
        "authors": "CJ Mungall, C Torniai, GV Gkoutos, SE Lewis, MA Haendel",
        "journal": "Genome biology 13 (1), 1-20, 2012",
        "year": ("2012",),
    },
    {
        "title": "Expansion of the Human Phenotype Ontology (HPO) knowledge base and resources",
        "authors": "S Köhler, L Carmody, N Vasilevsky, JOB Jacobsen, D Danis, JP Gourdine, ...",
        "journal": "Nucleic acids research 47 (D1), D1018-D1027, 2019",
        "year": ("2019",),
    },
    {
        "title": "The human phenotype ontology in 2021",
        "authors": "S Köhler, M Gargano, N Matentzoglu, LC Carmody, D Lewis-Smith, ...",
        "journal": "Nucleic acids research 49 (D1), D1207-D1217, 2021",
        "year": ("2021",),
    },
    {
        "title": "The Matchmaker Exchange: a platform for rare disease gene discovery",
        "authors": "AA Philippakis, DR Azzariti, S Beltran, AJ Brookes, CA Brownstein, ...",
        "journal": "Human mutation 36 (10), 915-921, 2015",
        "year": ("2015",),
    },
    {
        "title": "The human phenotype ontology",
        "authors": "PN Robinson, S Mundlos",
        "journal": "Clinical genetics 77 (6), 525-534, 2010",
        "year": ("2010",),
    },
    {
        "title": "Improved exome prioritization of disease genes through cross-species phenotype comparison",
        "authors": "PN Robinson, S Köhler, A Oellrich, K Wang, CJ Mungall, SE Lewis, ...",
        "journal": "Genome research 24 (2), 340-348, 2014",
        "year": ("2014",),
    },
    {
        "title": "Integrating phenotype ontologies across multiple species",
        "authors": "CJ Mungall, GV Gkoutos, CL Smith, MA Haendel, SE Lewis, M Ashburner",
        "journal": "Genome biology 11 (1), 1-16, 2010",
        "year": ("2010",),
    },
    {
        "title": "Next-generation diagnostics and disease-gene discovery with the Exomiser",
        "authors": "D Smedley, JOB Jacobsen, M Jäger, S Köhler, M Holtgrewe, M Schubach, ...",
        "journal": "Nature protocols 10 (12), 2004-2015, 2015",
        "year": ("2015",),
    },
    {
        "title": "Linking human diseases to animal models using ontology-based phenotype annotation",
        "authors": "NL Washington, MA Haendel, CJ Mungall, M Ashburner, M Westerfield, ...",
        "journal": "PLoS biology 7 (11), e1000247, 2009",
        "year": ("2009",),
    },
    {
        "title": "The environment ontology: contextualising biological and biomedical entities",
        "authors": "PL Buttigieg, N Morrison, B Smith, CJ Mungall, SE Lewis, ...",
        "journal": "Journal of biomedical semantics 4, 1-9, 2013",
        "year": ("2013",),
    },
    {
        "title": "The Monarch Initiative: an integrative data and analytic platform connecting phenotypes to genotypes across species",
        "authors": "CJ Mungall, JA McMurry, S Köhler, JP Balhoff, C Borromeo, M Brush, ...",
        "journal": "Nucleic acids research 45 (D1), D712-D722, 2017",
        "year": ("2017",),
    },
    {
        "title": "Classification, ontology, and precision medicine",
        "authors": "MA Haendel, CG Chute, PN Robinson",
        "journal": "New England Journal of Medicine 379 (15), 1452-1462, 2018",
        "year": ("2018",),
    },
    {
        "title": "Effective diagnosis of genetic disease by computational phenotype analysis of the disease-associated genome",
        "authors": "T Zemojtel, S Köhler, L Mackenroth, M Jäger, J Hecht, P Krawitz, ...",
        "journal": "Science translational medicine 6 (252), 252ra123-252ra123, 2014",
        "year": ("2014",),
    },
    {
        "title": "A whole-genome analysis framework for effective identification of pathogenic regulatory variants in Mendelian disease",
        "authors": "D Smedley, M Schubach, JOB Jacobsen, S Köhler, T Zemojtel, ...",
        "journal": "The American Journal of Human Genetics 99 (3), 595-606, 2016",
        "year": ("2016",),
    },
    {
        "title": "100,000 genomes pilot on rare-disease diagnosis in health care—preliminary report",
        "authors": "100,000 Genomes Project Pilot Investigators",
        "journal": "New England Journal of Medicine 385 (20), 1868-1880, 2021",
        "year": ("2021",),
    },
    {
        "title": "The human phenotype ontology: semantic unification of common and rare disease",
        "authors": "T Groza, S Köhler, D Moldenhauer, N Vasilevsky, G Baynam, T Zemojtel, ...",
        "journal": "The American Journal of Human Genetics 97 (1), 111-124, 2015",
        "year": ("2015",),
    },
    {
        "title": "Finding our way through phenotypes",
        "authors": "AR Deans, SE Lewis, E Huala, SS Anzaldo, M Ashburner, JP Balhoff, ...",
        "journal": "PLoS biology 13 (1), e1002033, 2015",
        "year": ("2015",),
    },
    {
        "title": "How many rare diseases are there?",
        "authors": "M Haendel, N Vasilevsky, D Unni, C Bologa, N Harris, H Rehm, ...",
        "journal": "Nature reviews drug discovery 19 (2), 77-78, 2020",
        "year": ("2020",),
    },
    {
        "title": "Disease model discovery from 3,328 gene knockouts by The International Mouse Phenotyping Consortium",
        "authors": "TF Meehan, N Conte, DB West, JO Jacobsen, J Mason, J Warren, ...",
        "journal": "Nature genetics 49 (8), 1231-1238, 2017",
        "year": ("2017",),
    },
    {
        "title": "The Cell Ontology 2016: enhanced content, modularization, and ontology interoperability",
        "authors": "AD Diehl, TF Meehan, YM Bradford, MH Brush, WM Dahdul, DS Dougall, ...",
        "journal": "Journal of biomedical semantics 7, 1-10, 2016",
        "year": ("2016",),
    },
    {
        "title": "The environment ontology in 2016: bridging domains with increased scope, semantic density, and interoperation",
        "authors": "PL Buttigieg, E Pafilis, SE Lewis, MP Schildhauer, RL Walls, CJ Mungall",
        "journal": "Journal of biomedical semantics 7, 1-12, 2016",
        "year": ("2016",),
    },
    {
        "title": "The Monarch Initiative in 2019: an integrative data and analytic platform connecting phenotypes to genotypes across species",
        "authors": "KA Shefchek, NL Harris, M Gargano, N Matentzoglu, D Unni, M Brush, ...",
        "journal": "Nucleic acids research 48 (D1), D704-D715, 2020",
        "year": ("2020",),
    },
    {
        "title": "Phenotype ontologies: the bridge between genomics and evolution",
        "authors": "PM Mabee, M Ashburner, Q Cronk, GV Gkoutos, M Haendel, E Segerdell, ...",
        "journal": "Trends in ecology & evolution 22 (7), 345-350, 2007",
        "year": ("2007",),
    },
    {
        "title": "PhenomeCentral: a portal for phenotypic and genotypic matchmaking of patients with rare genetic diseases",
        "authors": "OJ Buske, M Girdea, S Dumitriu, B Gallinger, T Hartley, H Trang, ...",
        "journal": "Human mutation 36 (10), 931-940, 2015",
        "year": ("2015",),
    },
    {
        "title": "Identifiers for the 21st century: How to design, provision, and reuse persistent identifiers to maximize utility and impact of life science data",
        "authors": "JA McMurry, N Juty, N Blomberg, T Burdett, T Conlin, N Conte, M Courtot, ...",
        "journal": "PLoS biology 15 (6), e2001414, 2017",
        "year": ("2017",),
    },
    {
        "title": "Unification of multi-species vertebrate anatomy ontologies for comparative biology in Uberon",
        "authors": "MA Haendel, JP Balhoff, FB Bastian, DC Blackburn, JA Blake, Y Bradford, ...",
        "journal": "Journal of biomedical semantics 5, 1-13, 2014",
        "year": ("2014",),
    },
    {
        "title": "PhenoDigm: analyzing curated annotations to associate animal models with human diseases",
        "authors": "D Smedley, A Oellrich, S Köhler, B Ruef, Sanger Mouse Genetics Project, ...",
        "journal": "Database 2013, bat025, 2013",
        "year": ("2013",),
    },
    {
        "title": "Phenotype-driven strategies for exome prioritization of human Mendelian disease genes",
        "authors": "D Smedley, PN Robinson",
        "journal": "Genome medicine 7, 1-11, 2015",
        "year": ("2015",),
    },
    {
        "title": "CLO: the cell line ontology",
        "authors": "S Sarntivijai, Y Lin, Z Xiang, TF Meehan, AD Diehl, UD Vempati, ...",
        "journal": "Journal of biomedical semantics 5 (1), 1-10, 2014",
        "year": ("2014",),
    },
    {
        "title": "Computational evaluation of exome sequence data using human and model organism phenotypes improves diagnostic efficiency",
        "authors": "WP Bone, NL Washington, OJ Buske, DR Adams, J Davis, D Draper, ...",
        "journal": "Genetics in Medicine 18 (6), 608-617, 2016",
        "year": ("2016",),
    },
    {
        "title": "OBO Foundry in 2021: operationalizing open data principles to evaluate ontologies",
        "authors": "R Jackson, N Matentzoglu, JA Overton, R Vita, JP Balhoff, PL Buttigieg, ...",
        "journal": "Database 2021, baab069, 2021",
        "year": ("2021",),
    },
    {
        "title": "Walking the interactome for candidate prioritization in exome sequencing studies of Mendelian diseases",
        "authors": "D Smedley, S Köhler, JC Czeschik, J Amberger, C Bocchini, A Hamosh, ...",
        "journal": "Bioinformatics 30 (22), 3215-3222, 2014",
        "year": ("2014",),
    },
    {
        "title": "Construction and accessibility of a cross-species phenotype ontology along with gene annotations for biomedical research",
        "authors": "S Köhler, SC Doelken, BJ Ruef, S Bauer, N Washington, M Westerfield, ...",
        "journal": "F1000Research 2, 2013",
        "year": ("2013",),
    },
    {
        "title": "The 24th annual Nucleic Acids Research database issue: a look back and upcoming changes",
        "authors": "MY Galperin, XM Fernández-Suárez, DJ Rigden",
        "journal": "Nucleic acids research 45 (D1), D1-D11, 2017",
        "year": ("2017",),
    },
    {
        "title": "Matchmaker exchange",
        "authors": "NLM Sobreira, H Arachchi, OJ Buske, JX Chong, B Hutton, J Foreman, ...",
        "journal": "Current protocols in human genetics 95 (1), 9.31. 1-9.31. 15, 2017",
        "year": ("2017",),
    },
    {
        "title": "Automatic concept recognition using the human phenotype ontology reference and test suite corpora",
        "authors": "T Groza, S Köhler, S Doelken, N Collier, A Oellrich, D Smedley, FM Couto, ...",
        "journal": "Database 2015, bav005, 2015",
        "year": ("2015",),
    },
    {
        "title": "KG-COVID-19: a framework to produce customized knowledge graphs for COVID-19 response",
        "authors": "JT Reese, D Unni, TJ Callahan, L Cappelletti, V Ravanmehr, S Carbon, ...",
        "journal": "Patterns 2 (1), 2021",
        "year": ("2021",),
    },
    {
        "title": "Phenotype ontologies and cross-species analysis for translational research",
        "authors": "PN Robinson, C Webber",
        "journal": "PLoS genetics 10 (4), e1004268, 2014",
        "year": ("2014",),
    },
    {
        "title": "The zebrafish anatomy and stage ontologies: representing the anatomy and development of Danio rerio",
        "authors": "CE Van Slyke, YM Bradford, M Westerfield, MA Haendel",
        "journal": "Journal of biomedical semantics 5, 1-11, 2014",
        "year": ("2014",),
    },
    {
        "title": "Navigating the phenotype frontier: the monarch initiative",
        "authors": "JA McMurry, S Köhler, NL Washington, JP Balhoff, C Borromeo, M Brush, ...",
        "journal": "Genetics 203 (4), 1491-1495, 2016",
        "year": ("2016",),
    },
    {
        "title": "Dead simple OWL design patterns",
        "authors": "D Osumi-Sutherland, M Courtot, JP Balhoff, C Mungall",
        "journal": "Journal of biomedical semantics 8 (1), 1-7, 2017",
        "year": ("2017",),
    },
    {
        "title": "New models for human disease from the International Mouse Phenotyping Consortium",
        "authors": "P Cacheiro, MA Haendel, D Smedley",
        "journal": "Mammalian Genome 30 (5-6), 143-150, 2019",
        "year": ("2019",),
    },
    {
        "title": "Improving ontologies by automatic reasoning and evaluation of logical definitions",
        "authors": "S Köhler, S Bauer, CJ Mungall, G Carletti, CL Smith, P Schofield, ...",
        "journal": "BMC bioinformatics 12 (1), 1-8, 2011",
        "year": ("2011",),
    },
    {
        "title": "The Matchmaker Exchange API: automating patient matching through the exchange of structured phenotypic and genotypic profiles",
        "authors": "OJ Buske, F Schiettecatte, B Hutton, S Dumitriu, A Misyura, L Huang, ...",
        "journal": "Human mutation 36 (10), 922-927, 2015",
        "year": ("2015",),
    },
    {
        "title": "The International Mouse Phenotyping Consortium: comprehensive knockout phenotyping underpinning the study of human disease",
        "authors": "T Groza, FL Gomez, HH Mashhadi, V Muñoz-Fuentes, O Gunes, R Wilson, ...",
        "journal": "Nucleic acids research 51 (D1), D1038-D1045, 2023",
        "year": ("2023",),
    },
    {
        "title": "Interpretable clinical genomics with a likelihood ratio paradigm",
        "authors": "PN Robinson, V Ravanmehr, JOB Jacobsen, D Danis, XA Zhang, ...",
        "journal": "The American Journal of Human Genetics 107 (3), 403-417, 2020",
        "year": ("2020",),
    },
    {
        "title": "Capturing phenotypes for precision medicine",
        "authors": "PN Robinson, CJ Mungall, M Haendel",
        "journal": "Molecular Case Studies 1 (1), a000372, 2015",
        "year": ("2015",),
    },
    {
        "title": "Use of model organism and disease databases to support matchmaking for human disease gene discovery",
        "authors": "CJ Mungall, NL Washington, J Nguyen‐Xuan, C Condit, D Smedley, ...",
        "journal": "Human mutation 36 (10), 979-984, 2015",
        "year": ("2015",),
    },
    {
        "title": "Modelling kidney disease using ontology: insights from the Kidney Precision Medicine Project",
        "authors": "E Ong, LL Wang, J Schaub, JF O’Toole, B Steck, AZ Rosenberg, F Dowd, ...",
        "journal": "Nature Reviews Nephrology 16 (11), 686-696, 2020",
        "year": ("2020",),
    },
    {
        "title": "A unified anatomy ontology of the vertebrate skeletal system",
        "authors": "WM Dahdul, JP Balhoff, DC Blackburn, AD Diehl, MA Haendel, BK Hall, ...",
        "journal": "PloS one 7 (12), e51070, 2012",
        "year": ("2012",),
    },
    {
        "title": "A census of disease ontologies",
        "authors": "MA Haendel, JA McMurry, R Relevo, CJ Mungall, PN Robinson, ...",
        "journal": "Annual Review of Biomedical Data Science 1, 305-331, 2018",
        "year": ("2018",),
    },
    {
        "title": "Nose to tail, roots to shoots: spatial descriptors for phenotypic diversity in the Biological Spatial Ontology",
        "authors": "WM Dahdul, H Cui, PM Mabee, CJ Mungall, D Osumi-Sutherland, ...",
        "journal": "Journal of biomedical semantics 5, 1-13, 2014",
        "year": ("2014",),
    },
    {
        "title": "Interpretable prioritization of splice variants in diagnostic next-generation sequencing",
        "authors": "D Danis, JOB Jacobsen, LC Carmody, MA Gargano, JA McMurry, ...",
        "journal": "The American Journal of Human Genetics 108 (9), 1564-1577, 2021",
        "year": ("2021",),
    },
    {
        "title": "Uberon: towards a comprehensive multi-species anatomy ontology",
        "authors": "M Haendel, G Gkoutos, S Lewis, C Mungall",
        "journal": "Nature precedings, 1-1, 2009",
        "year": ("2009",),
    },
    {
        "title": "Semantic integration of clinical laboratory tests from electronic health records for deep phenotyping and biomarker discovery",
        "authors": "XA Zhang, A Yates, N Vasilevsky, JP Gourdine, TJ Callahan, LC Carmody, ...",
        "journal": "NPJ digital medicine 2 (1), 32, 2019",
        "year": ("2019",),
    },
    {
        "title": "An improved phenotype-driven tool for rare mendelian variant prioritization: benchmarking exomiser on real patient whole-exome data",
        "authors": "V Cipriani, N Pontikos, G Arno, PI Sergouniotis, E Lenassi, P Thawong, ...",
        "journal": "Genes 11 (4), 460, 2020",
        "year": ("2020",),
    },
    {
        "title": "The case for open science: rare diseases",
        "authors": "YR Rubinstein, PN Robinson, WA Gahl, P Avillach, G Baynam, ...",
        "journal": "JAMIA open 3 (3), 472-486, 2020",
        "year": ("2020",),
    },
    {
        "title": "Plain-language medical vocabulary for precision diagnosis",
        "authors": "NA Vasilevsky, ED Foster, ME Engelstad, L Carmody, M Might, ...",
        "journal": "Nature genetics 50 (4), 474-476, 2018",
        "year": ("2018",),
    },
    {
        "title": "Prediction of Human Phenotype Ontology terms by means of hierarchical ensemble methods",
        "authors": "M Notaro, M Schubach, PN Robinson, G Valentini",
        "journal": "BMC bioinformatics 18 (1), 1-18, 2017",
        "year": ("2017",),
    },
    {
        "title": "Anatomy Ontologies for Bioinformatics: Principles and Practice",
        "authors": "M Haendel, F Neuhaus, D Osumi-Sutherland, PM Mabee, JLV Mejino Jr, ...",
        "year": ("2008",),
    },
    {
        "title": "Encoding clinical data with the human phenotype ontology for computational differential diagnostics",
        "authors": "S Köhler, NC Øien, OJ Buske, T Groza, JOB Jacobsen, C McNamara, ...",
        "journal": "Current protocols in human genetics 103 (1), e92, 2019",
        "year": ("2019",),
    },
    {
        "title": "Biolink Model: A universal schema for knowledge graphs in clinical, biomedical, and translational science",
        "authors": "DR Unni, SAT Moxon, M Bada, M Brush, R Bruskiewich, JH Caufield, ...",
        "journal": "Clinical and translational science 15 (8), 1848-1855, 2022",
        "year": ("2022",),
    },
    {
        "title": "Disease insights through cross-species phenotype comparisons",
        "authors": "MA Haendel, N Vasilevsky, M Brush, HS Hochheiser, J Jacobsen, ...",
        "journal": "Mammalian Genome 26, 548-555, 2015",
        "year": ("2015",),
    },
    {
        "title": "The GA4GH Phenopacket schema defines a computable representation of clinical data",
        "authors": "JOB Jacobsen, M Baudis, GS Baynam, JS Beckmann, S Beltran, ...",
        "journal": "Nature biotechnology 40 (6), 817-820, 2022",
        "year": ("2022",),
    },
    {
        "title": "matchbox: An open‐source tool for patient matching via the Matchmaker Exchange",
        "authors": "H Arachchi, MH Wojcik, B Weisburd, JOB Jacobsen, E Valkanas, S Baxter, ...",
        "journal": "Human mutation 39 (12), 1827-1834, 2018",
        "year": ("2018",),
    },
    {
        "title": "Metrics to assess value of biomedical digital repositories: response to RFI NOT-OD-16-133",
        "authors": "M Haendel, A Su, J McMurry, CG Chute, C Mungall, B Good, C Wu, ...",
        "journal": "Geneva: Zenodo, 2016",
        "year": ("2016",),
    },
    {
        "title": "Laying a community-based foundation for data-driven semantic standards in environmental health sciences",
        "authors": "CJ Mattingly, R Boyles, CP Lawler, AC Haugen, A Dearry, M Haendel",
        "journal": "Environmental health perspectives 124 (8), 1136-1140, 2016",
        "year": ("2016",),
    },
    {
        "title": "Emerging semantics to link phenotype and environment",
        "authors": "AE Thessen, DE Bunker, PL Buttigieg, LD Cooper, WM Dahdul, ...",
        "journal": "PeerJ 3, e1470, 2015",
        "year": ("2015",),
    },
    {
        "title": "Ontology-based data integration for advancing toxicological knowledge",
        "authors": "RR Boyles, AE Thessen, A Waldrop, MA Haendel",
        "journal": "Current Opinion in Toxicology 16, 67-74, 2019",
        "year": ("2019",),
    },
    {
        "title": "Mondo Disease Ontology: harmonizing disease concepts across the world",
        "authors": "N Vasilevsky, S Essaid, N Matentzoglu, NL Harris, M Haendel, ...",
        "journal": "CEUR Workshop Proceedings, CEUR-WS 2807, 2020",
        "year": ("2020",),
    },
    {
        "title": "A simple standard for sharing ontological mappings (SSSOM)",
        "authors": "N Matentzoglu, JP Balhoff, SM Bello, C Bizon, M Brush, TJ Callahan, ...",
        "journal": "Database 2022, 2022",
        "year": ("2022",),
    },
    {
        "title": "Proper attribution for curation and maintenance of research collections: metadata recommendations of the RDA/TDWG Working Group",
        "authors": "AE Thessen, M Woodburn, D Koureas, D Paul, M Conlon, DP Shorthouse, ...",
        "journal": "Data Science Journal 18, 54-54, 2019",
        "year": ("2019",),
    },
    {
        "title": "SEPIO: A Semantic Model for the Integration and Analysis of Scientific Evidence.",
        "authors": "MH Brush, KA Shefchek, MA Haendel",
        "journal": "ICBO/BioCreative, 2016",
        "year": ("2016",),
    },
    {
        "title": "Mondo: Unifying diseases for the world, by the world",
        "authors": "NA Vasilevsky, NA Matentzoglu, S Toro, JE Flack IV, H Hegde, DR Unni, ...",
        "journal": "medRxiv, 2022.04. 13.22273750, 2022",
        "year": ("2022",),
    },
    {
        "title": "Community approaches for integrating environmental exposures into human models of disease",
        "authors": "AE Thessen, CJ Grondin, RD Kulkarni, S Brander, L Truong, ...",
        "journal": "Environmental health perspectives 128 (12), 125002, 2020",
        "year": ("2020",),
    },
    {
        "title": "k-BOOM: A Bayesian approach to ontology structure inference, with applications in disease ontology construction",
        "authors": "CJ Mungall, S Koehler, P Robinson, I Holmes, M Haendel",
        "journal": "bioRxiv, 048843, 2016",
        "year": ("2016",),
    },
    {
        "title": "Prediction of human gene-phenotype associations by exploiting the hierarchical structure of the human phenotype ontology",
        "authors": "G Valentini, S Köhler, M Re, M Notaro, PN Robinson",
        "journal": "Bioinformatics and Biomedical Engineering: Third International Conference …, 2015",
        "year": ("2015",),
    },
    {
        "title": "Ontology based molecular signatures for immune cell types via gene expression analysis",
        "authors": "TF Meehan, NA Vasilevsky, CJ Mungall, DS Dougall, MA Haendel, ...",
        "journal": "BMC bioinformatics 14 (1), 1-15, 2013",
        "year": ("2013",),
    },
    {
        "title": "The RD‐Connect Genome‐Phenome Analysis Platform: Accelerating diagnosis, research, and gene discovery for rare diseases",
        "authors": "S Laurie, D Piscia, L Matalonga, A Corvó, M Fernández‐Callejo, ...",
        "journal": "Human mutation 43 (6), 717-733, 2022",
        "year": ("2022",),
    },
    {
        "title": "Ontology Development Kit: a toolkit for building, maintaining and standardizing biomedical ontologies",
        "authors": "N Matentzoglu, D Goutte-Gattat, SZK Tan, JP Balhoff, S Carbon, ...",
        "journal": "Database 2022, baac087, 2022",
        "year": ("2022",),
    },
    {
        "title": "The GA4GH Phenopacket schema: A computable representation of clinical data for precision medicine",
        "authors": "JOB Jacobsen, M Baudis, GS Baynam, JS Beckmann, S Beltran, ...",
        "journal": "medRxiv, 2021.11. 27.21266944, 2021",
        "year": ("2021",),
    },
    {
        "title": "Ontologies, knowledge representation, and machine learning for translational research: recent contributions",
        "authors": "PN Robinson, MA Haendel",
        "journal": "Yearbook of medical informatics 29 (01), 159-162, 2020",
        "year": ("2020",),
    },
    {
        "title": "Transforming the study of organisms: Phenomic data models and knowledge bases",
        "authors": "AE Thessen, RL Walls, L Vogt, J Singer, R Warren, PL Buttigieg, ...",
        "journal": "PLoS computational biology 16 (11), e1008376, 2020",
        "year": ("2020",),
    },
    {
        "title": "From SNOMED CT to Uberon: transferability of evaluation methodology between similarly structured ontologies",
        "authors": "G Elhanan, C Ochs, JLV Mejino Jr, H Liu, CJ Mungall, Y Perl",
        "journal": "Artificial intelligence in medicine 79, 9-14, 2017",
        "year": ("2017",),
    },
    {
        "title": "Phenotype Ontologies Traversing All The Organisms (POTATO) workshop aims to reconcile logical definitions across species. Workshop Report",
        "authors": "N Matentzoglu, J Balhoff, S Bello, C Boerkoel, Y Bradford, L Carmody, ...",
        "year": ("2018",),
    },
    {
        "title": "The influence of disease categories on gene candidate predictions from model organism phenotypes",
        "authors": "A Oellrich, S Koehler, N Washington, C Mungall, S Lewis, M Haendel, ...",
        "journal": "Journal of Biomedical Semantics 5 (1), 1-14, 2014",
        "year": ("2014",),
    },
    {
        "title": "How good is your phenotyping? Methods for quality assessment",
        "authors": "NL Washington, MA Haendel, S Köhler, SE Lewis, P Robinson, ...",
        "journal": "Proceedings of Phenotype Day 2014, 2014",
        "year": ("2014",),
    },
    {
        "title": "Unifying the identification of biomedical entities with the Bioregistry",
        "authors": "CT Hoyt, M Balk, TJ Callahan, D Domingo-Fernández, MA Haendel, ...",
        "journal": "Scientific data 9 (1), 714, 2022",
        "year": ("2022",),
    },
    {
        "title": "Progress toward a universal biomedical data translator",
        "authors": "K Fecho, AE Thessen, SE Baranzini, C Bizon, JJ Hadlock, S Huang, ...",
        "journal": "Clinical and Translational Science 15 (8), 1838-1847, 2022",
        "year": ("2022",),
    },
    {
        "title": "Identification of UBAP1 mutations in juvenile hereditary spastic paraplegia in the 100,000 Genomes Project",
        "authors": "T Bourinaris, D Smedley, V Cipriani, I Sheikh, A Athanasiou-Fragkouli, ...",
        "journal": "European Journal of Human Genetics 28 (12), 1763-1768, 2020",
        "year": ("2020",),
    },
    {
        "title": "Biodiversity informatics",
        "authors": "CS Parr, AE Thessen",
        "journal": "Ecological Informatics: Data Management and Knowledge Discovery, 375-399, 2018",
        "year": ("2018",),
    },
    {
        "title": "Phenotype‐driven approaches to enhance variant prioritization and diagnosis of rare disease",
        "authors": "JOB Jacobsen, C Kelly, V Cipriani, GE Research Consortium, CJ Mungall, ...",
        "journal": "Human mutation 43 (8), 1071-1081, 2022",
        "year": ("2022",),
    },
    {
        "title": "Data-driven method to enhance craniofacial and oral phenotype vocabularies",
        "authors": "R Mishra, A Burke, B Gitman, P Verma, M Engelstad, MA Haendel, ...",
        "journal": "The Journal of the American Dental Association 150 (11), 933-939. e2, 2019",
        "year": ("2019",),
    },
    {
        "title": "From Reductionism to Reintegration: Solving society’s most pressing problems requires building bridges between data types across the life sciences",
        "authors": "AE Thessen, P Bogdan, DJ Patterson, TM Casey, C Hinojo-Hinojo, ...",
        "journal": "PLoS Biology 19 (3), e3001129, 2021",
        "year": ("2021",),
    },
    {
        "title": "The Linked Data Modeling Language (LinkML): A General-Purpose Data Modeling Framework Grounded in Machine-Readable Semantics.",
        "authors": "SAT Moxon, H Solbrig, DR Unni, D Jiao, RM Bruskiewich, JP Balhoff, ...",
        "journal": "ICBO, 148-151, 2021",
        "year": ("2021",),
    },
    {
        "title": "Catalyzing knowledge-driven discovery in environmental health sciences through a community-driven harmonized language",
        "authors": "SD Holmgren, RR Boyles, RD Cronk, CG Duncan, RK Kwok, RM Lunn, ...",
        "journal": "International Journal of Environmental Research and Public Health 18 (17), 8985, 2021",
        "year": ("2021",),
    },
    {
        "title": "Representing glycophenotypes: semantic unification of glycobiology resources for disease discovery",
        "authors": "JPF Gourdine, MH Brush, NA Vasilevsky, K Shefchek, S Köhler, ...",
        "journal": "Database 2019, baz114, 2019",
        "year": ("2019",),
    },
    {
        "title": "Ontology mapping framework with feature extraction and semantic embeddings",
        "authors": "M Chandrashekar, R Nagulapati, Y Lee",
        "journal": "2018 IEEE International Conference on Healthcare Informatics Workshop (ICHI …, 2018",
        "year": ("2018",),
    },
    {
        "title": "Geoinformatics: Toward an integrative view of Earth as a system",
        "authors": "AK Sinha, AE Thessen, CG Barnes",
        "journal": "The Web of Geological Sciences: Advances, Impacts, and Interactions …, 2013",
        "year": ("2013",),
    },
    {
        "title": "Prenatal phenotyping: A community effort to enhance the Human Phenotype Ontology",
        "authors": "F Dhombres, P Morgan, BP Chaudhari, I Filges, TN Sparks, P Lapunzina, ...",
        "journal": "American Journal of Medical Genetics Part C: Seminars in Medical Genetics …, 2022",
        "year": ("2022",),
    },
    {
        "title": "The Sickle Cell Disease Ontology: Recent development and expansion of the universal sickle cell knowledge representation",
        "authors": "GK Mazandu, J Hotchkiss, V Nembaware, A Wonkam, N Mulder",
        "journal": "Database 2022, baac014, 2022",
        "year": ("2022",),
    },
    {
        "title": "Gold-standard ontology-based anatomical annotation in the CRAFT Corpus",
        "authors": "M Bada, N Vasilevsky, WA Baumgartner Jr, M Haendel, LE Hunter",
        "journal": "Database 2017, bax087, 2017",
        "year": ("2017",),
    },
    {
        "title": "Enhancing the human phenotype ontology for use by the layperson",
        "authors": "NA Vasilevsky, M Engelstad, ED Foster, CJ Mungall, PN Robinson, ...",
        "year": ("2016",),
    },
    {
        "title": "An improved phenotype-driven tool for rare mendelian variant prioritization: Benchmarking exomiser on real patient whole-exome data. Genes. 2020; 11 (4)",
        "authors": "V Cipriani, N Pontikos, G Arno, PI Sergouniotis, E Lenassi, P Thawong, ...",
        "year": ("",),
    },
    {
        "title": "The Environmental Conditions, Treatments, and Exposures Ontology (ECTO): connecting toxicology and exposure to human health and beyond",
        "authors": "LE Chan, AE Thessen, WD Duncan, N Matentzoglu, C Schmitt, ...",
        "journal": "Journal of Biomedical Semantics 14 (1), 1-12, 2023",
        "year": ("2023",),
    },
    {
        "title": "Evaluation of phenotype-driven gene prioritization methods for Mendelian diseases",
        "authors": "JOB Jacobsen, C Kelly, V Cipriani, PN Robinson, D Smedley",
        "journal": "Briefings in bioinformatics 23 (5), bbac188, 2022",
        "year": ("2022",),
    },
    {
        "title": "Haendel M. k-BOOM: a Bayesian approach to ontology structure inference, with applications in disease ontology construction. bioRxiv 2019: 048843",
        "authors": "CJ Mungall, S Koehler, P Robinson, I Holmes",
        "journal": "doi 10 (048843), 048843, 2019",
        "year": ("2019",),
    },
    {
        "title": "Structured prompt interrogation and recursive extraction of semantics (SPIRES): A method for populating knowledge bases using zero-shot learning",
        "authors": "JH Caufield, H Hegde, V Emonet, NL Harris, MP Joachimiak, ...",
        "journal": "arXiv preprint arXiv:2304.02711, 2023",
        "year": ("2023",),
    },
    {
        "title": "The Xenopus phenotype ontology: bridging model organism phenotype data to human health and development",
        "authors": "ME Fisher, E Segerdell, N Matentzoglu, MJ Nenni, JD Fortriede, S Chu, ...",
        "journal": "BMC bioinformatics 23 (1), 1-15, 2022",
        "year": ("2022",),
    },
    {
        "title": "The Clinical Variant Analysis Tool: Analyzing the evidence supporting reported genomic variation in clinical practice",
        "authors": "HL Chin, N Gazzaz, S Huynh, I Handra, L Warnock, A Moller-Hansen, ...",
        "journal": "Genetics in Medicine 24 (7), 1512-1522, 2022",
        "year": ("2022",),
    },
    {
        "title": "An algorithmic framework for isoform-specific functional analysis",
        "authors": "G Karlebach, L Carmody, JC Sundaramurthi, E Casiraghi, P Hansen, ...",
        "journal": "Biorxiv, 2022.05. 13.491897, 2022",
        "year": ("2022",),
    },
    {
        "title": "KG-Microbe: A Reference Knowledge-Graph and Platform for Harmonized Microbial Information.",
        "authors": "MP Joachimiak, H Hegde, WD Duncan, JT Reese, L Cappelletti, ...",
        "journal": "ICBO, 131-133, 2021",
        "year": ("2021",),
    },
    {
        "title": "Standardizing Ontology Workflows Using ROBOT.",
        "authors": "R Tauber, JP Balhoff, E Douglass, C Mungall, JA Overton",
        "journal": "ICBO, 2018",
        "year": ("2018",),
    },
    {
        "title": "Gold-Standard Ontology-Based Annotation of Concepts in Biomedical Text in the CRAFT Corpus: Updates and Extensions.",
        "authors": "M Bada, NA Vasilevsky, MA Haendel, L Hunter",
        "journal": "ICBO/BioCreative, 2016",
        "year": ("2016",),
    },
    {
        "title": "Uberon ontology",
        "authors": "CJ Mungall, M Haendel, W Dahdul, N Ibrahim, E Segerdell, DC Blackburn, ...",
        "year": ("2016",),
    },
    {
        "title": "GA4GH phenopackets: A practical introduction",
        "authors": "MS Ladewig, JOB Jacobsen, AH Wagner, D Danis, B El Kassaby, ...",
        "journal": "Advanced Genetics 4 (1), 2200016, 2023",
        "year": ("2023",),
    },
    {
        "title": "Phenotype-aware prioritisation of rare Mendelian disease variants",
        "authors": "C Kelly, A Szabo, N Pontikos, G Arno, PN Robinson, JOB Jacobsen, ...",
        "journal": "Trends in Genetics, 2022",
        "year": ("2022",),
    },
    {
        "title": "Implementation of Zebrafish Ontologies for Toxicology Screening",
        "authors": "AE Thessen, S Marvel, JC Achenbach, S Fischer, MA Haendel, ...",
        "journal": "Frontiers in Toxicology 4, 8, 2022",
        "year": ("2022",),
    },
    {"title": "384 Phenopackets", "authors": "PN Robinson", "journal": "Zenodo, 2020", "year": ("2020",)},
    {"title": "The Human Phenotype Ontology", "authors": "S Köhler, M Haendel, P Robinson", "year": ("2019",)},
    {
        "title": "“Opposite-of”-information improves similarity calculations in phenotype ontologies",
        "authors": "S Köhler, PN Robinson, CJ Mungall",
        "journal": "bioRxiv, 108977, 2017",
        "year": ("2017",),
    },
    {
        "title": "k-BOOM: A Bayesian approach to ontology structure inference, with applications in disease ontology construction. bioRxiv",
        "authors": "CJ Mungall, S Koehler, P Robinson, I Holmes, M Haendel",
        "journal": "Cold Spring Harbor Labs Journals, 2016",
        "year": ("2016",),
    },
    {
        "title": "The Monarch Initiative: Insights across species reveal human disease mechanisms",
        "authors": "C Mungall, J McMurry, S Koehler, J Balhoff, C Borromeo, M Brush, ...",
        "journal": "bioRxiv, 2016",
        "year": ("2016",),
    },
    {
        "title": "What is an anatomy ontology?",
        "authors": "RE Druzinsky, CJ Mungall, MA Haendel, H Lapp, P Mabee",
        "journal": "University of Illinois at Chicago, 2013",
        "year": ("2013",),
    },
    {
        "title": "The Monarch Initiative: an integrative data and analytic platform connecting phenotypes to genotypes across species 1: CAS: 528: DC% 2BC1cXhslWhsLk% 3D 10.1093/nar/gkw1128 …",
        "authors": "CJ Mungall, JA McMurry, S Köhler, JP Balhoff, C Borromeo, M Brush",
        "journal": "D712-D722, 0",
        "year": ("",),
    },
    {
        "title": "International Mouse Phenotyping Consortium and the Monarch Initiative(2019). New models for human disease from the International Mouse Phenotyping Consortium",
        "authors": "P Cacheiro, MA Haendel, D Smedley",
        "journal": "Mamm. Genome 30, 143-150, 0",
        "year": ("",),
    },
    {
        "title": "SEPIO: A Semantic Model for the Integration and Analysis of Scientific Evidence. in\u200b ICBO",
        "authors": "MH Brush, K Shefchek, M Haendel",
        "journal": "BioCreative, 0",
        "year": ("",),
    },
    {
        "title": "Uberon: towards a comprehensive multi-species anatomy ontology. 2009",
        "authors": "M Haendel, G Gkoutos, S Lewis, C Mungall",
        "year": ("",),
    },
    {
        "title": "Kö hler S, Balhoff JP, Borromeo C, et al. 2017. The Monarch Initiative: an integrative data and analytic platform connecting phenotypes to genotypes across species",
        "authors": "CJ Mungall, JA McMurry",
        "journal": "Nucleic Acids Res 45, D712-D722, 0",
        "year": ("",),
    },
    {
        "title": "an integrative data and analytic platform connecting phenotypes to genotypes across species| Nucleic Acids Research| Oxford Academic",
        "authors": "M Initiative",
        "year": ("",),
    },
    {
        "title": "Ontologizing health systems data at scale: making translational discovery a reality",
        "authors": "TJ Callahan, AL Stefanski, JM Wyrwa, C Zeng, A Ostropolets, JM Banda, ...",
        "journal": "NPJ Digital Medicine 6 (1), 89, 2023",
        "year": ("2023",),
    },
    {
        "title": "KG-Hub--Building and Exchanging Biological Knowledge Graphs",
        "authors": "JH Caufield, T Putman, K Schaper, DR Unni, H Hegde, TJ Callahan, ...",
        "journal": "arXiv preprint arXiv:2302.10800, 2023",
        "year": ("2023",),
    },
    {
        "title": "The bioregistry: Unifying the identification of biomedical entities th rough an integrative, open, community-driven metaregistry",
        "authors": "CT Hoyt, M Balk, TJ Callahan, D Domingo-Fernández, MA Haendel, ...",
        "journal": "bioRxiv, 2022",
        "year": ("2022",),
    },
    {
        "title": "Innovative approaches to combining genotype, phenotype, epigenetic, and exposure data for precision diagnostics",
        "authors": "MA Haendel, MG Kann, NL Washington",
        "journal": "Biocomputing 2016: Proceedings of the Pacific Symposium, 93-95, 2016",
        "year": ("2016",),
    },
    {
        "title": "Use of animal models for exome prioritization of rare disease genes",
        "authors": "D Smedley, S Kohler, W Bone, A Oellrich, J Jacobsen, ...",
        "journal": "Orphanet Journal of Rare Diseases 9, 1-2, 2014",
        "year": ("2014",),
    },
    {
        "title": "Phenopacket-tools: Building and validating GA4GH Phenopackets",
        "authors": "D Danis, JOB Jacobsen, AH Wagner, T Groza, MA Beckwith, L Rekerle, ...",
        "journal": "Plos one 18 (5), e0285433, 2023",
        "year": ("2023",),
    },
    {
        "title": "The Ontology of Biological Attributes (OBA)—computational traits for the life sciences",
        "authors": "R Stefancsik, JP Balhoff, MA Balk, RL Ball, SM Bello, AR Caron, ...",
        "journal": "Mammalian Genome, 1-15, 2023",
        "year": ("2023",),
    },
    {
        "title": "On the limitations of large language models in clinical diagnosis",
        "authors": "J Reese, D Danis, JH Caufield, E Casiraghi, G Valentini, CJ Mungall, ...",
        "journal": "medRxiv, 2023.07. 13.23292613, 2023",
        "year": ("2023",),
    },
    {
        "title": "Predicting nutrition and environmental factors associated with female reproductive disorders using a knowledge graph and random forests",
        "authors": "LE Chan, E Casiraghi, T Putman, J Reese, QE Harmon, K Schaper, ...",
        "journal": "medRxiv, 2023.07. 14.23292679, 2023",
        "year": ("2023",),
    },
    {
        "title": "The Medical Action Ontology: A Tool for Annotating and Analyzing Treatments and Clinical Management of Human Disease",
        "authors": "LC Carmody, MA Gargano, S Toro, NA Vasilevsky, MP Adam, H Blau, ...",
        "journal": "medRxiv, 2023.07. 13.23292612, 2023",
        "year": ("2023",),
    },
    {
        "title": "129. Standardization of cancer terminology in the Mondo Disease Ontology",
        "authors": "N Vasilevsky, N Matentzoglu, S Toro, J Flack, A Hamosh, P Robinson, ...",
        "journal": "Cancer Genetics 268, 41, 2022",
        "year": ("2022",),
    },
    {
        "title": "Classifying Animal Breeds with the Vertebrate Breed Ontology (VBO)",
        "authors": "S Toro, N Matentzoglu, KR Mullen, N Vasilevsky, HM Rando, M Haendel, ...",
        "journal": "International Conference on Biomedical Ontology, 2022",
        "year": ("2022",),
    },
    {
        "title": "GA4GH Phenopackets: A Practical Introduction",
        "authors": "MS Ladewig, JOB Jacobsen, AH Wagner, D Danis, B El Kassaby, ...",
        "journal": "Wiley, 2022",
        "year": ("2022",),
    },
    {
        "title": "The GA4GH Phenopacket schema: A computable representation of clinical data for precision medicine",
        "authors": "P Schofield, J Jacobson, J Baynam",
        "journal": "Nature Research, 2022",
        "year": ("2022",),
    },
    {
        "title": "Rare-disease data standards",
        "authors": "PN Robinson, H Graessner",
        "journal": "Bundesgesundheitsblatt, Gesundheitsforschung, Gesundheitsschutz 65 (11), 1126, 2022",
        "year": ("2022",),
    },
    {
        "title": "What Should be the Minimum Requirements for Making FAIR Ontology Alignments?",
        "authors": "C Trojahn, N Matentzoglu",
        "year": ("2022",),
    },
    {
        "title": "A Simple Standard for Ontological Mappings 2022: Updates of data model and outlook",
        "authors": "N Matentzoglu, J Flack, J Graybeal, NL Harris, HB Hegde, CT Hoyt, H Kim, ...",
        "journal": "CEUR Workshop Proceedings 3324, 61-66, 2022",
        "year": ("2022",),
    },
    {
        "title": "Ranking variant pathogenicity using Exomiser facilitated the identification of the missing second mutation in three recessive cases of congenital myopathy",
        "authors": "Y Lei, W Yang, HSS Chan",
        "journal": "The 20th Asian and Oceanian Myopathy Center (AOMC) Meeting in conjunction …, 2022",
        "year": ("2022",),
    },
    {
        "title": "A Semantic Model Leveraging Pattern-based Ontology Terms to Bridge Environmental Exposures and Health Outcomes",
        "authors": "LE Chan, NA Vasilevsky, A Thessen, N Matentzoglu, WD Duncan, ...",
        "journal": "Proceedings http://ceur-ws. org ISSN 1613, 0073, 2021",
        "year": ("2021",),
    },
    {
        "title": "Reclassification of Infectious Disease in the Mondo Disease Ontology",
        "authors": "N Vasilevsky, S Toro, N Matentzoglu, D Jiao, M Haendel, PN Robinson, ...",
        "journal": "Proceedings http://ceur-ws. org ISSN 1613, 0073, 2021",
        "year": ("2021",),
    },
    {
        "title": "Exomiser and Genomiser",
        "authors": "JOB Jacobsen, D Smedley, P Robinson",
        "journal": "Computational Exome and Genome Analysis, 387-406, 2017",
        "year": ("2017",),
    },
    {
        "title": "An Improved Bioinformatics Tool for Rare Disease Variant Prioritization: The Exomiser 9.0. 1 in Clinical Practice",
        "authors": "V Cipriani, N Pontikos, G Arno, AR Webster, AT Moore, KJ Carss, ...",
        "journal": "HUMAN HEREDITY 83 (1), 5-6, 2017",
        "year": ("2017",),
    },
    {
        "title": "Aligning the Human Phenotype and Mammalian Phenotype Ontology using Dead Simple Ontology Design Patterns.",
        "authors": "NA Vasilevsky, JP Balhoff, CJ Mungall, D Osumi-Sutherland, S Köhler, ...",
        "journal": "ICBO, 2017",
        "year": ("2017",),
    },
    {
        "title": "Tools for exploring mouse models of human disease",
        "authors": "M Haendel, I Papatheodorou, A Oellrich, CJ Mungall, N Washington, ...",
        "journal": "Drug Discovery Today: Disease Models 20, 21-26, 2016",
        "year": ("2016",),
    },
    {
        "title": "Tudor Groza, Sebastian Köhler, 3, 25 Dawid Moldenhauer, 3, 4 Nicole Vasilevsky, 5",
        "authors": "G Baynam, T Zemojtel, LM Schriml, WA Kibbe, PN Schofield, T Beck, ...",
        "journal": "The American Journal of Human Genetics 124 (111), 97-111, 2015",
        "year": ("2015",),
    },
    {
        "title": "/releases/2014-03-28/uberon",
        "authors": "C Mungall",
        "journal": "Uberon Website, 2014",
        "year": ("2014",),
    },
    {
        "title": "Improved exome prioritization of disease genes through cross-species phenotype comparison",
        "authors": "NR Peter, K Sebastian, O Anika, W Kai, JM Christopher, EL Suzanna, ...",
        "journal": "Genome Research 24 (2), 340-348, 2013",
        "year": ("2013",),
    },
    {"title": "MONDO", "authors": "Monarch Initiative", "journal": "(No Title), 0", "year": ("",)},
    {
        "title": "Curating databases en masse: a semantic integration approach for disease discovery",
        "authors": "MA Haendel",
        "year": ("",),
    },
    {
        "title": "Environmental Health Language Collaborative (EHLC): a route to environmental health science data harmonization",
        "authors": "AM Masci, S Holmgren, C Schmitt, R Habre, AE Thessen, R Boyles, ...",
        "year": ("",),
    },
    {
        "title": "Translational Genomics for Rare Disease",
        "authors": "PN Robinson",
        "journal": "Mission–Innovation: Telematics, eHealth and High-Definition Medicine in …, 0",
        "year": ("",),
    },
    {
        "title": "Toggle navigation BBOP home",
        "authors": "GHT Page, G Ontology, M Initiative, P First, N Biomedical, OBO Foundry, ...",
        "year": ("",),
    },
    {"title": "OBO Foundry", "authors": "GHT Page, G Ontology, M Initiative, P First, N Biomedical", "year": ("",)},
    {"title": "Monarch Initiative", "authors": "GHT Page, G Ontology", "year": ("",)},
    {
        "title": "Finding Useful Data Across Multiple Biomedical Data Repositories Using Datamed",
        "authors": "NIH Allen Dearry–NIEHS, H Berman-Rutgers, J Lyle-ICPSR, ...",
        "year": ("",),
    },
]

    # example_pubmed_query = "https://pubmed.ncbi.nlm.nih.gov/suggestions/?term=improved%20exome%20prioritization%20of%20disease%20genes%20through%20cross-species%20phenotype%20comparison"

    # scholarly_titles = get_pub_titles_scholarly()
    # scholarly_titles_file = Path(__file__).parent / "scholarly_titles.py"
    # with open(scholarly_titles_file, "w") as f:
    #     f.write(f"scholarly_titles = {scholarly_titles}")

    # print(f"{'-'*80}\nWriting output to: {OUTFILE}\n")
    # pubs = get_pubs()
    # with open(f"{Path(__file__).parent / 'pubs.py'}", "w") as f:
    #     f.write(f"pubs = {pubs}")

    # Get titles of monarch publications
    # titles = get_pub_titles()
    # pp(titles)
    # title_file = Path(__file__).parent / 'titles.py'
    # with open(title_file, 'w') as f:
    # f.write(f"titles = {titles}")

    # Get pubmed IDs of monarch publication titles
    search_results = search_for_doi_alt(pubs[50])
    print(search_results[0].keys())
    for result in search_results:
        try:
            print(result["container-title"])
        except KeyError:
            print(result["title"])
    # dois = get_all_dois(pubs)
    # pmid_file = Path(__file__).parent / "pubmed_search_result.py"
    # with open(pmid_file, "w") as f:
    #     f.write(f"dois = {dois}")

    # Write output to file
    # with open(OUTFILE, 'w') as f:
    #     json.dump(pubs, f, indent=2)
