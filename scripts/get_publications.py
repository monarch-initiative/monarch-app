from pathlib import Path

import pprint
from scholarly import scholarly

pp = pprint.PrettyPrinter(indent=2).pprint

outfile = Path(__file__).parent / 'scholarly_output.py'
print(f"{'-'*80}\nWriting publications to {outfile}")

def get_pubs_scholarly():
    def _check_missing_fields(pub):
        """Check for missing fields in the publication"""
        bib = pub['bib']
        missing = [j for j in ['title', 'author', 'pub_year'] if j not in bib]      
        missing.append('journal/publisher' if 'journal' not in bib and 'publisher' not in bib else '')
        missing.append('pub_url' if 'pub_url' not in pub else '')
        missing = [j for j in missing if j != '']
        return missing

    author = scholarly.search_author_id(id = 'zmUEDj0AAAAJ')
    scholarly.fill(author, sections=['publications'], sortby='year')
    publications = author['publications']
    pubs = []
    for p in publications:
        scholarly.fill(p, sections=['bib'])
        bib = p['bib']
        
        # Debug info
        print(f"Processing publication: {bib['title']}")
        missing = _check_missing_fields(p)
        if missing:
            print(f"\tMissing keys: {', '.join(missing)}")

        link = f"[Link]({p['pub_url']})" if 'pub_url' in p else 'No link found'        
        pub_year = bib['pub_year'] if 'pub_year' in bib else 'Unknown'
        journal = bib['journal'] if 'journal' in bib else bib['publisher'] if 'publisher' in bib else bib['citation'] if 'citation' in bib else 'No journal found'
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
            }
        except KeyError:
            pp(p)
            raise
        pubs.append(pub)
    return pubs


if __name__ == '__main__':
    pubs = get_pubs_scholarly()
    with open(outfile, 'w') as f:
        f.write(f"pubs = {pprint.pformat(pubs)}")