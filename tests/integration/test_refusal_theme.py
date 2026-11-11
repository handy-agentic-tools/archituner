# covers: archituner/presentation/rejection/** archituner/theme/**
import os
import re
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
BAD = 'layers:\n  api: ["src/@@@"]\n'.replace("@@@", "*")
BASE = "clamp(0.8px, 0.0625rem, 0.18vw)"


def test_the_refused_contract_renders_the_theme_s_ladder_and_face():
    with tempfile.TemporaryDirectory() as home:
        contract = os.path.join(home, "ARCHITECTURE.md")
        with open(contract, "w", encoding="utf-8") as handle:
            handle.write(BAD)
        page = os.path.join(home, "rejection.html")
        done = subprocess.run([sys.executable, "-m", "archituner", contract,
                               "-o", page], cwd=REPO, capture_output=True,
                              text=True, timeout=120)
        assert done.returncode == 2, (done.returncode, done.stdout, done.stderr)
        with open(page, encoding="utf-8") as handle:
            body = handle.read()
    assert BASE in body, "the refusal page never defines the base unit"
    assert "var(--u)" in body, "the refusal page holds no dimension off --u"
    assert "ui-monospace" in body, \
        "the refusal page keeps a face from outside the theme"
    assert "system-ui" not in body, body[:200]
    assert not [line for line in body.splitlines()
                if BASE not in line
                and re.search(r"\d[\d.]*(?:px|rem|em)\b", line)], \
        "the refusal page holds a fixed dimension"
    assert "prefers-color-scheme: dark" in body, \
        "the refusal page lost the second ground"


def outcome_of(name, test):
    try:
        test()
        print(f"PASS  {name}")
        return 0
    except Exception as e:
        print(f"FAIL  {name}  {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    failures = sum(map(lambda pair: outcome_of(*pair),
                       filter(lambda pair: pair[0].startswith("test_"),
                              sorted(globals().items()))))
    print(("all green", f"{failures} failed")[bool(failures)])
    raise SystemExit(bool(failures))
