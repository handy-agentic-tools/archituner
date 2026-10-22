import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from archituner.run.prose import measure_prose

LINE_FORM = "/" + "/"
BLOCK_FORM = "/" + "*"
MARKUP_FORM = "<" + "!--"


def plant(tree, rel, text):
    with open(os.path.join(tree, rel), "w", encoding="utf-8") as handle:
        handle.write(text)


def build(files):
    tree = tempfile.mkdtemp()
    for rel, text in files.items():
        plant(tree, rel, text)
    return tree


def test_a_comment_and_a_docstring_join_their_record_as_rows():
    tree = build({
        "dirty.py": "def f():\n    return 1  # tail\n",
        "talked.py": 'def g():\n    """quoted"""\n    return 2\n',
    })
    records = {"dirty.py": {"path": "dirty.py", "layer": "api"},
               "talked.py": {"path": "talked.py", "layer": "api"}}
    figure = measure_prose(tree, records)
    assert records["dirty.py"]["prose"] == [
        {"line": 2, "text": "return 1  # tail"}]
    assert records["talked.py"]["prose"] == [
        {"line": 2, "text": '"""quoted"""'}]
    assert (records["dirty.py"]["prose_count"],
            records["dirty.py"]["prose_percent"],
            records["talked.py"]["prose_count"],
            records["talked.py"]["prose_percent"],
            figure) == (1, 50.0, 1, 33.3, 40.0)


def test_one_line_refused_by_two_forms_folds_to_one_entry():
    tree = build({"forms.py": f'S = "a {LINE_FORM} b {BLOCK_FORM} c '
                              f'{MARKUP_FORM} d"  # tail\n'})
    records = {"forms.py": {"path": "forms.py", "layer": "core"}}
    figure = measure_prose(tree, records)
    assert (records["forms.py"]["prose"],
            records["forms.py"]["prose_count"],
            records["forms.py"]["prose_percent"],
            figure) == (
        [{"line": 1,
          "text": f'S = "a {LINE_FORM} b {BLOCK_FORM} c {MARKUP_FORM} d"'
                  "  # tail"}], 1, 100.0, 100.0)


def test_a_file_no_layer_claims_joins_neither_side_of_the_figure():
    tree = build({
        "stray.py": "# prose nobody claims\nVALUE = 1\n",
        "clean.py": "VALUE = 1\n\nVALUE = 2\n",
    })
    stray = {"path": "stray.py", "layer": None}
    records = {"stray.py": stray,
               "clean.py": {"path": "clean.py", "layer": "api"}}
    figure = measure_prose(tree, records)
    assert set(stray) == {"path", "layer"}
    assert (records["clean.py"]["prose_count"],
            records["clean.py"]["prose_percent"], figure) == (0, 0.0, 0.0)


def test_a_file_the_gate_cannot_parse_loses_its_rows_keeps_its_lines():
    tree = build({
        "dirty.py": "def f():\n    return 1  # tail\n",
        "broken.py": "def broken(:\n",
    })
    records = {"dirty.py": {"path": "dirty.py", "layer": "api"},
               "broken.py": {"path": "broken.py", "layer": "api"}}
    figure = measure_prose(tree, records)
    assert (records["broken.py"]["prose"], records["broken.py"]["prose_count"],
            records["broken.py"]["prose_percent"], figure) == (
        [], 0, 0.0, 33.3)


def test_a_file_no_decode_reads_joins_neither_side_of_the_figure():
    tree = build({"dirty.py": "def f():\n    return 1  # tail\n"})
    with open(os.path.join(tree, "muted.py"), "wb") as handle:
        handle.write(b"\xff\xfe = 1\n")
    records = {"dirty.py": {"path": "dirty.py", "layer": "api"},
               "muted.py": {"path": "muted.py", "layer": "api"}}
    figure = measure_prose(tree, records)
    assert (records["muted.py"]["prose"], records["muted.py"]["prose_count"],
            records["muted.py"]["prose_percent"], figure) == ([], 0, 0.0, 50.0)


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"PASS  {name}")
    print("all green")
