import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.vocabulary import Contract


def test_a_contract_value_defaults_to_no_limits():
    contract = Contract(path="ARCHITECTURE.md", layers={}, pairs={},
                        naming=[], package_root=None, body="", findings=[])
    assert contract.limits == {}, contract.limits
    assert contract.overrides == [], contract.overrides


def test_two_contracts_built_without_the_block_share_no_default_object():
    first = Contract(path="ARCHITECTURE.md", layers={}, pairs={},
                     naming=[], package_root=None, body="", findings=[])
    second = Contract(path="ARCHITECTURE.md", layers={}, pairs={},
                      naming=[], package_root=None, body="", findings=[])
    assert first.limits is not second.limits, (first.limits, second.limits)
    assert first.overrides is not second.overrides, \
        (first.overrides, second.overrides)


def run_one(pair):
    name, test = pair
    try:
        test()
        print(f"PASS  {name}")
        return 0
    except Exception as e:
        print(f"FAIL  {name}  {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    entries = sorted(filter(lambda item: item[0].startswith("test_"),
                            globals().items()))
    failures = sum(map(run_one, entries))
    print(("all green", f"{failures} failed")[bool(failures)])
    raise SystemExit(bool(failures))
