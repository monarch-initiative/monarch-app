import os
import requests as rq

from functools import lru_cache

from pydantic import BaseSettings

from monarch_py.implementations.oak.oak_implementation import OakImplementation
from monarch_py.implementations.solr.solr_implementation import SolrImplementation
from monarch_py.datamodels.model import TermSetPairwiseSimilarity



class Settings(BaseSettings):
    solr_host = os.getenv("SOLR_HOST") if os.getenv("SOLR_HOST") else "127.0.0.1"
    solr_port = os.getenv("SOLR_PORT") if os.getenv("SOLR_PORT") else 8983
    solr_url = os.getenv("SOLR_URL") if os.getenv("SOLR_URL") else f"http://{solr_host}:{solr_port}/solr"
    phenio_db_path = os.getenv("PHENIO_DB_PATH") if os.getenv("PHENIO_DB_PATH") else "/data/phenio.db"

    oak_server_host = os.getenv("OAK_SERVER_HOST", '127.0.0.1')
    oak_server_port = os.getenv("OAK_SERVER_PORT", 18811)

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
            if iv == 'NaN':
                input_dict[k][ik] = None

    return input_dict


class OakHTTPRequester:
    def compare(self, subjects, objects):
        host = f"http://{settings.oak_server_host}:{settings.oak_server_port}"
        path = f"/compare/{','.join(subjects)}/{','.join(objects)}"
        url = f"{host}/{path}"

        print(f"Fetching {url}...")
        response = rq.get(url=url)
        data = response.json()

        # FIXME: currently, the response returned from semsimian_server doesn't
        #  100% match the TermSetPairwiseSimilarity model, so we perform some
        #  transformations below. once it does, we can remove all the code below
        #  and just return TermSetPairwiseSimilarity(**data)

        # remove these similarity maps and fold them into the _best_matches dicts
        object_best_matches_similarity_map = convert_nans(
            data.pop('object_best_matches_similarity_map')
        )
        subject_best_matches_similarity_map = convert_nans(
            data.pop('subject_best_matches_similarity_map')
        )

        # convert to a format that can be coerced into a TermSetPairwiseSimilarity
        converted_data = {
            **data,
            **{
                'subject_termset': data['subject_termset'][0],
                'object_termset': data['object_termset'][0],
                'subject_best_matches': {
                    k: {**v, 'similarity': subject_best_matches_similarity_map[k]}
                    for k, v in data['subject_best_matches'].items()
                },
                'object_best_matches': {
                    k: {**v, 'similarity': object_best_matches_similarity_map[k]}
                    for k, v in data['object_best_matches'].items()
                }
            }
        }

        return TermSetPairwiseSimilarity(**converted_data)


@lru_cache(maxsize=1)
def oak():
    return OakHTTPRequester()
