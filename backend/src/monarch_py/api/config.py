import os
import requests as rq
from functools import lru_cache
from typing import List

from pydantic import BaseSettings

from monarch_py.implementations.solr.solr_implementation import SolrImplementation
from monarch_py.datamodels.model import TermSetPairwiseSimilarity, SemsimSearchResult


class Settings(BaseSettings):
    solr_host = os.getenv("SOLR_HOST") if os.getenv("SOLR_HOST") else "127.0.0.1"
    solr_port = os.getenv("SOLR_PORT") if os.getenv("SOLR_PORT") else 8983
    solr_url = os.getenv("SOLR_URL") if os.getenv("SOLR_URL") else f"http://{solr_host}:{solr_port}/solr"
    phenio_db_path = os.getenv("PHENIO_DB_PATH") if os.getenv("PHENIO_DB_PATH") else "/data/phenio.db"

    semsim_server_host = os.getenv("SEMSIM_SERVER_HOST", "127.0.0.1")
    semsim_server_port = os.getenv("SEMSIM_SERVER_PORT", 9999)


settings = Settings()


@lru_cache(maxsize=1)
def solr():
    return SolrImplementation(settings.solr_url)


def convert_nans(input_dict, to_value=None):
    """
    Given an input dict of the form {<term>: {<field>: <value>, ...}}
    converts any <value> of 'NaN' to None.
    """
    for k, v in input_dict.items():
        for ik, iv in v.items():
            if iv == "NaN":
                input_dict[k][ik] = None

    return input_dict


class SemsimianHTTPRequester:
    """A class that makes HTTP requests to the semsimian_server."""

    def convert_tsps_data(self, data):
        """Convert to a format that can be coerced into a TermSetPairwiseSimilarity model

        FIXME: currently, the response returned from semsimian_server doesn't
        100% match the TermSetPairwiseSimilarity model, so we perform some
        transformations below. once it does, we can remove all the code below
        and just return TermSetPairwiseSimilarity(**data)
        """
        # remove these similarity maps and fold them into the _best_matches dicts
        object_best_matches_similarity_map = convert_nans(data.pop("object_best_matches_similarity_map"))
        subject_best_matches_similarity_map = convert_nans(data.pop("subject_best_matches_similarity_map"))
        converted_data = {
            **data,
            **{
                # flatten the nested termset dicts
                "subject_termset": {k: v for d in data["subject_termset"] for k, v in d.items()},
                "object_termset": {k: v for d in data["object_termset"] for k, v in d.items()},
                "subject_best_matches": {
                    k: {**v, "similarity": subject_best_matches_similarity_map[k]}
                    for k, v in data["subject_best_matches"].items()
                },
                "object_best_matches": {
                    k: {**v, "similarity": object_best_matches_similarity_map[k]}
                    for k, v in data["object_best_matches"].items()
                },
            },
        }
        return converted_data

    def compare(self, subjects: List[str], objects: List[str]):
        host = f"http://{settings.semsim_server_host}:{settings.semsim_server_port}"
        path = f"compare/{','.join(subjects)}/{','.join(objects)}"
        url = f"{host}/{path}"

        print(f"Fetching {url}...")
        response = rq.get(url=url)
        data = response.json()
        results = self.convert_tsps_data(data)
        return TermSetPairwiseSimilarity(**results)

    def search(self, termset: List[str], prefix: str, limit: int):
        host = f"http://{settings.semsim_server_host}:{settings.semsim_server_port}"
        path = f"search/{','.join(termset)}/{prefix}?limit={limit}"
        url = f"{host}/{path}"

        print(f"Fetching {url}...")
        response = rq.get(url=url)
        data = response.json()
        results = [
            SemsimSearchResult(
                subject=solr().get_entity(i[2], extra=False), score=i[0], similarity=self.convert_tsps_data(i[1])
            )
            for i in data
        ]

        return results


@lru_cache(maxsize=1)
def semsimian():
    return SemsimianHTTPRequester()


@lru_cache(maxsize=1)
def oak():
    return NotImplementedError("OAK is temporarily disabled")


#    oak_implementation = OakImplementation()
#    oak_implementation.init_phenio_adapter(force_update=False, phenio_path=settings.phenio_db_path)
#    return oak_implementation
