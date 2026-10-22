import os

from archituner.contract import read_contract
from archituner.source import cross_contract_uses


def sibling_contracts(tree):
    parent = os.path.dirname(os.path.abspath(tree))
    here = os.path.abspath(tree)
    try:
        entries = sorted(os.listdir(parent))
    except OSError:
        return []
    found = []
    for name in entries:
        candidate = sibling_contract(os.path.join(parent, name), here)
        if candidate:
            found.append(candidate)
    return found


def sibling_contract(directory, here):
    if directory == here:
        return None
    if not os.path.isdir(directory):
        return None
    candidate = os.path.join(directory, "ARCHITECTURE.md")
    if os.path.exists(candidate):
        return candidate
    return None


def cross_contract_names(tree, own_layers):
    roots = {glob.split("/")[0].split("*")[0].strip("/")
             for globs in own_layers.values() for glob in globs}
    roots.discard("")
    if not roots:
        return None
    trees = []
    for path in sibling_contracts(tree):
        named = sibling_tree(path)
        if named:
            trees.append(named)
    return cross_contract_uses(trees, roots)


def sibling_tree(contract_path):
    try:
        sibling = read_contract(contract_path)
    except SystemExit:
        return None
    return (sibling.tree, os.path.basename(os.path.dirname(contract_path)))
