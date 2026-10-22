import fnmatch
import glob
import os
import re
import subprocess
import sys
from itertools import compress

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNIT = "tests/unit"
FLOWS = "tests/integration"
LINTS = "tests/lints"
ARCH = "archituner/"
COVERS = "# covers:"
SHEBANG = "#!"
PARDIR = os.pardir
MATCH_ALL = re.compile(".*")
UNIT_TEST = "/".join((UNIT, "*", "test_*.py"))
MIRROR = re.compile(r"(.+)/(.+)\.py")


def at(rel):
    return os.path.join(ROOT, *rel.split("/"))


def unit_mirror(rel):
    rel = rel.removeprefix(ARCH)
    found = MIRROR.fullmatch(rel)
    if not found:
        return ""
    directory, name = found.group(1), found.group(2)
    name = (directory.rsplit("/", 1)[-1] if name == "__init__" else name)
    return f"{UNIT}/{directory}/test_{name}.py"


def files_of(directory):
    try:
        names = os.listdir(at(directory))
    except OSError:
        return []
    return [f"{directory}/{name}" for name in sorted(names)
            if os.path.isfile(at(f"{directory}/{name}"))]


def covers_of(rel):
    try:
        with open(at(rel), encoding="utf-8", errors="replace") as handle:
            lines = handle.read().splitlines()
    except OSError:
        return MATCH_ALL
    if not lines:
        return MATCH_ALL
    anchor = lines[0].startswith(SHEBANG)
    line = "".join(lines[anchor:anchor + 1])
    if not line.startswith(COVERS):
        return MATCH_ALL
    globs = line[len(COVERS):].split()
    return re.compile("|".join(map(fnmatch.translate, globs)) or ".*")


def every_test():
    found = sorted(glob.glob(os.path.join(at(UNIT), "*", "test_*.py")))
    tests = [os.path.relpath(path, ROOT).replace(os.sep, "/")
             for path in found]
    tests.extend(files_of(FLOWS))
    tests.extend(files_of(LINTS))
    return tests


def selected_by(path, names, matchers):
    rel = os.path.relpath(os.path.normpath(os.path.join(ROOT, path)), ROOT)
    if rel.split(os.sep, 1)[0] == PARDIR:
        return []
    rel = rel.replace(os.sep, "/")
    mirror = unit_mirror(rel)
    chosen = [mirror] if os.path.isfile(at(mirror)) else []
    hit = os.path.normcase(rel)
    if (fnmatch.fnmatch(rel, UNIT_TEST)
            or os.path.dirname(rel) in (FLOWS, LINTS)):
        chosen.append(rel)
    chosen.extend(compress(names, map(lambda m: m.match(hit), matchers)))
    return chosen


def run_tests(tests):
    failed = 0
    for test in sorted(tests):
        done = subprocess.run([sys.executable, at(test)], cwd=ROOT,
                              capture_output=True)
        failed += done.returncode != 0
        mark = "FAIL" if done.returncode else "PASS"
        print(f"{mark}  {test}")
    if failed:
        return 1
    print("all green")
    return 0


def main(paths):
    names = files_of(FLOWS) + files_of(LINTS)
    matchers = list(map(covers_of, names))
    if not paths:
        return run_tests(set(every_test()))
    chosen, refused = set(), []
    for path in paths:
        selected = selected_by(path, names, matchers)
        chosen.update(selected)
        if not selected:
            refused.append(path)
    message = "".join(f"no test selects {path}\n" for path in refused)
    if message:
        print(message, end="", file=sys.stderr)
        return 1
    return run_tests(chosen)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
