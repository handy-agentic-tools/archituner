import os
import sys

from archituner.conformance import compare
from archituner.conformance.visibility import narrow
from archituner.run.analysis import analyse
from archituner.run.baseline import baseline_outcome
from archituner.run.baseline import baseline_path
from archituner.run.baseline import stored_baseline
from archituner.run.outcomes import page_lines
from archituner.run.outcomes import quoted_lines
from archituner.run.outcomes import visible_claims
from archituner.run.paths import file_axis


def zero_claim(result):
    if not any(f["layer"] for f in result["files"]):
        return (f"failed run: {len(result['files'])} file(s) walked, "
                f"none claimed by any layer")
    return None


def refused_outcome(out, refusal, contract_path, reason, report):
    answer = refusal(contract_path, reason)
    report += answer["lines"]
    if answer["artifact"] is not None:
        open(out, "w", encoding="utf-8").write(answer["artifact"])
        report.append(f"  -> {out}")
    return {"status": answer["status"], "report": report}


def perform(contract_path, out, builder, refusal, narrowing=None, fmt=None):
    report = []
    narrowing = narrowing if narrowing is not None else {}
    tree = os.path.dirname(os.path.abspath(contract_path))
    stored = stored_baseline(contract_path, builder is None)
    try:
        result = analyse(contract_path, stored)
    except SystemExit as stop:
        return refused_outcome(out, refusal, contract_path, str(stop), report)
    unclaimed = zero_claim(result)
    if builder is None:
        return baseline_outcome(contract_path, result, unclaimed, report)
    narrowing, missing = file_axis(tree, narrowing)
    result["baseline"] = os.path.basename(baseline_path(contract_path))
    result["change"] = compare(result, stored) if stored else None
    narrowed = dict(narrow(result, narrowing),
                    claim_findings=visible_claims(result.claims, narrowing)
                    + missing)
    quoted = quoted_lines(tree, narrowed["witnesses"])
    colour = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
    answer = builder(result, narrowed, quoted, unclaimed, fmt, colour)
    report += answer["lines"]
    if answer["artifact"] is not None:
        open(out, "w", encoding="utf-8").write(answer["artifact"])
        report += page_lines(result, contract_path, out)
    return {"status": answer["status"], "report": report}
