import os
from typing import List

import zmq

from tinyrpc.server import RPCServer
from tinyrpc.dispatch import RPCDispatcher
from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc.transports.zmq import ZmqServerTransport

from monarch_py.implementations.oak.oak_implementation import OakImplementation
# from monarch_py.datamodels.model import TermSetPairwiseSimilarity
from monarch_py.api.config import settings

def run_server():
    # first load oak, before starting the server
    phenio_db_path = settings.phenio_db_path if os.path.exists(settings.phenio_db_path) else None
    oak = OakImplementation().init_semsim(phenio_path=phenio_db_path)

    # set up all the bits that a tinyrpc server is made of
    ctx = zmq.Context()
    dispatcher = RPCDispatcher()
    transport = ZmqServerTransport.create(
        ctx, f'tcp://{settings.oak_server_host}:{settings.oak_server_port}'
    )

    rpc_server = RPCServer(
        transport,
        JSONRPCProtocol(),
        dispatcher
    )

    # register a serializable proxy for the compare method
    @dispatcher.public
    def compare_as_dict(
        subjects: List[str], objects: List[str], predicates: List[str] = None, labels=False
    ) -> dict:
        return oak.compare(
            subjects=subjects, objects=objects,
            predicates=predicates, labels=labels
        ).dict()

    rpc_server.serve_forever()

if __name__ == '__main__':
    run_server()
