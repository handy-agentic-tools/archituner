import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.contract.boundaries import boundaries_reasons


def test_a_boundaries_bullet_naming_a_non_sibling_pair_is_a_finding():
    reasons, findings = boundaries_reasons(
        "- `a.child -> b`: why", ["a", "b", "a.child"], {("b", "a")})
    assert ("a.child", "b") not in reasons, reasons
    named = [f for f in findings if "a.child -> b" in f.text]
    assert any("non-sibling" in f.text for f in named), \
        sorted(f.text for f in findings)
    reasons, _ = boundaries_reasons(
        "- `a -> *`: walls", ["a", "b", "a.child"], {("b", "a")})
    assert reasons == {("a", "b"): "walls"}, reasons


def test_a_vacuous_wildcard_bullet_on_a_flat_contract_still_names_no_real_edge():
    _, findings = boundaries_reasons(
        "- `a -> *`: walls", ["a", "b"], {("a", "b")})
    assert any("no real edge" in f.text for f in findings), \
        sorted(f.text for f in findings)


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
