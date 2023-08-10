"""
This script uses the scholarly package to get the publications of the Monarch Initiative
from Google Scholar. It then writes the publications to a json file in the format:
    [
        {
            'year': 2020,
            'items': [
                {
                    'title': 'Publication Title',
                    'authors': 'Author 1, Author 2, Author 3',
                    'journal': 'Journal Name',
                    'pub_year': 2020,
                    'issue': 'Volume(Issue):Pages',
                    'link': 'Link to publication'
                },
                ...
    ]

Note: scholarly doesn't always return the same keys for each publication, so this script
should be used to get the publications, but the json file should be manually edited to
ensure that the correct information is displayed for each publication.
"""
import json
from pathlib import Path
from scholarly import scholarly

outdir = Path(__file__).parent.parent / 'frontend' / 'src' / 'pages' / 'about'
print(f"{'-'*80}\nWriting publications to {outdir}")

import pprint
pp = pprint.PrettyPrinter(indent=2).pprint


### Search for publications which cite the Monarch Initiative
author = scholarly.search_author_id(id = 'zmUEDj0AAAAJ')

### Fill in the publication details for the author
scholarly.fill(author, sections=['publications'], sortby='year')
publications = author['publications']

### Construct a list of publications by year
pubs_by_year = []
for p in publications:
    scholarly.fill(p, sections=['bib'])
    bib = p['bib']

    # Check for missing keys
    missing = [j for j in ['title', 'author', 'pub_year'] if j not in bib]      
    missing.append('journal/publisher' if 'journal' not in bib and 'publisher' not in bib else '')
    missing.append('pub_url' if 'pub_url' not in p else '')
    missing = [j for j in missing if j != '']
    
    # Debug info
    print(f"{'-'*80}\nProcessing publication: {bib['title']}")
    if missing:
        print(f"Missing keys: {missing}")

    link = f"[Link]({p['pub_url']})" if 'pub_url' in p else ''        
    pub_year = bib['pub_year'] if 'pub_year' in bib else 'N/A'
    journal = bib['journal'] if 'journal' in bib else bib['publisher'] if 'publisher' in bib else bib['citation'] if 'citation' in bib else 'Unknown'
    issue = ''
    if 'volume' in bib:
        issue += f"{bib['volume']}"
    if 'number' in bib:
        issue += f"({bib['number']})"
    if 'pages' in bib:
        issue += f":{bib['pages']}"

    try:
        pub = {
            'title': bib['title'],
            'authors': ', '.join(bib['author'].split(' and ')),
            'journal': journal,
            'pub_year': pub_year,
            'issue': issue,
            'link': link
            # 'link': f"[Link]({p['pub_url']})" if 'pub_url' in p else f"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={bib['title'].replace(' ', '+')}&btnG=&oq={bib['title'].replace(' ', '+')}",
        }
    except KeyError:
        pp(p)
        raise

    if any(i['year'] == pub_year for i in pubs_by_year):
        pubs_by_year[-1]['items'].append(pub)
    else:
        pubs_by_year.append({
            'year': pub_year,
            'items': [pub]
        })

# Write the publications to a json file
with open(f'{outdir}/publications.json', 'w') as f:
    json.dump(pubs_by_year, f, indent=2)

