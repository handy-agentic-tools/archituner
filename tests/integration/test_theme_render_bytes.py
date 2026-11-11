# covers: archituner/__main__.py archituner/cli/** archituner/run/** archituner/contract/** archituner/theme/** archituner/presentation/**
import hashlib
import os
import re
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

PAYLOAD = "const DATA = "
DIGEST = "6f070f69512aea5313df9f42ffa0a0a19b3dc6ac7991301df577340c196373c3"
BYTES = 90250

REPORT_DIGEST = "ad40ff0e3728b6ca3eb611f2142083a8040b4a7653b65cd2f0181d02b5511683"
REPORT_BYTES = 806

CONTRACT = """---
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

- `core -> api`: a stage never reaches back to the thing that constructed it.
"""

API_ENTRY = "import core_x\nVALUE = 1\n"
CORE_BACKBONE = "VALUE = 2\n"

REFUSED_CONTRACT = "layers:\n  api: [\"api_*\"]\n"


def drive(*args):
    return subprocess.run([sys.executable, "-m", "archituner", *args],
                          cwd=REPO, capture_output=True, text=True,
                          timeout=120)


def plant(tree, rel, text):
    path = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build(home):
    tree = os.path.join(home, "tree")
    plant(tree, "ARCHITECTURE.md", CONTRACT)
    plant(tree, "api_a.py", API_ENTRY)
    plant(tree, "core_x.py", CORE_BACKBONE)
    return os.path.join(tree, "ARCHITECTURE.md")


def past_payload(page):
    text = page.decode("utf-8")
    return "\n".join(line for line in text.splitlines()
                     if not line.startswith(PAYLOAD)).encode("utf-8")


def test_the_report_over_one_fixed_tree_hashes_the_digest_frozen_on_main():
    with tempfile.TemporaryDirectory() as home:
        contract = build(home)
        proc = drive(contract, "--report")
        assert proc.returncode == 0, \
            (proc.returncode, proc.stdout, proc.stderr)
        body = proc.stdout.encode("utf-8")
    assert len(body) == REPORT_BYTES, (len(body), REPORT_BYTES)
    assert hashlib.sha256(body).hexdigest() == REPORT_DIGEST, (
        hashlib.sha256(body).hexdigest(), REPORT_DIGEST)


def test_the_page_past_its_payload_line_hashes_the_same_digest_the_theme_must_not_move():
    contract = os.path.join(REPO, "ARCHITECTURE.md")
    with tempfile.TemporaryDirectory() as home:
        page = os.path.join(home, "page.html")
        proc = drive(contract, "-o", page)
        assert proc.returncode == 0, \
            (proc.returncode, proc.stdout, proc.stderr)
        body = past_payload(open(page, "rb").read())
    assert len(body) == BYTES, (len(body), BYTES)
    assert hashlib.sha256(body).hexdigest() == DIGEST, (
        hashlib.sha256(body).hexdigest(), DIGEST)


def test_a_refused_contract_renders_a_page_that_follows_the_system_ground():
    with tempfile.TemporaryDirectory() as home:
        tree = os.path.join(home, "tree")
        plant(tree, "ARCHITECTURE.md", REFUSED_CONTRACT)
        contract = os.path.join(tree, "ARCHITECTURE.md")
        page = os.path.join(tree, "page.html")
        proc = drive(contract, "-o", page)
        assert proc.returncode == 2, \
            (proc.returncode, proc.stdout, proc.stderr)
        body = open(page, encoding="utf-8").read()
    assert "prefers-color-scheme: dark" in body, (
        "the refusal page follows no ground: it spells no "
        "prefers-color-scheme block, so a system set to dark still draws "
        "the light ground")
    assert contract not in body, (
        "the refusal page shows the contract's absolute path, which "
        "uispec.md forbids the artifact to show")


TAB_RULE = re.compile(r'(#panel-tabs[^{}]*)\{([^{}]*)\}')
LITERAL = re.compile(r'#[0-9a-fA-F]{6}\b|\b\d[\d.]*(?:px|rem|em)\b')


def test_the_panel_s_tab_dress_spends_the_theme_by_name():
    with tempfile.TemporaryDirectory() as home:
        page = os.path.join(home, 'page.html')
        proc = drive(os.path.join(REPO, 'ARCHITECTURE.md'), '-o', page)
        assert proc.returncode == 0, \
            (proc.returncode, proc.stdout, proc.stderr)
        with open(page, encoding='utf-8') as handle:
            sheet = handle.read().partition('<style>')[2] \
                .partition('</style>')[0]
    rules = TAB_RULE.findall(sheet)
    assert rules, 'the page carries no #panel-tabs dress'
    literal = LITERAL.search(
        '\n'.join(one[0] + one[1] for one in rules))
    assert literal is None, literal.group()


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
