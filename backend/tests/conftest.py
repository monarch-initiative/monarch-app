import os
from glob import glob

import pytest
# from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch

from monarch_py.implementations.solr.solr_implementation import SolrImplementation
from monarch_py.datamodels.model import AssociationResults, HistoPheno, Node, SearchResults


def _as_module(fixture_path: str) -> str:
    """Convert a file path to a module path."""
    return fixture_path.replace("/", ".").replace("\\", ".").replace(".py", "")


if os.getcwd().endswith("monarch-app"):
    fixtures_dir = "backend/tests/fixtures"
elif os.getcwd().endswith("backend"):
    fixtures_dir = "tests/fixtures"
else:
    raise Exception("Could not find fixtures directory")

fixtures = glob(f"{fixtures_dir}/[!_]*.py")
pytest_plugins = [_as_module(f) for f in fixtures]


### Mock SolrImplementation

@pytest.fixture
def mock_solr(node, associations, autocomplete, search, histopheno):
    """Mock SolrImplementation class."""
    with patch("monarch_py.implementations.solr.solr_implementation.SolrImplementation") as mock:
        mock.get_entity.return_value = Node(**node)
        mock.get_associations.return_value = AssociationResults(**associations)
        mock.autocomplete.return_value = SearchResults(**autocomplete)
        mock.search.return_value = SearchResults(**search)
        yield mock
