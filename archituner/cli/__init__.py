import sys

from archituner.cli.intent import read
from archituner.cli.page import page_builder
from archituner.cli.page import page_refusal
from archituner.report.outcomes import check_outcome
from archituner.report.outcomes import json_outcome
from archituner.report.outcomes import reading_outcome
from archituner.report.outcomes import refused
from archituner.report.outcomes import rejected
from archituner.run import declared_version
from archituner.run import perform

USAGE = ("usage: archituner <ARCHITECTURE.md> (the check) [-o <file>] "
         "[--check] [--baseline] [--json]\n"
         "       [--report [--format md]] [--layer l ...] [--state s ...] "
         "[--file p ...]\n"
         "       [--min-weight n]")

DOORS = {"baseline": (None, refused),
         "check": (check_outcome, refused),
         "json": (json_outcome, rejected),
         "render": (page_builder, page_refusal),
         "report": (reading_outcome, refused)}


def console():
    return main(sys.argv)


def main(argv):
    flags = argv[1:]
    if "--help" in flags or "-h" in flags:
        print(USAGE)
        return 0
    if "--version" in flags:
        print(declared_version())
        return 0
    intent = read(argv)
    if intent is None:
        print(USAGE, file=sys.stderr)
        return 2
    mode, narrowing, fmt = intent
    out = argv[argv.index("-o") + 1] if "-o" in flags else "archituner.html"
    builder, refusal = DOORS[mode]
    narrowing = narrowing or ({} if mode == "check" else None)
    outcome = perform(argv[1], out, builder, refusal, narrowing, fmt)
    for line in outcome["report"]:
        print(line)
    return outcome["status"]
