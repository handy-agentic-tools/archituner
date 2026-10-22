from archituner.report.spelling import item_line
from archituner.report.spelling import section_line


def measure_line(label, value, law):
    if law is None:
        return f"{label} {value}"
    limit = "none" if law["limit"] is None else law["limit"]
    text = f"{label} {value}/{limit}"
    if law["share"] is not None:
        text += f" ({law['share']})"
    return text


def files_lines(document, md):
    lines = [section_line(
        "files: worst first - cognitive, then cyclomatic, then path", md)]
    for record in sorted(document["files"],
                         key=lambda r: (-r["cognitive"], -r["cyclomatic"],
                                        r["path"])):
        limits = record.get("limits", {})
        parts = []
        if "size" in record:
            parts.append(measure_line("size", record["size"],
                                      limits.get("size")))
        for key in ("defs", "depth", "cyclomatic", "cognitive"):
            parts.append(measure_line(key, record[key], limits.get(key)))
        if "prose_count" in record:
            parts.append(measure_line("prose", record["prose_count"],
                                      limits.get("prose_count"))
                         + f" ({record['prose_percent']}%)")
        lines.append(item_line(f"{record['path']}  " + "  ".join(parts), md))
    return lines


def prose_lines(document, md):
    lines = [section_line("prose", md)]
    entries = [(record["path"], entry)
               for record in document["files"] if "prose" in record
               for entry in record["prose"]]
    if not entries:
        lines.append(item_line("no prose", md))
    for path, entry in entries:
        lines.append(item_line(f"{path}:{entry['line']}  {entry['text']}", md))
    return lines
