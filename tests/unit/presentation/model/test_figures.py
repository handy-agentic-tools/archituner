import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, REPO)
try:
    import archituner.presentation.model.figures as figures
except ModuleNotFoundError:
    figures = None

CONTRACT = os.path.join(REPO, "ARCHITECTURE.md")
MIRRORED = os.path.join("archituner", "presentation", "model", "figures.py")

NAMES = ("cli", "run", "presentation")
NAMES_PLUS = NAMES + ("theme",)
USERS = ("tests_unit", "run", "presentation")
USERS_PLUS = USERS + ("conformance",)
USED_BY = ("run",)
USED_BY_PLUS = USED_BY + ("matching",)
USES = ("theme",)
USES_PLUS = USES + ("vocabulary",)


def unpinned(figure):
    def missing(*_):
        return figure + " lands in no function of the figures module"
    return missing


def box(name, x, y, width, height):
    return {"name": name, "x": x, "y": y, "width": width, "height": height}


def join(x1, x2, y):
    return {"x1": x1, "x2": x2, "y": y}


def line(x, y1, y2):
    return {"x": x, "y1": y1, "y2": y2}


CHAIN_FIG = {"width": 160, "height": 86, "on": "presentation",
             "boxes": [box("cli",0,0,140,20), box("run",0,32,140,20),
                       box("presentation",0,64,140,20)],
             "arrows": [line(70,21,32), line(70,53,64)]}
CHAIN_FIG_PLUS = dict(CHAIN_FIG, height=118,
                      boxes=CHAIN_FIG["boxes"] + [box("theme",0,96,140,20)],
                      arrows=CHAIN_FIG["arrows"] + [line(70,85,96)])
BUS_FIG = {"width": 280, "height": 72,
           "users": [box("tests_unit",0,0,110,20), box("run",0,25,110,20),
                     box("presentation",0,50,110,20)],
           "joins": [join(110,130,10), join(110,130,35), join(110,130,60)],
           "bus": line(130,10,60), "arrow": join(130,160,35),
           "layer": box("vocabulary",160,25,110,20)}
BUS_FIG_PLUS = dict(BUS_FIG, height=97,
                    users=BUS_FIG["users"] + [box("conformance",0,75,110,20)],
                    joins=BUS_FIG["joins"] + [join(110,130,85)],
                    bus=line(130,10,85))
TREE_FIG = {"width": 200, "height": 118,
            "labels": {"used_by": {"x": 26, "y": 10}, "uses": {"x": 26, "y": 87}},
            "used_by": [box("run",26,16,140,20)],
            "joins": [join(10,26,26)], "into": line(10,26,47),
            "layer": box("presentation",0,47,166,20),
            "uses": [box("theme",26,93,140,20)],
            "heads": [join(10,26,103)], "out": line(10,68,103), "spare": {}}
TREE_FIG_USED = dict(TREE_FIG, height=143,
                     labels={"used_by": {"x": 26, "y": 10},
                             "uses": {"x": 26, "y": 112}},
                     used_by=[box("run",26,16,140,20),
                              box("matching",26,41,140,20)],
                     joins=[join(10,26,26), join(10,26,51)],
                     into=line(10,26,72),
                     layer=box("presentation",0,72,166,20),
                     uses=[box("theme",26,118,140,20)],
                     heads=[join(10,26,128)], out=line(10,93,128))
TREE_FIG_USES = dict(TREE_FIG, height=143,
                     uses=[box("theme",26,93,140,20),
                           box("vocabulary",26,118,140,20)],
                     heads=[join(10,26,103), join(10,26,128)],
                     out=line(10,68,128))
TREE_FIG_NOTHING = dict(TREE_FIG, used_by=[], joins=[], into=None,
                        uses=[], heads=[], out=None,
                        spare={"used_by": {"x": 26, "y": 16},
                               "uses": {"x": 26, "y": 93}})


def test_the_panel_figures_land_in_the_figures_module():
    chain = getattr(figures, "chain_column", unpinned("the chain column"))
    bus = getattr(figures, "relied_on", unpinned("the most-relied-on figure"))
    tree = getattr(figures, "uses_tree", unpinned("the uses tree"))
    drawn = (chain(NAMES, "presentation"), bus(USERS, "vocabulary"),
             tree(USED_BY, "presentation", USES),
             tree((), "presentation", ()))
    assert drawn == (CHAIN_FIG, BUS_FIG, TREE_FIG, TREE_FIG_NOTHING), drawn


def test_adding_one_name_moves_one_row_and_nothing_else():
    chain = getattr(figures, "chain_column", unpinned("the chain column"))
    bus = getattr(figures, "relied_on", unpinned("the most-relied-on figure"))
    tree = getattr(figures, "uses_tree", unpinned("the uses tree"))
    drawn = (chain(NAMES_PLUS, "presentation"),
             bus(USERS_PLUS, "vocabulary"),
             tree(USED_BY_PLUS, "presentation", USES),
             tree(USED_BY, "presentation", USES_PLUS))
    assert drawn == (CHAIN_FIG_PLUS, BUS_FIG_PLUS, TREE_FIG_USED,
                     TREE_FIG_USES), drawn


def drive():
    return subprocess.run(
        [sys.executable, "-m", "archituner", CONTRACT,
         "--check", "--file", MIRRORED],
        capture_output=True, text=True, cwd=REPO)


def test_the_figures_module_sits_within_its_limits():
    one, two = drive(), drive()
    assert (one.returncode, one.stdout) == (two.returncode, two.stdout), \
        (one.returncode, two.returncode, one.stdout, one.stderr)
    assert one.returncode == 0, (one.returncode, one.stdout, one.stderr)
    assert one.stdout.splitlines() == ["no divergence"], one.stdout


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
