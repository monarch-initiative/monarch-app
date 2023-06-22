########################################################################
# This file is used to import pytest fixtures from the tests directory #
########################################################################

import pytest

from .fixtures import autocomplete, histopheno, node, node_associations, search


def test_autocomplete(autocomplete):
    assert autocomplete