import pytest
from fastapi.testclient import TestClient
from monarch_py.api.semsim import router

client = TestClient(router)


@pytest.mark.skip(reason="Not implemented")
def test_semsim(semsim):
    ...
