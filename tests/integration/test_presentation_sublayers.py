# covers: archituner/__main__.py archituner/cli/** archituner/run/** archituner/contract/** archituner/source/** archituner/conformance/** archituner/matching/** archituner/vocabulary/** archituner/theme/** archituner/presentation/**
import hashlib
import json
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

PACKAGE_INIT = "archituner/presentation/__init__.py"
DIGEST = "18d367e5438a0bdd82010b623df84191cea8e2d0c54b034c96d684de920aa863"
BYTES = 1387

CONTRACT = """---
package_root: "."

limits:
  size: 8000
  defs: 8
  depth: 4
  cyclomatic: 30
  cognitive: 50
  prose_count: 0

  overrides:
    - "size `core`: 40 - a table of tokens, no logic"

layers:
  api:   ["api_*"]
  core:  ["core_*"]
  model: ["model_*"]

dependencies:
  allow:
    - api -> core
    - api -> model
    - core -> model
  forbid:
    - core -> api
    - model -> api
    - model -> core
---

## Boundaries

- `model -> *`: a representation computes nothing and depends on nothing.
- `core -> api`: a stage never reaches back to the thing that constructed it.
"""

PLANTED = (
    ("api_x.py", "# a note the reader sees\nimport core_y\nimport model_z\n"
                 "VALUE = 1\n"),
    ("core_y.py", "VALUE = " + " ".join(str(i) for i in range(30)) + "\n"),
    ("model_z.py", "import core_y\nVALUE = 2\n"),
    ("extra_q.py", "VALUE = 3\n"),
)


def finding_texts():
    proc = subprocess.run([sys.executable, "-m", "archituner",
                           "ARCHITECTURE.md", "--json"], cwd=REPO,
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode in (0, 1), (proc.returncode, proc.stdout,
                                       proc.stderr)
    document = json.loads(proc.stdout)
    return [finding["text"] for finding in document["findings"]]


def divergence_lines():
    proc = subprocess.run([sys.executable, "-m", "archituner",
                           "ARCHITECTURE.md", "--check"], cwd=REPO,
                          capture_output=True, text=True, timeout=120)
    return proc.stdout.splitlines()


def report_of():
    with tempfile.TemporaryDirectory() as home:
        tree = os.path.join(home, "tree")
        os.makedirs(tree)
        with open(os.path.join(tree, "ARCHITECTURE.md"), "w") as handle:
            handle.write(CONTRACT)
        for name, text in PLANTED:
            with open(os.path.join(tree, name), "w") as handle:
                handle.write(text)
        proc = subprocess.run(
            [sys.executable, "-m", "archituner",
             os.path.join(tree, "ARCHITECTURE.md"), "--report"],
            cwd=REPO, capture_output=True, timeout=120)
    assert proc.returncode == 1, (proc.returncode, proc.stdout[:400],
                                  proc.stderr[:400])
    return proc.stdout


def lines_starting_with(lines, prefix):
    return [line for line in lines if line.startswith(prefix)]


def test_no_finding_names_a_flat_file_under_presentation():
    strays = [text for text in finding_texts()
              if " and no child claims it" in text
              and not text.startswith(PACKAGE_INIT + " ")]
    assert strays == [], strays


def test_every_presentation_sublayer_glob_claims_its_files():
    empty = lines_starting_with(
        finding_texts(), "glob matches nothing: presentation.")
    assert empty == [], empty


def test_no_divergence_names_an_edge_between_the_sublayers():
    edges = lines_starting_with(
        divergence_lines(), "divergence: presentation.")
    assert edges == [], edges


def test_a_rerun_of_a_planted_tree_renders_the_same_report_bytes():
    assert report_of() == report_of()


def test_a_report_over_a_planted_tree_hashes_the_digest_frozen_on_main():
    body = report_of()
    assert len(body) == BYTES, (len(body), BYTES)
    assert hashlib.sha256(body).hexdigest() == DIGEST, (
        hashlib.sha256(body).hexdigest(), DIGEST)


def run_one(name, test):
    try:
        test()
        print(f"PASS  {name}")
        return 0
    except Exception as e:
        print(f"FAIL  {name}  {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    failures = 0
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            failures += run_one(name, test)
    print(f"{failures} failed" if failures else "all green")
    raise SystemExit(1 if failures else 0)
