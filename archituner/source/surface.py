from archituner.source.names import declared_all
from archituner.source.names import names_of
from archituner.source.names import parsed_of
from archituner.source.reading import imports_of
from archituner.source.walk import source_files


def entry_of(order, pairs):
    allowed = {t for (s, t), k in pairs.items() if k == "allow"}
    for name in order:
        if name not in allowed:
            return name
    return order[0]


def named_entries(names_, path):
    return [{"name": name, "file": path} for name in names_]


def collected_names(parsed, declared, layer_declares):
    names = []
    for path, tree_ in parsed.items():
        own = declared[path]
        if own is not None:
            names += named_entries(own, path)
        elif not layer_declares:
            names += named_entries(names_of(tree_), path)
    return names


def merged_names(names):
    merged = {}
    for entry_name in sorted(names, key=lambda n: n["name"]):
        seen = merged.setdefault(entry_name["name"],
                                 {"name": entry_name["name"],
                                  "file": entry_name["file"]})
        if entry_name["file"] not in seen["file"].split(", "):
            seen["file"] += ", " + entry_name["file"]
    return list(merged.values())


def read_surface(tree, files, order, pairs):
    entry = entry_of(order, pairs)
    parsed = parsed_of(tree, files, entry)
    declared = {path: declared_all(tree_) for path, tree_ in parsed.items()}
    layer_declares = any(names is not None for names in declared.values())
    names = collected_names(parsed, declared, layer_declares)
    return {"entry": entry, "names": merged_names(names)}


def file_uses(tree, label, path, roots):
    return [{"contract": label, "file": path, "module": module}
            for module, _line in imports_of(tree, path, "")
            if module.split(".")[0] in roots]


def cross_contract_uses(trees, roots):
    uses = []
    for tree, label in trees:
        for path in sorted(source_files(tree)):
            uses += file_uses(tree, label, path, roots)
    if not uses:
        return None
    return {"names": uses,
            "contracts": sorted({u["contract"] for u in uses})}
