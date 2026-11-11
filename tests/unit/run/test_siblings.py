import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.run.siblings import cross_contract_names
from archituner.run.siblings import sibling_contracts
from archituner.run.siblings import sibling_tree

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

- `model -> *`: a representation computes nothing and depends on nothing.
- `core -> api`: a stage never reaches back to the thing that constructed it.
"""

LAYERS = {"api": ["api_*"], "core": ["core_*"], "model": ["model_*"]}

OTHER_CONTRACT = """---
layers:
  zeta: ["zeta_*"]
  eta:  ["eta_*"]

dependencies:
  allow:
    - zeta -> eta
  forbid:
    - eta -> zeta
---

## Boundaries

- `eta -> zeta`: a consumer never reaches back to the thing that constructed it.
"""


def plant(tree, rel, text):
    path = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def reads_as_no_sibling(path):
    assert sibling_tree(path) is None


def test_sibling_contracts_are_the_siblings_owning_one():
    parent = tempfile.mkdtemp()
    own = os.path.join(parent, "own")
    os.makedirs(own)
    plant(parent, "a/ARCHITECTURE.md", "a\n")
    plant(parent, "b/ARCHITECTURE.md", "b\n")
    plant(parent, "c/README.md", "c\n")
    plant(parent, "note.txt", "d\n")
    found = sibling_contracts(own)
    assert found == [os.path.join(parent, "a", "ARCHITECTURE.md"),
                     os.path.join(parent, "b", "ARCHITECTURE.md")]
    assert own not in found


def test_a_tree_whose_parent_is_gone_holds_no_siblings():
    parent = tempfile.mkdtemp()
    assert sibling_contracts(os.path.join(parent, "gone", "own")) == []


def test_a_question_naming_no_root_answers_none():
    parent = tempfile.mkdtemp()
    own = os.path.join(parent, "own")
    os.makedirs(own)
    plant(parent, "use/ARCHITECTURE.md", CONTRACT)
    plant(parent, "use/stray.py", "import api_\n")
    assert cross_contract_names(own, {}) is None
    assert cross_contract_names(own, {"x": ["*/y"]}) is None


def test_a_sibling_use_is_named_and_a_refusing_sibling_is_skipped():
    parent = tempfile.mkdtemp()
    own = os.path.join(parent, "own")
    os.makedirs(own)
    plant(parent, "use/ARCHITECTURE.md", CONTRACT)
    plant(parent, "use/stray.py", "import api_\n")
    plant(parent, "bad/ARCHITECTURE.md", "not a contract\n")
    plant(parent, "quiet/ARCHITECTURE.md", CONTRACT)
    plant(parent, "quiet/other.py", "VALUE = 1\n")
    found = cross_contract_names(own, LAYERS)
    assert found == {"names": [{"contract": "use", "file": "stray.py",
                                "module": "api_"}],
                     "contracts": ["use"]}


def test_siblings_naming_nothing_answer_none():
    parent = tempfile.mkdtemp()
    own = os.path.join(parent, "own")
    os.makedirs(own)
    plant(parent, "bad/ARCHITECTURE.md", "not a contract\n")
    assert cross_contract_names(own, LAYERS) is None
    plant(parent, "quiet/ARCHITECTURE.md", CONTRACT)
    plant(parent, "quiet/other.py", "VALUE = 1\n")
    assert cross_contract_names(own, LAYERS) is None


def test_a_sibling_declaring_a_root_this_tree_declares_is_not_a_subscriber():
    parent = tempfile.mkdtemp()
    own = os.path.join(parent, "own")
    os.makedirs(own)
    plant(own, "ARCHITECTURE.md", CONTRACT)
    plant(parent, "twin/ARCHITECTURE.md", CONTRACT)
    plant(parent, "other/ARCHITECTURE.md", OTHER_CONTRACT)
    found = sibling_contracts(own)
    assert found == [os.path.join(parent, "other", "ARCHITECTURE.md")], \
        "a sibling whose contract declares a package root this tree also " \
        "declares is another checkout of the same project, not a " \
        "subscriber; a sibling of different roots stays one"


def test_the_cross_contract_reading_skips_a_sibling_of_the_same_roots():
    parent = tempfile.mkdtemp()
    own = os.path.join(parent, "own")
    os.makedirs(own)
    plant(own, "ARCHITECTURE.md", CONTRACT)
    plant(parent, "twin/ARCHITECTURE.md", CONTRACT)
    plant(parent, "twin/stray.py", "import core_\n")
    plant(parent, "other/ARCHITECTURE.md", OTHER_CONTRACT)
    plant(parent, "other/stray.py", "import core_\n")
    found = cross_contract_names(own, LAYERS)
    assert found == {"names": [{"contract": "other", "file": "stray.py",
                                "module": "core_"}],
                     "contracts": ["other"]}, \
        "the cross-contract reading counts only siblings whose contract " \
        "declares no package root this tree declares"


GOOD_NAMES = {"names": [{"contract": "good", "file": "stray.py",
                         "module": "api_"}], "contracts": ["good"]}
GONE = "/nonexistent/target"


def sibling(parent, name, broken):
    tree = os.path.join(parent, name)
    os.makedirs(tree)
    plant(tree, "ARCHITECTURE.md", CONTRACT)
    plant(tree, "stray.py", "import api_\n")
    broken(tree)
    return tree


def gone_module(tree):
    os.symlink(GONE, os.path.join(tree, "gone.py"))


def sealed_gitignore(tree):
    os.symlink(os.path.dirname(tree), os.path.join(tree, ".gitignore"))


def undecodable_bytes(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(b"\xff\xfe\xfa\n")


def undecodable_contract(tree):
    undecodable_bytes(os.path.join(tree, "ARCHITECTURE.md"))


def own_beside(broken):
    parent = tempfile.mkdtemp()
    own = os.path.join(parent, "own")
    os.makedirs(own)
    sibling(parent, "use", broken)
    return own


def contributes_nothing(tree):
    assert cross_contract_names(tree, LAYERS) is None


def test_a_sibling_with_an_unreadable_file_contributes_nothing():
    contributes_nothing(own_beside(gone_module))
    contributes_nothing(own_beside(sealed_gitignore))
    contributes_nothing(own_beside(undecodable_contract))


def test_a_good_sibling_beside_broken_ones_still_contributes():
    parent = tempfile.mkdtemp()
    own = os.path.join(parent, "own")
    os.makedirs(own)
    plant(parent, "good/ARCHITECTURE.md", CONTRACT)
    plant(parent, "good/stray.py", "import api_\n")
    alone = cross_contract_names(own, LAYERS)
    sibling(parent, "use", gone_module)
    sibling(parent, "seal", sealed_gitignore)
    sibling(parent, "bad", undecodable_contract)
    os.makedirs(os.path.join(parent, "skip", "ARCHITECTURE.md"))
    assert cross_contract_names(own, LAYERS) == alone == GOOD_NAMES


def test_a_contract_path_that_cannot_be_read_as_a_contract_reads_as_no_sibling():
    parent = tempfile.mkdtemp()
    gone = os.path.join(parent, "gone", "ARCHITECTURE.md")
    reads_as_no_sibling(gone)
    directory = os.path.join(parent, "bad", "ARCHITECTURE.md")
    os.makedirs(directory)
    reads_as_no_sibling(directory)
    undecodable = os.path.join(parent, "rough", "ARCHITECTURE.md")
    undecodable_bytes(undecodable)
    reads_as_no_sibling(undecodable)


if __name__ == "__main__":
    entries = sorted(filter(lambda item: item[0].startswith("test_"),
                            globals().items()))
    for _, test in entries:
        test()
        print(f"PASS  {_}")
    print("all green")
