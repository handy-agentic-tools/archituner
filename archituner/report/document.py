import dataclasses
import json

from archituner.vocabulary import REALISED

REASONS = {(True, True): "divergence and limit breach",
           (True, False): "divergence",
           (False, True): "limit breach"}


def outcome_document(status, reason):
    return json.dumps({"schema": 1, "status": status, "reason": reason},
                      indent=2, ensure_ascii=False, sort_keys=True)


def machine_document(reading, narrowed):
    return dict(reading,
                status="divergent"
                if narrowed["diverged"] or narrowed["breaches"] else "ok",
                reason=REASONS.get((narrowed["diverged"],
                                    bool(narrowed["breaches"]))),
                breaches=narrowed["breaches"])


def crossings_data(data, narrowed, quoted):
    crossings = [{"file": w["file"], "line": w["line"], "module": w["module"],
                  "source": p["source"], "target": p["target"],
                  "kind": p["kind"], "state": p["state"],
                  "code": quoted[(w["file"], w["line"])]}
                 for p in narrowed["pairs"]
                 if p["state"] in REALISED
                 for w in p["imports"]]
    crossings.sort(key=lambda c: (c["source"], c["target"], c["file"],
                                  c["line"], c["module"]))
    document = dict(data, schema=1, crossings=crossings)
    if narrowed["narrowing"]:
        document["files"] = narrowed["files"]
        document["filters"] = narrowed["narrowing"]
    return document


def crossings_document(data, narrowed, quoted):
    return json.dumps(crossings_data(data, narrowed, quoted),
                      indent=2, ensure_ascii=False, sort_keys=True,
                      default=dataclasses.asdict)
