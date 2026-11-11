def worst_ratio(row, side, scale):
    areas = [item["files"] * scale for item in row]
    total = sum(areas)
    if min([side, total, *areas]) <= 0:
        return float("inf")
    return max((side * side * max(areas)) / (total * total),
               (total * total) / (side * side * min(areas)))


def grown_row(items, row, side, scale):
    while items and worst_ratio(row + [items[0]], side, scale) <= worst_ratio(row, side, scale):
        row.append(items.pop(0))
    return row


def row_laid(row, scale, x, y, width, height):
    area = sum(item["files"] for item in row) * scale
    across = width <= height
    band = area / min(width, height)
    offset = x if across else y
    boxes = []
    for item in row:
        span = (item["files"] * scale) / band if band else 0
        boxes.append({**item, "x": offset, "y": y, "width": span, "height": band}
                     if across else
                     {**item, "x": x, "y": offset, "width": band, "height": span})
        offset += span
    if across:
        return boxes, x, y + band, width, height - band
    return boxes, x + band, y, width - band, height


def squarify(items, x, y, width, height):
    items = list(map(dict, items))
    placed = []
    total = sum(item["files"] for item in items)
    if min(total, width, height) <= 0:
        return placed
    scale = (width * height) / total
    row = []
    while items:
        row = grown_row(items, row, min(width, height), scale)
        boxes, x, y, width, height = row_laid(row, scale, x, y, width, height)
        placed += boxes
        row = []
    return placed
