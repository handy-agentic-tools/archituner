from archituner.presentation.model.layout import UNIT

CHAIN_W = UNIT * 160
CHAIN_STEP = UNIT * 32
BUS_W = UNIT * 280
TREE_W = UNIT * 200
BOX_W = UNIT * 140
BOX_H = UNIT * 20
ROW_STEP = UNIT * 25
USER_W = UNIT * 110
ARROW_X = UNIT * 70
JOIN_X = UNIT * 110
BUS_X = UNIT * 130
LAYER_X = UNIT * 160
TREE_SPINE = UNIT * 10
ROW_X = UNIT * 26
LABEL_H = UNIT * 16
LABEL_DROP = UNIT * 10
ROW_MID = UNIT * 10
SELECT_DROP = UNIT * 6
USES_DROP = UNIT * 30
SPINE_BOTTOM = UNIT * 21
TAIL = UNIT * 22
NAME_INSET = UNIT * 8
NAME_BASE = UNIT * 14


def box(name, x, y, width, height):
    return {"name": name, "x": x, "y": y, "width": width, "height": height}


def join(x1, x2, y):
    return {"x1": x1, "x2": x2, "y": y}


def line(x, y1, y2):
    return {"x": x, "y1": y1, "y2": y2}


def chain_column(names, on):
    return {"width": CHAIN_W,
            "height": max(0, CHAIN_STEP * (len(names) - 1) + TAIL),
            "on": on,
            "boxes": [box(name, 0, CHAIN_STEP * i, BOX_W, BOX_H)
                      for i, name in enumerate(names)],
            "arrows": [line(ARROW_X, CHAIN_STEP * i + BOX_H + 1,
                            CHAIN_STEP * (i + 1))
                       for i in range(len(names) - 1)]}


def relied_on(users, layer):
    middle = (len(users) - 1) // 2
    return {"width": BUS_W,
            "height": max(0, ROW_STEP * (len(users) - 1) + TAIL),
            "users": [box(name, 0, ROW_STEP * i, USER_W, BOX_H)
                      for i, name in enumerate(users)],
            "joins": [join(JOIN_X, BUS_X, ROW_STEP * i + ROW_MID)
                      for i in range(len(users))],
            "bus": line(BUS_X, ROW_MID,
                        ROW_STEP * (len(users) - 1) + ROW_MID),
            "arrow": join(BUS_X, LAYER_X, ROW_STEP * middle + ROW_MID),
            "layer": box(layer, LAYER_X, ROW_STEP * middle, USER_W, BOX_H)}


def uses_tree(used_by, layer, uses):
    labels = {"used_by": {"x": ROW_X, "y": LABEL_DROP}}
    above = []
    joins = []
    y = LABEL_H
    for name in used_by:
        above.append(box(name, ROW_X, y, BOX_W, BOX_H))
        joins.append(join(TREE_SPINE, ROW_X, y + ROW_MID))
        y += ROW_STEP
    spare = {}
    if not used_by:
        spare["used_by"] = {"x": ROW_X, "y": y}
        y += ROW_STEP
    layer_y = y + SELECT_DROP
    into = line(TREE_SPINE, LABEL_H + ROW_MID, layer_y) if used_by else None
    y = layer_y + USES_DROP
    labels["uses"] = {"x": ROW_X, "y": y + LABEL_DROP}
    y += LABEL_H
    below = []
    heads = []
    last = layer_y + SPINE_BOTTOM
    for name in uses:
        heads.append(join(TREE_SPINE, ROW_X, y + ROW_MID))
        below.append(box(name, ROW_X, y, BOX_W, BOX_H))
        last = y + ROW_MID
        y += ROW_STEP
    if not uses:
        spare["uses"] = {"x": ROW_X, "y": y}
        y += ROW_STEP
    out = line(TREE_SPINE, layer_y + SPINE_BOTTOM, last) if uses else None
    return {"width": TREE_W, "height": y, "labels": labels,
            "used_by": above, "joins": joins, "into": into,
            "layer": box(layer, 0, layer_y, BOX_W + ROW_X, BOX_H),
            "uses": below, "heads": heads, "out": out, "spare": spare}
