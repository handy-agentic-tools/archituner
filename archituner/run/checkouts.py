import os
import subprocess

from archituner.contract import read_contract

GIT_WAIT = 30
GIT_ENV = {name: value for name, value in os.environ.items()
           if not name.startswith("GIT_")}


def checkout_marks(tree):
    if not os.path.exists(os.path.join(tree, ".git")):
        return {"common_dir": None, "origin_url": None,
                "roots": contract_roots(tree)}
    return {"common_dir": git_common_dir(tree),
            "origin_url": origin_url(tree),
            "roots": contract_roots(tree)}


def same_project(beside, own):
    if own["common_dir"] is not None \
            and beside["common_dir"] == own["common_dir"]:
        return True
    if own["origin_url"] is not None \
            and beside["origin_url"] == own["origin_url"]:
        return True
    return bool(beside["roots"] & own["roots"])


def git_common_dir(tree):
    found = git_text(tree, "rev-parse", "--git-common-dir")
    if found is None:
        return None
    return os.path.realpath(os.path.join(tree, found))


def origin_url(tree):
    return git_text(tree, "config", "--get", "remote.origin.url")


def git_text(tree, *args):
    try:
        run = subprocess.run(["git", *args], cwd=tree, capture_output=True,
                             env=GIT_ENV, timeout=GIT_WAIT)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if run.returncode:
        return None
    return run.stdout.decode().strip() or None


def contract_roots(tree):
    try:
        contract = read_contract(os.path.join(tree, "ARCHITECTURE.md"))
    except (OSError, SystemExit):
        return set()
    return package_roots(contract.layers)


def package_roots(layers):
    roots = {glob.split("/")[0].split("*")[0].strip("/")
             for globs in layers.values() for glob in globs}
    roots.discard("")
    return roots
