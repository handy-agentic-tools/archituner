from archituner.report.spelling import coloured_glyph
from archituner.report.spelling import item_line
from archituner.report.spelling import section_line
from archituner.vocabulary import STATES


def stated(axis, values):
    if isinstance(values, list):
        return f"{axis}={','.join(str(v) for v in values)}"
    return f"{axis}={values}"


def summary_lines(document, md, colour):
    lines = [f"{'# ' if md else ''}{document['contract']}"
             f" in {document['tree']}",
             f"verdict: {document['status']}"]
    narrowing = document.get("filters")
    if narrowing:
        lines.append("filters: " + "  ".join(
            stated(axis, values)
            for axis, values in sorted(narrowing.items())))
    counts = document["counts"]
    lines.append("counts: " + "  ".join(
        f"{coloured_glyph(state, colour)} {state} {counts[state]}"
        for state in STATES))
    coverage = document["coverage"]
    lines.append(f"  claimed {coverage['claimed']}"
                 f"  unclaimed {coverage['unclaimed']}")
    lines.append(f"  prose {document['prose_percent']}%"
                 f" of claimed non-blank lines")
    return lines


def unclaimed_lines(document, md):
    unclaimed = [record["path"] for record in document["files"]
                 if not record["layer"]]
    if not unclaimed:
        return []
    lines = [section_line("unclaimed files", md)]
    for path in unclaimed:
        lines.append(item_line(path, md))
    return lines
