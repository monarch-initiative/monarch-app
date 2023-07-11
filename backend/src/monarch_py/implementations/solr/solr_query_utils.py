from typing import List

from monarch_py.datamodels.solr import SolrQuery, HistoPhenoKeys
from monarch_py.utils.utils import escape

def build_association_query(
    category: List[str] = None,
    predicate: List[str] = None,
    subject: List[str] = None,
    object: List[str] = None,
    subject_closure: str = None,
    object_closure: str = None,
    entity: List[str] = None,
    direct: bool = None,
    q: str = None,
    offset: int = 0,
    limit: int = 20,
) -> SolrQuery:
    """Populate a SolrQuery object with association filters"""

    query = SolrQuery(start=offset, rows=limit)

    if category:
        query.add_field_filter_query("category", " OR ".join(category))
    if predicate:
        query.add_field_filter_query("predicate", " OR ".join(predicate))
    if subject:
        if direct:
            query.add_field_filter_query("subject", " OR ".join(subject))
        else:
            query.add_filter_query(" OR ".join([f'subject:"{s}" OR subject_closure:"{s}"' for s in subject]))
    if subject_closure:
        query.add_field_filter_query("subject_closure", subject_closure)
    if object:
        if direct:
            query.add_field_filter_query("object", " OR ".join(object))
        else:
            query.add_filter_query(" OR ".join([f'object:"{o}" OR object_closure:"{o}"' for o in object]))
    if object_closure:
        query.add_field_filter_query("object_closure", object_closure)
    if entity:
        if direct:
            query.add_filter_query(" OR ".join([f'subject:"{escape(e)}" OR object:"{escape(e)}"' for e in entity]))
        else:
            query.add_filter_query(
                " OR ".join(
                    [
                        f'subject:"{escape(e)}" OR subject_closure:"{escape(e)}" OR object:"{escape(e)}" OR object_closure:"{escape(e)}"'
                        for e in entity
                    ]
                )
            )
    if q:
        # We don't yet have tokenization strategies for the association index, initially we'll limit searching to
        # the visible fields in an association table plus their ID equivalents and use a wildcard query for substring matching
        query.q = f"*{q}*"
        query.query_fields = "subject subject_label predicate object object_label"

    return query


def build_histopheno_query(subject_closure: str) -> SolrQuery:
    """Get SolrQueryResult for a histopheno query"""
    query = build_association_query(
        subject_closure=subject_closure,
        offset = 0,
        limit = 0,
    )
    hpkeys = [i.value for i in HistoPhenoKeys]
    query.facet_queries = [f'object_closure:"{i}"' for i in hpkeys]
    return query