import pytest


@pytest.fixture
def association_table():
    return {"limit": 5, "offset": 0, "total": 0, "items": []}
