import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.run.baseline import baseline_path

NAME = ".archituner-baseline.json"


def test_the_baseline_lives_beside_its_contract():
    tree = tempfile.mkdtemp()
    contract = os.path.join(tree, "ARCHITECTURE.md")
    with open(contract, "w", encoding="utf-8") as handle:
        handle.write("---\n")
    path = baseline_path(contract)
    assert os.path.dirname(path) == tree
    assert os.path.basename(path) == NAME
    assert not os.path.exists(path)


def test_the_path_is_the_contracts_whichever_way_it_is_spelled():
    tree = tempfile.mkdtemp()
    contract = os.path.join(tree, "sub", "..", "ARCHITECTURE.md")
    assert baseline_path(contract) == os.path.join(tree, NAME)


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
