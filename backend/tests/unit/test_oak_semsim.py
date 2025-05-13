import pytest

from monarch_py.implementations.oak.oak_implementation import OakImplementation


@pytest.mark.skip(reason="This is a long running test")
def test_semsim_compare():
    subject_ids = ["MP:0010771"]
    object_ids = ["HP:0004325"]

    print("Getting oak implementation")
    oak = OakImplementation()
    print("Initializing semsim")
    oak.init_semsim()
    print("Running compare")
    tsps = oak.compare(subject_ids, object_ids)

    assert len(tsps.subject_best_matches) == 1
    assert len(tsps.object_best_matches) == 1


if __name__ == "__main__":
    test_semsim_compare()
