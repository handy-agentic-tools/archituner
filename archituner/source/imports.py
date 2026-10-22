import sys

from archituner.source.reading import imports_of
from archituner.source.reading import judging_pair
from archituner.source.reading import resolved_path


def module_of(path, root):
    if not path.startswith(root):
        return None
    trimmed = path[len(root):].removesuffix(".py")
    parts = [p for p in trimmed.split("/") if p]
    if parts[-1:] == ["__init__"]:
        parts = parts[:-1]
    return ".".join(parts)


def resolve(module, path_by_module, prefix_pkg=None):
    prefixes = (prefix_pkg,) if isinstance(prefix_pkg, str) else tuple(prefix_pkg or ())
    if not module:
        return None
    if module.split(".")[0] in sys.stdlib_module_names:
        return None
    for candidate in [module] + [f"{p}.{module}" for p in prefixes]:
        target = resolved_path(candidate, path_by_module, prefixes)
        if target is not None:
            return target
    return None


def resolved_import(path, record, files, path_by_module, retry_prefix,
                    edges, module, line):
    target = resolve(module, path_by_module, retry_prefix)
    if target is None or target == path:
        return
    record["imports"].append({"module": module, "path": target,
                              "layer": files[target]["layer"],
                              "line": line})
    files[target]["importers"].append(path)
    src, tgt = record["layer"], files[target]["layer"]
    if src and tgt and src != tgt:
        edges.setdefault(judging_pair(src, tgt), []).append(
            {"file": path, "module": module, "line": line})


def resolve_file_imports(tree, path, record, files, path_by_module,
                         retry_prefix, edges):
    own_module = record["module"] or ""
    for module, line in imports_of(tree, path, own_module):
        resolved_import(path, record, files, path_by_module, retry_prefix,
                        edges, module, line)


def claimed(record):
    return record["layer"] is not None or record["module"] is not None


def resolve_imports(tree, files, path_by_module, retry_prefix):
    edges = {}
    for path, record in files.items():
        if claimed(record):
            resolve_file_imports(tree, path, record, files, path_by_module,
                                 retry_prefix, edges)
    return edges
