from archituner.report.spelling import item_line
from archituner.report.spelling import section_line


def breaches_lines(document, md):
    lines = [section_line("limit breaches", md)]
    breaches = sorted(document["breaches"],
                      key=lambda b: (b["file"], b["number"]))
    if not breaches:
        lines.append(item_line("no limit breaches", md))
    for breach in breaches:
        text = (f"{breach['file']}: {breach['number']}"
                f" {breach['value']} over {breach['limit']}")
        if breach["reason"]:
            text += f" - {breach['reason']}"
        lines.append(item_line(text, md))
    return lines
