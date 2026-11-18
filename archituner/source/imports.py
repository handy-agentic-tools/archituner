from archituner.source.reading import imports_of
from archituner.source.reading import index_name
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


def candidates(module, relative, declared, prefixes):
    base = index_name(module, relative, declared)
    if not base:
        return []
    return [base] + [f"{p}.{base}" for p in prefixes]


def resolve(module, path_by_module, prefix_pkg=None, may_be_name=False,
            relative=False, declared=None):
    if not module:
        return None
    prefixes = (prefix_pkg,) if isinstance(prefix_pkg, str) else tuple(prefix_pkg or ())
    for candidate in candidates(module, relative, declared, prefixes):
        target = resolved_path(candidate, path_by_module, prefixes,
                               may_be_name)
        if target is not None:
            return target
    return None


def resolved_import(path, record, files, path_by_module, retry_prefix,
                    edges, module, line, may_be_name, relative=False,
                    declared=None):
    target = resolve(module, path_by_module, retry_prefix, may_be_name,
                     relative=relative, declared=declared)
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
                         retry_prefix, edges, declared=None):
    own_module = record["module"] or ""
    for module, line, may_be_name, relative in imports_of(tree, path,
                                                          own_module):
        resolved_import(path, record, files, path_by_module, retry_prefix,
                        edges, module, line, may_be_name, relative,
                        declared=declared)


def claimed(record):
    return record["layer"] is not None or record["module"] is not None


def resolve_imports(tree, files, path_by_module, retry_prefix,
                    declared=None):
    edges = {}
    for path, record in files.items():
        if claimed(record):
            resolve_file_imports(tree, path, record, files, path_by_module,
                                 retry_prefix, edges, declared=declared)
    return edges
