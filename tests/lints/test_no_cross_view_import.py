# covers: archituner/presentation/page/views/**
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
VIEWS = os.path.join(ROOT, "archituner", "presentation", "page", "views")
FORBIDDEN = re.compile(r"archituner\.presentation\.page\.(?:views|shell)\b")


def sources():
    return sorted(glob.glob(os.path.join("**", "*.py"), root_dir=VIEWS,
                            recursive=True))


def findings():
    return [name + ": " + line.strip()
            for name in sources()
            for line in open(os.path.join(VIEWS, name),
                             encoding="utf-8").read().splitlines()
            if FORBIDDEN.search(line)]


def test_the_views_home_holds_the_modules_the_rule_judges():
    assert sources() != [], VIEWS


def test_a_view_imports_neither_the_shell_nor_another_view():
    assert findings() == [], findings()


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
