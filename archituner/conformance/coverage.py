def coverage_tree(files):
    root = {"name": ".", "path": "", "children": {}, "own": {}}
    for record in files:
        parts = record["path"].split("/")
        node = root
        for depth, part in enumerate(parts[:-1]):
            node = node["children"].setdefault(part, {
                "name": part, "path": "/".join(parts[:depth + 1]),
                "children": {}, "own": {}})
        node["own"].setdefault(record["layer"], []).append(record["path"])

    def shape(node):
        children = [shape(child) for child in node["children"].values()]
        leaves = [{"kind": "files", "name": layer or "unclaimed", "path": node["path"],
                   "layer": layer, "files": len(members), "members": sorted(members),
                   "children": []}
                  for layer, members in sorted(node["own"].items(),
                                               key=lambda kv: (kv[0] or "",))]
        items = children + leaves
        return {"kind": "dir", "name": node["name"], "path": node["path"],
                "layer": None, "members": [],
                "files": sum(item["files"] for item in items),
                "children": [item for item in items if item["files"] > 0]}

    return shape(root)
