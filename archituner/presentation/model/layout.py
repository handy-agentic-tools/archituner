from archituner.presentation.model.squarify import squarify

UNIT = 1
HEADER = UNIT * 15
INSET = UNIT * 3
MIN_SPLIT = UNIT * 46
NAME_MIN = UNIT * 40
DIRNAME_Y = UNIT * 11
NAME_Y = UNIT * 13
META_Y = UNIT * 25
LABEL_INSET = UNIT * 4
MARK_X = UNIT * 3
MARK_Y = UNIT * 12
CANVAS_W = UNIT * 1000
CANVAS_H = UNIT * 620
NARROW_W = UNIT * 560


def held(node):
    return sorted(node["members"]
                  + [path for child in node["children"] for path in held(child)])


def place(node, x, y, width, height, parent, depth):
    opened = (node["kind"] == "dir" and node["children"]
              and width > MIN_SPLIT and height > MIN_SPLIT + HEADER)
    box = {"id": f"{node['path']}|{node['layer'] or ''}|{depth}",
           "path": node["path"], "name": node["name"], "layer": node["layer"],
           "files": node["files"], "members": [] if opened else held(node),
           "x": x, "y": y, "width": width, "height": height,
           "parent": parent, "depth": depth, "opened": bool(opened)}
    if not opened:
        return [box]
    inner = (x + INSET, y + HEADER, width - 2 * INSET, height - HEADER - INSET)
    boxes = [box]
    for child in squarify(node["children"], *inner):
        boxes += place(child, child["x"], child["y"], child["width"], child["height"],
                       box["id"], depth + 1)
    return boxes


def treemap(coverage, x, y, width, height):
    root = coverage["tree"]
    boxes = []
    for child in squarify(root["children"], x, y, width, height):
        boxes += place(child, child["x"], child["y"], child["width"], child["height"],
                       None, 0)
    return boxes


def regions(coverage):
    return treemap(coverage, 0, 0, CANVAS_W, CANVAS_H)


def canvas():
    return CANVAS_W, CANVAS_H


def labels():
    return NAME_MIN, MIN_SPLIT, DIRNAME_Y, NAME_Y, META_Y


def stack_geometry():
    return {"row": UNIT * 34, "pad": UNIT * 28, "margin": UNIT * 20,
            "node_w": UNIT * 604, "node_h": UNIT * 22, "band_l": UNIT * 352,
            "gap_l": UNIT * 8, "band_r": UNIT * 220, "cell": UNIT * 56,
            "hop": UNIT * 5,
            "narrow": {"row": UNIT * 38, "pad": UNIT * 26,
                       "margin": UNIT * 8, "node_w": UNIT * 200,
                       "node_h": UNIT * 30, "band_l": UNIT * 144,
                       "gap_l": UNIT * 6, "band_r": UNIT * 8,
                       "cell": UNIT * 50, "hop": UNIT * 3.5}}
