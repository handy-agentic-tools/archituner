import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.run.siblings import cross_contract_names
from archituner.run.siblings import sibling_contracts

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


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
