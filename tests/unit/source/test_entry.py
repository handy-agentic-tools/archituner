import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
import archituner.source.entry


def files_of(*records):
    return {path: {"layer": layer} for path, layer in records}


def test_no_claimed_main_names_no_entry():
    files = files_of(("pkg_a/entry.py", "app"), ("pkg_b/tool.py", "tool"))
    assert archituner.source.entry.entry_layer(files) is None, files


def test_the_first_main_in_path_order_wins():
    files = files_of(("tools/__main__.py", "tool"),
                     ("app/__main__.py", "app"))
    assert archituner.source.entry.entry_layer(files) == "app", files


def test_an_unclaimed_main_is_no_entry():
    files = files_of(("standalone/__main__.py", None),
                     ("loose/__main__.py", ""))
    assert archituner.source.entry.entry_layer(files) is None, files


def test_an_unclaimed_main_leaves_the_claimed_one_standing():
    files = files_of(("standalone/__main__.py", None),
                     ("cli/__main__.py", "cli"))
    assert archituner.source.entry.entry_layer(files) == "cli", files


def main():
    failures = 0
    tests = filter(lambda item: item[0].startswith("test_"),
                   sorted(globals().items()))
    for name, test in tests:
        try:
            test()
            print(f"PASS  {name}")
        except Exception as e:
            print(f"FAIL  {name}  {type(e).__name__}: {e}")
            failures += 1
    print(f"{failures} failed" if failures else "all green")
    return failures


if __name__ == "__main__":
    raise SystemExit(1 if main() else 0)
