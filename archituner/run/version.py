import importlib.metadata
import os
import tomllib


def declared_version():
    try:
        return importlib.metadata.version("archituner")
    except importlib.metadata.PackageNotFoundError:
        root = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))
        with open(os.path.join(root, "pyproject.toml"), "rb") as handle:
            return tomllib.load(handle)["project"]["version"]
