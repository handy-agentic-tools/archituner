import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
sys.path.insert(0, REPO)
from archituner.presentation.page.views.readings import SCRIPT

CONTRACT = os.path.join(REPO, 'ARCHITECTURE.md')
MIRRORED = os.path.join('archituner', 'presentation', 'page', 'views',
                        'readings.py')

BLOCK_COMMENT = re.compile(r'/[*].*?[*]/', re.S)
LINE_COMMENT = re.compile(r'[/]{2}.*')
WHITESPACE = re.compile(r'\s+')

RAW = (
    "data-reading='\" + r + \"'\"",
    "\">\" + r + \" reading\"",
    " <b>\" + CHANGE.dropped + \"</b>",
    "Write one with \" + command",
    "CHANGE.dropped_layers.join(\", \")",
    "<code>\" + (DATA.baseline || \"the contract's directory\")",
)


def flat_of(text):
    return WHITESPACE.sub(' ', LINE_COMMENT.sub(' ', BLOCK_COMMENT.sub(
        ' ', text))).strip()


def test_the_reading_row_writes_no_value_into_its_markup_without_the_escape():
    flat = flat_of(SCRIPT)
    left = list(filter(lambda one: one in flat, RAW))
    assert not left, ("a value is concatenated into the markup raw, and a "
                      "name holding an apostrophe truncates the attribute "
                      "it is written into: " + " | ".join(left))


def drive():
    return subprocess.run(
        [sys.executable, '-m', 'archituner', CONTRACT,
         '--check', '--file', MIRRORED],
        capture_output=True, text=True, cwd=REPO)


def test_the_readings_module_sits_within_its_limits():
    one, two = drive(), drive()
    assert (one.returncode, one.stdout) == (two.returncode, two.stdout), \
        (one.returncode, two.returncode, one.stdout, one.stderr)
    assert one.returncode == 0, (one.returncode, one.stdout, one.stderr)
    assert one.stdout.splitlines() == ['no divergence'], one.stdout


def test_the_nav_names_no_shape_view():
    flat = BLOCK_COMMENT.sub(' ', SCRIPT)
    flat = LINE_COMMENT.sub(' ', flat)
    assert '"shape"' not in WHITESPACE.sub(' ', flat).strip(), (
        'the nav still offers the shape view')


def test_the_nav_names_no_files_view():
    flat = BLOCK_COMMENT.sub(' ', SCRIPT)
    flat = LINE_COMMENT.sub(' ', flat)
    assert '"files"' not in WHITESPACE.sub(' ', flat).strip(), (
        'the nav still offers the files view')

def test_the_nav_names_no_surface_view():
    flat = BLOCK_COMMENT.sub(' ', SCRIPT)
    flat = LINE_COMMENT.sub(' ', flat)
    assert '"surface"' not in WHITESPACE.sub(' ', flat).strip(), (
        'the nav still offers the surface view')


if __name__ == '__main__':
    for name, test in sorted(globals().items()):
        if name.startswith('test_'):
            test()
            print(f'PASS  {name}')
    print('all green')
