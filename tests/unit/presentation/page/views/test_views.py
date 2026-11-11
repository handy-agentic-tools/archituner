import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
sys.path.insert(0, REPO)
from archituner.presentation.page.views.views import SCRIPT

CONTRACT = os.path.join(REPO, 'ARCHITECTURE.md')
MIRRORED = 'archituner/presentation/page/views/views.py'

BLOCK_COMMENT = re.compile(r'/[*].*?[*]/', re.S)
LINE_COMMENT = re.compile(r'[/]{2}.*')
WHITESPACE = re.compile(r'\s+')

RAW = (
    "\"<th>\" + t + \"</th>\"",
    "\"<tr><th>\" + s + \"</th>\"",
    "data-pair='\" + s + \"->\" + t",
    "title='\" + s + \" → \" + t + \": \" + mark",
    "'>\" + glyph + \"</td>",
    "data-view='\" + v + \"'>\" + v + \"</button>",
    "lead from \" + from + \" to it",
    "chain from \" + from + \" reaches it",
)


def flat_of(text):
    return WHITESPACE.sub(' ', LINE_COMMENT.sub(' ', BLOCK_COMMENT.sub(
        ' ', text))).strip()


def drive():
    return subprocess.run(
        [sys.executable, '-m', 'archituner', CONTRACT,
         '--check', '--file', MIRRORED],
        capture_output=True, text=True, cwd=REPO)


def test_the_views_module_sits_within_its_limits():
    one, two = drive(), drive()
    assert (one.returncode, one.stdout) == (two.returncode, two.stdout), \
        (one.returncode, two.returncode, one.stdout, one.stderr)
    assert one.returncode == 0, (one.returncode, one.stdout, one.stderr)
    assert one.stdout.splitlines() == ['no divergence'], one.stdout


def test_the_views_write_no_value_into_their_markup_without_the_escape():
    flat = flat_of(SCRIPT)
    left = list(filter(lambda one: one in flat, RAW))
    assert not left, ("a value is concatenated into the markup raw, and a "
                      "name holding an apostrophe truncates the attribute "
                      "it is written into: " + " | ".join(left))


def test_a_pair_the_payload_omits_is_drawn_as_the_empty_cell():
    body = re.search(r'function drawMatrix\(\).*?return h; \}',
                     flat_of(SCRIPT)).group(0)
    gap = re.search(r'pairAt\[s \+ "->" \+ t\]; (.*?)const mark = changing',
                    body)
    assert gap, 'the matrix never looks the pair up: ' + body[:160]
    assert gap.group(1).strip() == 'if (!p) { h += "<td></td>"; return; }', (
        'the pair the payload omits is read, not drawn as an empty cell',
        gap.group(1))


def test_the_views_open_no_view_with_a_sentence():
    flat = flat_of(SCRIPT)
    assert 'const SENTENCE' not in flat, (
        'the views still build a sentence to open with: ' + flat[-200:])
    assert '$("#sentence")' not in flat, (
        'the script still writes into the sentence line')


def test_the_shape_view_is_gone_from_the_script():
    flat = flat_of(SCRIPT)
    assert 'function drawShape' not in flat, 'the shape view still draws'


if __name__ == '__main__':
    for name, test in sorted(globals().items()):
        if name.startswith('test_'):
            test()
            print(f'PASS  {name}')
    print('all green')
