# covers: archituner/__main__.py archituner/cli/** archituner/run/** archituner/contract/** archituner/source/** archituner/conformance/classification.py archituner/conformance/proposal.py archituner/presentation/**
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))


def drive(*args):
    return subprocess.run([sys.executable, "-m", "archituner", *args],
                          cwd=REPO, capture_output=True, text=True,
                          timeout=120)


def test_the_page_module_stands_within_its_limits():
    proc = drive("ARCHITECTURE.md", "--check",
                 "--file", "archituner/presentation/page/shell/page.py")
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    assert proc.stdout.splitlines() == ["no divergence"], proc.stdout


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
