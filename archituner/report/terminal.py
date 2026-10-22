from archituner.report.breaches import breaches_lines
from archituner.report.findings import divergences_lines
from archituner.report.findings import findings_lines
from archituner.report.matrix import matrix_lines
from archituner.report.records import files_lines
from archituner.report.records import prose_lines
from archituner.report.summary import summary_lines
from archituner.report.summary import unclaimed_lines


def terminal_report(document, fmt, colour):
    md = fmt == "md"
    colour = colour and not md
    lines = summary_lines(document, md, colour)
    lines += findings_lines(document, md)
    lines += breaches_lines(document, md)
    lines += matrix_lines(document, md, colour)
    lines += divergences_lines(document, md)
    lines += unclaimed_lines(document, md)
    lines += files_lines(document, md)
    lines += prose_lines(document, md)
    change = document["change"]
    if change:
        moved = change["counts"]
        lines.append(f"  vs baseline: improved {moved['improved']}"
                     f"  regressed {moved['regressed']}"
                     f"  unchanged {moved['unchanged']}")
    return "\n".join(lines)
