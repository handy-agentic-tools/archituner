import os


def measure_prose(tree, files):
    from archituner.conformance.no_prose import findings

    prose_total = 0
    non_blank_total = 0
    for record in files.values():
        if not record["layer"]:
            continue
        entries, non_blank = prose_record(tree, record, findings)
        prose_total += len(entries)
        non_blank_total += non_blank
    return round(100 * prose_total / non_blank_total, 1) if prose_total else 0.0


def prose_record(tree, record, findings):
    path = os.path.join(tree, record["path"])
    with open(path, "rb") as handle:
        data = handle.read()
    try:
        rows = findings(data)
    except Exception:
        rows = []
    try:
        with open(path, encoding="utf-8") as handle:
            body = handle.readlines()
    except Exception:
        rows, body = [], []
    entries = [{"line": row, "text": body[row - 1].strip()}
               for row in sorted({row for row, _ in rows})]
    non_blank = sum(1 for line in body if line.strip())
    record["prose"] = entries
    record["prose_count"] = len(entries)
    record["prose_percent"] = round(100 * len(entries) / non_blank, 1) \
        if entries else 0.0
    return entries, non_blank
