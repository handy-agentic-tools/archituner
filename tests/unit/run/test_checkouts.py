import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.run.checkouts import contract_roots


def test_a_tree_whose_contract_cannot_be_decoded_declares_no_roots():
    parent = tempfile.mkdtemp()
    path = os.path.join(parent, "ARCHITECTURE.md")
    with open(path, "wb") as handle:
        handle.write(b"\xff\xfe\xfa\n")
    assert contract_roots(parent) == set()


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
