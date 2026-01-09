import re
from monarch_py.datamodels.model import ExpandedCurie
from monarch_py.service.curie_service import converter

__all__ = [
    "get_expanded_curie",
]


def expansion_patch(url: str):
    """Any short term patches that we need while waiting for upstream fixes"""

    # This fixes MGI urls that take the form of
    # https://identifiers.org/MGI/97486
    # rather than https://identifiers.org/MGI:97486
    pattern = r"/MGI/(\d+)$"
    replacement = r"/MGI:\1"
    url = re.sub(pattern, replacement, url)

    # Fix phenopacket.store URLs to include /phenopackets/ subdirectory and .json extension
    # Input:  .../notebooks/GENE/FILENAME
    # Output: .../notebooks/GENE/phenopackets/FILENAME.json
    phenopacket_pattern = r"(phenopacket-store/blob/main/notebooks/[^/]+)/(.+)$"
    phenopacket_replacement = r"\1/phenopackets/\2.json"
    url = re.sub(phenopacket_pattern, phenopacket_replacement, url)

    return url


def get_uri(id: str) -> str | None:
    """Returns the URI for the given CURIE, or None if the prefix is unknown."""
    expanded = converter.expand(id)
    if expanded is None:
        return None
    return expansion_patch(expanded)


def get_expanded_curie(id: str) -> ExpandedCurie:
    """Returns the URI for the given CURIE."""
    return ExpandedCurie(id=id, url=converter.expand(id))
