import pytest

from monarch_py.implementations.oak.oak_implementation import OakImplementation
from monarch_py.api.config import oak
from monarch_py.utils.utils import dict_diff, compare_dicts
# from profiler import profile

# @profile()
@pytest.mark.skip(reason="This is a long running test")
def test_semsim_compare():

    subject_ids = ["MP:0010771", "MP:0002169", "MP:0005391", "MP:0005389", "MP:0005367"]
    object_ids = ["HP:0004325", "HP:0000093", "MP:0006144"]

    # oi = OakImplementation()
    # tsps = oi.compare(subject_ids, object_ids)
    tsps = oak.compare(subject_ids, object_ids)
    # tsps = oi.compare_termsets(subject_ids, object_ids)

    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(tsps)


if __name__ == "__main__":
    test_semsim_compare()
