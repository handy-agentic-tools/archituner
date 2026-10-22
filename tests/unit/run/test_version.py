import importlib.metadata
import os
import sys
import tomllib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.run.version import declared_version

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))


def pyproject_version():
    with open(os.path.join(ROOT, "pyproject.toml"), "rb") as handle:
        return tomllib.load(handle)["project"]["version"]


def test_the_declared_version_is_what_the_installed_distribution_answers():
    wanted = importlib.metadata.version("archituner")
    assert isinstance(declared_version(), str)
    assert declared_version() == wanted


def test_an_uninstalled_tree_still_answers_pyprojects_version():
    kept = importlib.metadata.version
    try:
        def missing(name):
            raise importlib.metadata.PackageNotFoundError(name)
        importlib.metadata.version = missing
        assert declared_version() == pyproject_version()
    finally:
        importlib.metadata.version = kept


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
