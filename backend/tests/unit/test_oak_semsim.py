# from monarch_py.api.config import oak
from monarch_py.implementations.oak.oak_implementation import OakImplementation
# from monarch_py.utils.utils import dict_diff, compare_dicts


import cProfile
import pstats
from functools import wraps

def profile(
        output_file: str = None,
        sort_by: str ='cumulative',
        lines_to_print: int = None,
        strip_dirs: bool = False
    ):
    def inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _output_file = output_file or func.__name__ + '.prof'
            pr = cProfile.Profile()
            pr.enable()
            retval = func(*args, **kwargs)
            pr.disable()
            pr.dump_stats(_output_file)

            with open(_output_file, 'w') as f:
                ps = pstats.Stats(pr, stream=f)
                if strip_dirs:
                    ps.strip_dirs()
                if isinstance(sort_by, (tuple, list)):
                    ps.sort_stats(*sort_by)
                else:
                    ps.sort_stats(sort_by)
                ps.print_stats(lines_to_print)
            return retval
        return wrapper
    return inner



# @pytest.mark.skip(reason="This is a long running test")
@profile()
def test_semsim_compare():

    subject_ids = ["MP:0010771" ]
    object_ids = ["HP:0004325"]

    print("Getting oak implementation")
    oak = OakImplementation()
    print("Initializing semsim")
    oak.init_semsim()
    print("Running compare")
    tsps = oak.compare(subject_ids, object_ids)
    # tsps = oak.compare_termsets(subject_ids, object_ids)

    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(tsps)


if __name__ == "__main__":
    test_semsim_compare()
