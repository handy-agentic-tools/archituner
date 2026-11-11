import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
sys.path.insert(0, REPO)
from archituner.presentation.page.views.axes import SCRIPT

CONTRACT = os.path.join(REPO, 'ARCHITECTURE.md')
MIRRORED = os.path.join('archituner', 'presentation', 'page', 'views',
                        'axes.py')

BLOCK_COMMENT = re.compile(r'/[*].*?[*]/', re.S)
LINE_COMMENT = re.compile(r'[/]{2}.*')
WHITESPACE = re.compile(r'\s+')

HIT_BUTTON = re.compile(r"<button class='[^']*' data-hit=")

RAW = (
    "data-isolate='outcome:\" + o",
    "title='show only \" + o",
    "not compared'>\" + MOVED.dropped",
    "class='count'>\" + CHANGE.dropped + \"</span></button>\"",
    "data-isolate='state:\" + s",
    "title='show only \" + s",
    "findings <span class='count'>\" + DATA.findings.length",
    "\" + held + \" pair(s) hidden",
    "data-hit='\" + h.kind + \":\" + h.id + \"'>[\"",
    "\" + shut + \" hidden</span>",
    "\" + hidden[axis] + \" \" + what + \" hidden",
    "\"<option value='\" + l + \"'\"",
    "\">\" + l + \"</option>\"",
    "data-axis='coverage' value='\" + c + \"'\"",
    "\">\" + c + \"</label>\"",
    "min='0' value='\" + filters.weight + \"'>\"",
)


def flat_of(text):
    return WHITESPACE.sub(' ', LINE_COMMENT.sub(' ', BLOCK_COMMENT.sub(
        ' ', text))).strip()


def test_the_search_results_carry_a_class_the_sheet_can_dress():
    flat = LINE_COMMENT.sub(' ', BLOCK_COMMENT.sub(' ', SCRIPT))
    assert HIT_BUTTON.search(flat), 'the search results build bare buttons'


def test_the_axes_write_no_value_into_their_markup_without_the_escape():
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


def hits_source():
    found = re.search(r'function hits\(\) \{.*?\n\}', SCRIPT, re.S)
    assert found, 'the hits function is gone'
    return found.group()


def hits_markup(entries, query):
    run = subprocess.run(
        ['node', '-e', 'const esc = t => String(t);'
         'let query = ' + json.dumps(query) + ';'
         'const INDEX = ' + json.dumps(entries) + ';'
         + hits_source() + ';process.stdout.write(hits());'],
        capture_output=True, text=True)
    run.check_returncode()
    return run.stdout


def index_of(names):
    return [{'kind': 'layer', 'id': name, 'text': name.lower()}
            for name in names]


def test_a_query_beyond_the_cap_says_how_many_it_shows_of_how_many():
    markup = hits_markup(index_of(['x0%d' % n for n in range(10)]), 'x')
    assert markup.count('data-hit=') == 8, markup
    assert '8 of 10' in re.sub(r'<[^>]*>', ' ', markup), markup


def test_a_query_at_the_cap_names_no_count():
    markup = hits_markup(index_of(['x0%d' % n for n in range(8)]), 'x')
    assert not re.search(r'\d+ of \d+', re.sub(r'<[^>]*>', ' ', markup)), \
        markup


def test_the_axes_module_sits_within_its_limits():
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
