# covers: archituner/__main__.py archituner/cli/** archituner/run/** archituner/contract/** archituner/source/** archituner/conformance/** archituner/matching/** archituner/vocabulary/** archituner/presentation/** tests/unit/presentation/page/shell/test_page.py tests/unit/presentation/rejection/test_rejection.py tests/unit/theme/test_theme.py tests/lints/test_no_literal_styling.py tests/lints/test_no_view_geometry.py
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))


def drive(*paths):
    argv = [sys.executable, "-m", "archituner", "ARCHITECTURE.md", "--check"]
    for path in paths:
        argv += ["--file", path]
    return subprocess.run(argv, cwd=REPO, capture_output=True, text=True,
                          timeout=120)


def test_the_presentation_root_has_no_module_of_its_own():
    assert not os.path.exists(
        os.path.join(REPO, "archituner/presentation/__init__.py"))


def test_the_page_module_stands_within_its_limits():
    proc = drive("archituner/presentation/page/shell/page.py")
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    assert proc.stdout.splitlines() == ["no divergence"], proc.stdout


def test_the_rejection_module_stands_within_its_limits():
    proc = drive("archituner/presentation/rejection/rejection.py")
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    assert proc.stdout.splitlines() == ["no divergence"], proc.stdout


def test_the_page_mirror_stands_within_its_limits():
    proc = drive("tests/unit/presentation/page/shell/test_page.py")
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    assert proc.stdout.splitlines() == ["no divergence"], proc.stdout


def test_the_rejection_mirror_stands_within_its_limits():
    proc = drive("tests/unit/presentation/rejection/test_rejection.py")
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    assert proc.stdout.splitlines() == ["no divergence"], proc.stdout


def test_the_theme_mirror_stands_within_its_limits():
    proc = drive("tests/unit/theme/test_theme.py")
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    assert proc.stdout.splitlines() == ["no divergence"], proc.stdout


def test_the_literal_styling_lint_stands_within_its_limits():
    proc = drive("tests/lints/test_no_literal_styling.py")
    assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)
    assert proc.stdout.splitlines() == ["no divergence"], proc.stdout


def test_the_view_geometry_lint_stands_within_its_limits():
    proc = drive("tests/lints/test_no_view_geometry.py")
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
