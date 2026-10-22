import json
import os

from archituner.conformance import baseline_of


def baseline_path(contract_path):
    return os.path.join(os.path.dirname(os.path.abspath(contract_path)), ".archituner-baseline.json")


def stored_baseline(contract_path, writing):
    if writing or not os.path.exists(baseline_path(contract_path)):
        return None
    with open(baseline_path(contract_path), encoding="utf-8") as handle:
        return json.load(handle)


def baseline_outcome(contract_path, result, unclaimed, report):
    if unclaimed:
        report.append(unclaimed)
        return {"status": 1, "report": report}
    path = baseline_path(contract_path)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(baseline_of(result), handle, indent=1, sort_keys=True)
    report.append(f"baseline written: {path}")
    return {"status": 0, "report": report}
