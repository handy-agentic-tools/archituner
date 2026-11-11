import os

from archituner.contract import read_contract
from archituner.run.checkouts import checkout_marks
from archituner.run.checkouts import package_roots
from archituner.run.checkouts import same_project
from archituner.source import cross_contract_uses


def sibling_contracts(tree):
    parent = os.path.dirname(os.path.abspath(tree))
    here = os.path.abspath(tree)
    own = checkout_marks(here)
    try:
        entries = sorted(os.listdir(parent))
    except OSError:
        return []
    found = []
    for name in entries:
        candidate = sibling_contract(os.path.join(parent, name), here, own)
        if candidate:
            found.append(candidate)
    return found


def sibling_contract(directory, here, own):
    if directory == here:
        return None
    if not os.path.isdir(directory):
        return None
    candidate = os.path.join(directory, "ARCHITECTURE.md")
    if not os.path.exists(candidate):
        return None
    if same_project(checkout_marks(directory), own):
        return None
    return candidate


def cross_contract_names(tree, own_layers):
    roots = package_roots(own_layers)
    if not roots:
        return None
    names = []
    contracts = set()
    for path in sibling_contracts(tree):
        found = sibling_uses(path, roots)
        if found:
            names += found["names"]
            contracts.update(found["contracts"])
    if not names:
        return None
    return {"names": names, "contracts": sorted(contracts)}


def sibling_uses(contract_path, roots):
    named = sibling_tree(contract_path)
    if not named:
        return None
    try:
        return cross_contract_uses([named], roots)
    except (OSError, UnicodeDecodeError):
        return None


def sibling_tree(contract_path):
    try:
        sibling = read_contract(contract_path)
    except (OSError, SystemExit, UnicodeDecodeError):
        return None
    return (sibling.tree, os.path.basename(os.path.dirname(contract_path)))
