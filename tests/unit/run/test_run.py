import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
import archituner.run as run
from archituner.run import analyse
from archituner.run import declared_version
from archituner.run import perform


def test_the_run_root_holds_the_three_stage_names_callable():
    assert callable(run.analyse)
    assert callable(run.perform)
    assert callable(run.declared_version)
    assert callable(analyse)
    assert callable(perform)
    assert callable(declared_version)


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
