import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
sys.path.insert(0, REPO)
from archituner.presentation.page.shell.shell import BODY
from archituner.presentation.page.shell.shell import CLOSE
from archituner.presentation.page.shell.shell import HEAD

CONTRACT = os.path.join(REPO, 'ARCHITECTURE.md')
MIRRORED = os.path.join('archituner', 'presentation', 'page', 'shell',
                        'shell.py')

BLOCK_COMMENT = re.compile(r'/[*].*?[*]/', re.S)
LINE_COMMENT = re.compile(r'[/]{2}.*')
WHITESPACE = re.compile(r'\s+')

HEAD_BYTES = (
         '<!doctype html>\n'
         '<meta charset="utf-8">\n'
         '<title>archituner</title>\n'
         '<style>\n'
         )
BODY_BYTES = (
         '</style>\n<div id="main">\n  <nav id="nav"></nav>\n  <div id="tree'
         '"></div>\n  <div id="verdict"></div>\n  <div id="shellbar"><span i'
         'd="reading"></span><span id="legend"></span></div>\n  <div id="pro'
         'venance"></div>\n  <div id="ask"></div>\n  <div class="hint"></div'
         '>\n  <div id="cmd"></div>\n  <div id="view"></div>\n</div>\n<div i'
         'd="detail"><div id="panel-head"><h2 id="panel-name">Whole project<'
         '/h2><button data-close=\'1\' aria-label=\'close the panel\'>✕</but'
         'ton></div><div id="panel-tabs" role="tablist"></div><div id="panel'
         '-body"></div></div>\n<script>\n'
         )

CLOSE_BYTES = (
         '</script>\n'
         )


def test_the_shell_markup_holds_byte_for_byte():
    assert (HEAD, BODY, CLOSE) == (
        HEAD_BYTES,
        BODY_BYTES,
        CLOSE_BYTES,
    ), "the shell markup moved: the hint line is the phone's, and the panel" \
       " heading carries the sheet's cross"


PLACES = ('<div id="shellbar">', '<div id="provenance">', '<div id="ask">',
          '<div id="cmd">', '<div id="view">')


def test_the_command_bar_sits_above_the_view():
    where = [BODY.find(mark) for mark in PLACES]
    assert where == sorted(where), list(zip(PLACES, where))


def test_the_hint_line_sits_first_under_the_search_and_filters_row():
    marks = ('<div id="ask">', '<div class="hint">', '<div id="cmd">',
             '<div id="view">')
    where = [BODY.find(mark) for mark in marks]
    assert -1 not in where, list(zip(marks, where))
    assert where == sorted(where), list(zip(marks, where))


def test_the_panel_s_tab_strip_sits_between_the_heading_and_the_card():
    marks = ('id="panel-name"', 'role="tablist"', 'id="panel-body"')
    where = [BODY.find(mark) for mark in marks]
    assert -1 not in where, list(zip(marks, where))
    assert where == sorted(where), list(zip(marks, where))


def drive():
    return subprocess.run(
        [sys.executable, '-m', 'archituner', CONTRACT,
         '--check', '--file', MIRRORED],
        capture_output=True, text=True, cwd=REPO)


def test_the_shell_module_sits_within_its_limits():
    one, two = drive(), drive()
    assert (one.returncode, one.stdout) == (two.returncode, two.stdout), \
        (one.returncode, two.returncode, one.stdout, one.stderr)
    assert one.returncode == 0, (one.returncode, one.stdout, one.stderr)
    assert one.stdout.splitlines() == ['no divergence'], one.stdout


if __name__ == '__main__':
    for name, test in sorted(globals().items()):
        if name.startswith('test_'):
            test()
            print(f'PASS  {name}')
    print('all green')
