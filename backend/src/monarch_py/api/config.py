import os
import zmq
from functools import lru_cache

from pydantic import BaseSettings

from tinyrpc import RPCClient
from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc.transports.zmq import ZmqClientTransport

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

class OakRPCMarshaller:
    def __init__(self) -> None:
        ctx = zmq.Context()
        rpc_client = RPCClient(
            JSONRPCProtocol(),
            ZmqClientTransport.create(
                ctx, f'tcp://{settings.oak_server_host}:{settings.oak_server_port}'
            )
        )
        self.oak_server = rpc_client.get_proxy()

    def compare(self, *args, **kwargs):
        # for some reason TermSetPairwiseSimilarity is not JSON-serializable so
        # we can't call compare() directly. instead, we call compare_as_dict(),
        # which sends back a dict, and then we convert it into the expected
        # TermSetPairwiseSimilarity type
        result = self.oak_server.compare_as_dict(*args, **kwargs)
        return TermSetPairwiseSimilarity(**result)


@lru_cache(maxsize=1)
def oak():
    return OakRPCMarshaller()
