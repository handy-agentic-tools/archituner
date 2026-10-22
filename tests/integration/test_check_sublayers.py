# covers: archituner/__main__.py archituner/cli/** archituner/run/** archituner/contract/** archituner/source/** archituner/conformance/** archituner/presentation/** archituner/vocabulary/** archituner/matching/** archituner/theme/**
import json
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

CONTRACT = """---
layers:
  app:     ["src_app/@@@"]
  app.one: ["src_app/one/@@@"]
  app.two: ["src_app/two/@@@"]
  app.far: ["src_far/@@@"]

dependencies:
  allow:
    - app.one -> app.two
    - app.two -> app.one
    - app.one -> app.far
    - app.far -> app.one
    - app.two -> app.far
    - app.far -> app.two
---
""".replace("@@@", "**")

FLATS = ["src_app/flat_a.py", "src_app/flat_b.py", "src_app/flat_c.py"]
ESCAPEE = "src_far/escapee.py"
APP_GLOB = "src_app/" + "**"
FAR_GLOB = "src_far/" + "**"
ONE_GLOB = "src_app/one/" + "**"
TWO_GLOB = "src_app/two/" + "**"


def plant(tree, rel, text):
    path = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build(tree):
    plant(tree, "ARCHITECTURE.md", CONTRACT)
    for rel in FLATS + [ESCAPEE]:
        plant(tree, rel, "VALUE = 1\n")
    return os.path.join(tree, "ARCHITECTURE.md")


def drive(contract, *flags):
    proc = subprocess.run([sys.executable, "-m", "archituner", contract,
                           *flags], cwd=REPO, capture_output=True,
                          text=True, timeout=120)
    assert proc.returncode in (0, 1), (proc.returncode, proc.stdout,
                                       proc.stderr)
    return proc


def runs(contract):
    check = drive(contract, "--check")
    blob = drive(contract, "--json")
    report = drive(contract, "--report")
    findings = json.loads(blob.stdout)["findings"]
    return check, blob.stdout, report.stdout, \
        [f["text"] for f in findings], findings


def hole_text(path):
    return f"{path} is claimed by app's {APP_GLOB} and no child claims it"


def escape_text():
    return (f"{ESCAPEE} is claimed by app.far's {FAR_GLOB} but no glob "
            f"of its parent app claims it")


FINDING_TEXTS = (hole_text(FLATS[0]), hole_text(FLATS[1]),
                 hole_text(FLATS[2]), escape_text(),
                 f"glob matches nothing: app.one: {ONE_GLOB}",
                 f"glob matches nothing: app.two: {TWO_GLOB}")


def item_lines(report):
    return [line.strip() for line in report.splitlines()]


def reported(text, name, texts, report):
    assert text in texts, (name, texts)
    assert text in item_lines(report), (name, report)


def probe_free(finding):
    return ("probe" not in finding["text"]
            and "probe" not in finding["produced_by"])


def test_each_flat_file_is_reported_as_a_hole():
    with tempfile.TemporaryDirectory() as tree:
        _check, _blob, report, texts, _findings = runs(build(tree))
    for path in FLATS:
        reported(hole_text(path), path, texts, report)


def test_the_child_file_outside_its_parent_is_reported_as_an_escape():
    with tempfile.TemporaryDirectory() as tree:
        _check, _blob, report, texts, _findings = runs(build(tree))
    reported(escape_text(), ESCAPEE, texts, report)


def test_check_fails_naming_the_claim_findings_and_never_a_probe():
    with tempfile.TemporaryDirectory() as tree:
        check, _blob, _report, _texts, _findings = runs(build(tree))
    assert check.returncode != 0, (check.returncode, check.stdout,
                                   check.stderr)
    assert all(text in check.stdout for text in FINDING_TEXTS), \
        FINDING_TEXTS
    assert "probe" not in check.stdout, check.stdout


def test_no_mode_names_a_path_the_walk_did_not_find():
    with tempfile.TemporaryDirectory() as tree:
        _check, blob, report, _texts, findings = runs(build(tree))
    assert "probe" not in blob, blob
    assert "probe" not in report, report
    assert all(probe_free(f) for f in findings), findings


if __name__ == "__main__":
    failures = 0
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            try:
                test()
                print(f"PASS  {name}")
            except Exception as e:
                print(f"FAIL  {name}  {type(e).__name__}: {e}")
                failures += 1
    print(f"{failures} failed" if failures else "all green")
    raise SystemExit(1 if failures else 0)
