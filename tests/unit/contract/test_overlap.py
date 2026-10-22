import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.contract.overlap import overlap_findings

ESCAPED = {"a": ["src_a/" + "**"], "b": ["src_b/" + "**"],
           "a.child": ["src_x/" + "**"]}
REACHED = {"a": ["src_a/" + "**"], "b": ["src_b/" + "**"],
           "a.child": ["src_a/child/" + "**"]}


def test_a_child_file_its_parent_does_not_claim_is_a_finding():
    findings = overlap_findings(ESCAPED)
    assert not any("probe" in f.text or "probe" in f.produced_by
                   for f in findings), \
        sorted((f.text, f.produced_by) for f in findings)


def test_a_parent_file_no_child_claims_is_a_finding():
    findings = overlap_findings(ESCAPED)
    assert not any("is claimed by" in f.text for f in findings), \
        sorted(f.text for f in findings)


def test_a_parent_child_overlap_is_not_an_overlap_finding():
    findings = overlap_findings(REACHED)
    assert not any("overlap" in f.text and "a.child" in f.text
                   for f in findings), \
        sorted(f.text for f in findings)


def run_one(pair):
    name, test = pair
    try:
        test()
        print(f"PASS  {name}")
        return 0
    except Exception as e:
        print(f"FAIL  {name}  {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    entries = sorted(filter(lambda item: item[0].startswith("test_"),
                            globals().items()))
    failures = sum(map(run_one, entries))
    print(("all green", f"{failures} failed")[bool(failures)])
    raise SystemExit(bool(failures))
