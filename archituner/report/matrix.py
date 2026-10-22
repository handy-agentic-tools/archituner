from archituner.report.spelling import coloured_glyph
from archituner.report.spelling import section_line


def matrix_lines(document, md, colour):
    order = document["order"]
    lines = [section_line(
        "matrix: rows import columns; layers in dependency order", md)]
    width = max(len(name) for name in order)
    place = {name: at for at, name in enumerate(order)}
    cells = {name: [" "] * len(order) for name in order}
    for pair in document["pairs"]:
        cells[pair["source"]][place[pair["target"]]] = coloured_glyph(
            pair["state"], colour)
    if md:
        lines.append("")
        lines.append("| " + " | ".join([""] + order) + " |")
        lines.append("|" + " --- |" * (len(order) + 1))
        for source in order:
            lines.append(f"| {source} | " + " | ".join(cells[source]) + " |")
    else:
        lines.append(" " * (width + 4)
                     + "".join(name.ljust(width + 2) for name in order))
        for source in order:
            lines.append("  " + source.ljust(width + 2) + "".join(
                mark + " " * (width + 1) for mark in cells[source]))
    return lines
