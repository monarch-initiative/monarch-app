from monarch_py.datamodels.model import HistoBin, HistoPheno
from monarch_py.datamodels.solr import HistoPhenoKeys, SolrQueryResult


def parse_histopheno(query_result: SolrQueryResult, subject_closure: str):
    bins = []
    for k, v in query_result.facet_counts.facet_queries.items():
        id = f"{k.split(':')[1]}:{k.split(':')[2]}".replace('"', "")
        label = HistoPhenoKeys(id).name
        bins.append(HistoBin(id=id, label=label, count=v))
    bins = sorted(bins, key=lambda x: x.count, reverse=True)

    return HistoPheno(id=subject_closure, items=bins)

