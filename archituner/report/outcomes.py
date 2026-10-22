from archituner.report.document import crossings_data
from archituner.report.document import crossings_document
from archituner.report.document import machine_document
from archituner.report.document import outcome_document
from archituner.report.report import check_report
from archituner.report.terminal import terminal_report

JSON_EXITS = {"ok": 0, "divergent": 1, "rejected": 2, "failed_run": 3}


def refused(contract_path, reason):
    return {"status": 2, "lines": [reason], "artifact": None}


def rejected(contract_path, reason):
    return {"status": 2, "lines": [outcome_document("rejected", reason)],
            "artifact": None}


def check_outcome(reading, narrowed, quoted, unclaimed, fmt, colour):
    if unclaimed:
        return {"status": 1, "lines": [unclaimed], "artifact": None}
    lines = check_report(dict(reading, pairs=narrowed["pairs"],
                              breaches=narrowed["breaches"],
                              claim_findings=narrowed.get("claim_findings",
                                                          [])))
    return {"status": 1 if lines else 0,
            "lines": lines or ["no divergence"], "artifact": None}


def json_outcome(reading, narrowed, quoted, unclaimed, fmt, colour):
    if unclaimed:
        return {"status": JSON_EXITS["failed_run"],
                "lines": [outcome_document("failed_run", unclaimed)],
                "artifact": None}
    document = machine_document(reading, narrowed)
    return {"status": JSON_EXITS[document["status"]],
            "lines": [crossings_document(document, narrowed, quoted)],
            "artifact": None}


def reading_outcome(reading, narrowed, quoted, unclaimed, fmt, colour):
    if unclaimed:
        return {"status": 1, "lines": [unclaimed], "artifact": None}
    document = machine_document(reading, narrowed)
    return {"status": JSON_EXITS[document["status"]],
            "lines": [terminal_report(crossings_data(
                document, narrowed, quoted), fmt, colour)],
            "artifact": None}
