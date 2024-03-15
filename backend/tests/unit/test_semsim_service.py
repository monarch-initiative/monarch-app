from monarch_py.service.semsim_service import SemsimianService

import pytest


@pytest.fixture
def semsim_service():
    return SemsimianService(semsim_server_host="localhost", semsim_server_port=8080, entity_implementation=None)


@pytest.mark.parametrize(
    "data, expected",
    [
        ({"some_dict": {"a": 1, "b": "NaN", "c": 3}}, {"some_dict": {"a": 1, "b": None, "c": 3}}),
        ({"some_dict": {"a": 1, "b": "two", "c": 3}}, {"some_dict": {"a": 1, "b": "two", "c": 3}}),
    ],
)
def test_convert_nans(semsim_service, data, expected):
    result = semsim_service._convert_nans(data)
    assert result == expected
