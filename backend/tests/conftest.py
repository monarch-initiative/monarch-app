from glob import glob
import os


# if os.getcwd().endswith("monarch-app"):
#     fixtures_dir = "backend/tests/fixtures"
# elif os.getcwd().endswith("backend"):
#     fixtures_dir = "tests/fixtures"
# else:
#     raise Exception("Could not find fixtures directory")

fixtures_dir = "backend/tests/fixtures"
fixtures = glob(f"{fixtures_dir}/*.py")


def refactor(string: str) -> str:
    return string.replace("/", ".").replace("\\", ".").replace(".py", "")

print([refactor(fixture) for fixture in fixtures if "__" not in fixture])

pytest_plugins = [
    refactor(fixture) for fixture in glob(f"{fixtures_dir}/*.py") if "__" not in fixture
]