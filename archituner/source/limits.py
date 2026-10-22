from archituner.matching import glob_matcher
from archituner.matching import match_path
from archituner.vocabulary import Finding


def layer_files(selector, files):
    return {path for path, record in files.items()
            if record["layer"] == selector}


def reached_files(selector, layers, files):
    if selector in layers:
        return layer_files(selector, files)
    matcher = glob_matcher(selector)
    return {path for path in files if match_path(matcher, path)}


def selector_findings(overrides, layers, files):
    reach = []
    findings = []
    for number, selector, value, reason in overrides:
        reached = reached_files(selector, layers, files)
        if not reached:
            findings.append(Finding(
                text=f"limits selector reaches no file: {selector}",
                produced_by=f"limits override {number} `{selector}`"))
        reach.append((number, value, reason, reached))
    return reach, findings


def selects(named, reached, number, path):
    return named == number and path in reached


def governed_limit(number, default, path, reach):
    for named, value, why, reached in reach:
        if selects(named, reached, number, path):
            return value, why
    return default, None


def governed_of(number, default, measured, path, reach):
    limit, reason = governed_limit(number, default, path, reach)
    share = None if measured is None or not limit else round(measured / limit, 2)
    breach = None
    if limit is not None and measured is not None and measured > limit:
        breach = {"file": path, "number": number, "value": measured,
                  "limit": limit, "reason": reason}
    return {"limit": limit, "share": share}, breach


def record_limits(path, record, limits, reach):
    governed = {number: governed_of(number, limits[number], record[number],
                                    path, reach)
                for number in limits if number in record}
    record["limits"] = {number: outcome
                        for number, (outcome, _breach) in governed.items()}
    return [breach for _number, (_outcome, breach) in governed.items()
            if breach]


def measure_limits(files, layers, limits, overrides):
    reach, findings = selector_findings(overrides, layers, files)
    breaches = []
    for path, record in files.items():
        breaches += record_limits(path, record, limits, reach)
    breaches.sort(key=lambda b: (b["file"], b["number"]))
    return breaches, findings
