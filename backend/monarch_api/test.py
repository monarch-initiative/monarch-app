import pprint
import requests
import urllib.parse as parse

pp = pprint.PrettyPrinter(indent=4)
solr_url = "http://localhost:8983/solr"


def build_association_query(args: dict) -> str:
    query = "?"
    query_params = ['q', 'offset', 'limit']
    filter_params = ['subject', 'object', 'predicate', 'entity', 'category', 'between']
    for i in query_params:
        if args[i] == None:
            pass
        elif i in query_params:
            query += f'{i}={args[i]}&'
    query += "fq="
    for i in filter_params:
        if args[i] == None:
            pass
        elif i == 'entity':
            query += f'subject:"{i}" OR object:"{i}"&'
        elif i == 'between':
            between = args[i].split(",")
            query += f'(subject:"{between[0]}" AND object:"{between[1]}") OR (subject:"{between[1]}" AND object:"{between[0]}")&'
        else:
            query += f'{i}:"{args[i]}"&'
    return query

def get_associations(
    q: str = "*:*",
    offset: int = 0,
    limit: int = 20,
    category: str = None,
    predicate: str = None,
    subject: str = None,
    object: str = None,
    entity: str = None, # return nodes where entity is subject or object
    between: str = None # strip by comma and check associations in both directions. example: "MONDO:000747,MONDO:000420"
    ):

    query = build_association_query(locals())
    
    association_url = f"{solr_url}/association/query"
    url = association_url+query
    r = requests.get(url)
    results = r.json()['response']['docs']
    return results
    
    print("Query: ",query)
    print("URL: ", url)   
    #print(docs)
    for i in docs:
        print(i['subject'], )
    
    
get_associations()
get_associations(subject="ZFIN:ZDB-GENE-050913-20")
get_associations(between="ZFIN:ZDB-GENE-050913-20,GO:0005576")