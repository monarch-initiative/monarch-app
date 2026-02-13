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
    # ID format: phenopacket.store:GENE.FILENAME (dot separator)
    # Pedigree notation in IDs uses dots (e.g., IV.12) but filenames use underscores (IV_12)
    # Input:  .../notebooks/GENE.FILENAME_WITH.DOTS
    # Output: .../notebooks/GENE/phenopackets/FILENAME_WITH_DOTS.json
    phenopacket_match = re.search(r"(.+phenopacket-store/blob/main/notebooks/)([^.]+)\.(.+)$", url)
    if phenopacket_match:
        prefix, gene, filename = phenopacket_match.groups()
        filename = filename.replace(".", "_")  # Convert pedigree dots to underscores
        url = f"{prefix}{gene}/phenopackets/{filename}.json"

    return url


def get_uri(id: str) -> str | None:
    """Returns the URI for the given CURIE, or None if the prefix is unknown."""
    expanded = converter.expand(id)
    if expanded is None:
        return None
    return expansion_patch(expanded)


def get_expanded_curie(id: str) -> ExpandedCurie:
    """Returns the URI for the given CURIE."""
    return ExpandedCurie(id=id, url=get_uri(id))
