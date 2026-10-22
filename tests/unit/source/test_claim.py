import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, REPO)

from archituner.source.claim import claim_files
from archituner.source.claim import decoded_size
from archituner.vocabulary import Finding


def snippet_tree(files):
    directory = tempfile.mkdtemp()
    for path, body in files.items():
        full = os.path.join(directory, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(body)
    return directory


def named(findings, expected):
    texts = [f.text for f in findings]
    return findings[texts.index(expected)] if expected in texts else None


def test_ignored_file_is_not_walked():
    tree = snippet_tree({"app/keep.py": "import app.drop\n",
                         "app/drop.py": "import app.keep\n"})
    files, by_module, findings, _claims = claim_files(
        tree, {"app": ["app/" + "**"]}, "", ignore=["app/drop.py"])
    record = files["app/keep.py"]
    assert (sorted(files), sorted(by_module), record["imports"],
            record["importers"]) == (["app/keep.py"], ["app.keep"], [], []), \
        (sorted(files), sorted(by_module))


def test_ignore_glob_matching_nothing_is_a_finding():
    tree = snippet_tree({"app/keep.py": "x = 1\n"})
    files, by_module, findings, _claims = claim_files(
        tree, {"app": ["app/" + "**"]}, "", ignore=["gone/" + "*.py"])
    mine = named(findings, "ignore glob matches nothing: gone/" + "*.py")
    assert isinstance(mine, Finding), findings


def test_ignore_glob_taking_a_claimed_file_is_a_finding():
    tree = snippet_tree({"app/keep.py": "x = 1\n",
                         "app/drop.py": "y = 2\n"})
    files, by_module, findings, _claims = claim_files(
        tree, {"app": ["app/" + "**"]}, "", ignore=["app/drop.py"])
    expected = ("ignore glob app/drop.py takes app/drop.py, which layer "
                "app's app/" + "** would claim; ignore wins")
    mine = named(findings, expected)
    assert (sorted(files), isinstance(mine, Finding)) == \
        (["app/keep.py"], True), (sorted(files), findings)


def test_the_taken_finding_names_the_layers_first_matching_glob():
    tree = snippet_tree({"app/keep.py": "x = 1\n",
                         "app/drop.py": "y = 2\n"})
    files, by_module, findings, _claims = claim_files(
        tree, {"app": ["app/" + "**", "app/drop.py"]}, "",
        ignore=["app/drop.py"])
    expected = ("ignore glob app/drop.py takes app/drop.py, which layer "
                "app's app/" + "** would claim; ignore wins")
    assert named(findings, expected) is not None, findings


def test_a_layer_glob_matching_only_ignored_files_gets_the_vacancy():
    tree = snippet_tree({"app/keep.py": "x = 1\n",
                         "gen/made.py": "g = 1\n"})
    files, by_module, findings, _claims = claim_files(
        tree, {"app": ["app/" + "**"], "gen": ["gen/" + "**"]}, "",
        ignore=["gen/made.py"])
    taken = named(findings, "ignore glob gen/made.py takes gen/made.py, "
                            "which layer gen's gen/" + "** would claim; "
                            "ignore wins")
    vacant = named(findings, "glob matches nothing: gen: gen/" + "**")
    assert (sorted(files), isinstance(taken, Finding),
            isinstance(vacant, Finding)) == (["app/keep.py"], True, True), \
        findings


def test_ignore_entry_order_does_not_change_the_walk():
    tree = snippet_tree({"app/keep.py": "x = 1\n",
                         "app/a.py": "a = 1\n",
                         "app/b.py": "b = 1\n"})
    one = claim_files(tree, {"app": ["app/" + "**"]}, "",
                      ignore=["app/b.py", "app/a.py"])
    two = claim_files(tree, {"app": ["app/" + "**"]}, "",
                      ignore=["app/a.py", "app/b.py"])
    assert sorted(one[0]) == sorted(two[0]) == ["app/keep.py"], \
        (sorted(one[0]), sorted(two[0]))


def test_every_record_carries_its_size_in_decoded_characters():
    tree = snippet_tree({"app/keep.py": "X = 1\n",
                         "app/text.py": "V = 'éé'\n"})
    with open(os.path.join(tree, "app", "broken.py"), "wb") as handle:
        handle.write(b"\xff\xfe V = 1\n")
    files, by_module, findings, _claims = claim_files(
        tree, {"app": ["app/" + "**"]}, "")
    sizes = (files["app/keep.py"]["size"], files["app/text.py"]["size"])
    assert sizes == (6, 9), sizes
    record = files["app/broken.py"]
    assert (record["size"], record["defs"], record["cyclomatic"],
            decoded_size(tree, "app/broken.py")) == (None, 0, 1, None), record


TESTS = (test_ignored_file_is_not_walked,
         test_ignore_glob_matching_nothing_is_a_finding,
         test_ignore_glob_taking_a_claimed_file_is_a_finding,
         test_the_taken_finding_names_the_layers_first_matching_glob,
         test_a_layer_glob_matching_only_ignored_files_gets_the_vacancy,
         test_ignore_entry_order_does_not_change_the_walk,
         test_every_record_carries_its_size_in_decoded_characters)

failed = []
for test in TESTS:
    try:
        test()
        print(f"PASS  {test.__name__}")
    except Exception as e:
        print(f"FAIL  {test.__name__}  {type(e).__name__}: {e}")
        failed.append(test.__name__)
print(f"{len(failed)} failed" if failed else "all green")
raise SystemExit(bool(failed))
