import ast
import os


def relative_base(own_module, is_init, level):
    parts = own_module.split(".")
    strip = level - 1 if is_init else level
    return ".".join(parts[:len(parts) - strip]) if strip < len(parts) else ""


def from_stem(node, own_module, is_init):
    if not node.level:
        return node.module or ""
    base = relative_base(own_module, is_init, node.level)
    return ".".join(filter(None, [base, node.module or ""]))


def import_entries(node, own_module, is_init):
    if isinstance(node, ast.Import):
        return [(alias.name, node.lineno) for alias in node.names]
    if not isinstance(node, ast.ImportFrom):
        return []
    stem = from_stem(node, own_module, is_init)
    return [(stem, node.lineno)] + [(f"{stem}.{alias.name}", node.lineno)
                                    for alias in node.names]


def imports_of(tree, path, own_module):
    try:
        parsed = ast.parse(open(os.path.join(tree, path), encoding="utf-8").read())
    except (SyntaxError, UnicodeDecodeError):
        return []
    is_init = path.endswith("__init__.py")
    found = []
    for node in ast.walk(parsed):
        found += import_entries(node, own_module, is_init)
    return found


def parent_name(name):
    head, dot, _ = name.rpartition(".")
    return head if dot else None


def judging_pair(src, tgt):
    a, b = src, tgt
    while a.count(".") > b.count("."):
        a = a.rpartition(".")[0]
    while b.count(".") > a.count("."):
        b = b.rpartition(".")[0]
    while parent_name(a) != parent_name(b):
        a, b = a.rpartition(".")[0], b.rpartition(".")[0]
    return a, b


def resolved_path(candidate, path_by_module, prefixes):
    probe = candidate
    while probe:
        if probe in path_by_module:
            return path_by_module[probe]
        probe = probe.rpartition(".")[0]
        if probe in prefixes:
            return None
    return None
