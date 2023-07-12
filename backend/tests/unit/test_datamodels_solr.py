import urllib
from typing import List

import pytest
from monarch_py.datamodels.solr import SolrQuery


@pytest.mark.parametrize(
    "query,query_string_parts",
    [
        (SolrQuery(), ["q=*:*"]),
        (SolrQuery(rows=10), ["q=*:*", "rows=10"]),
        (SolrQuery(start=101), ["q=*:*", "start=101"]),
        (SolrQuery(q="marfan"), ["q=marfan"]),
        (SolrQuery(facet_fields=["category"]), ["facet.field=category", "facet=true"]),
        (
            SolrQuery(facet_fields=["category", "taxon"]),
            ["q=*:*", "facet.field=category", "facet.field=taxon", "facet=true"],
        ),
        (
            SolrQuery(
                facet_queries=[
                    'object_closure:"HP:0000924"',
                    'object_closure:"HP:0000119"]',
                ]
            ),
            [
                "q=*:*",
                'facet.query=object_closure:"HP:0000924"',
                'facet.query=object_closure:"HP:0000119"]',
                "facet=true",
            ],
        ),
        (
            SolrQuery(filter_queries=['subject_category:"biolink:Gene"']),
            ['fq=subject_category:"biolink:Gene"'],
        ),
        (
            SolrQuery(q="marfan", query_fields="id^100 name^10 synonym"),
            ["qf=", "defType=edismax"],
        ),  # don't worry about actual value of qf
        (
            SolrQuery(
                q="marfan",
                boost='boost=if(termfreq(category,"biolink:Disease"),10.0,1)',
            ),
            ['boost=if(termfreq(category,"biolink:Disease"),10.0,1)'],
        ),
        (SolrQuery(sort="label asc"), ["sort=label+asc"]),
    ],
)
def test_query(query: SolrQuery, query_string_parts: List[str]):
    query_string = urllib.parse.unquote(query.query_string())
    for part in query_string_parts:
        assert part in query_string
