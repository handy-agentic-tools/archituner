import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
sys.path.insert(0, REPO)
from archituner.presentation.page.views.detail import SCRIPT

CONTRACT = os.path.join(REPO, 'ARCHITECTURE.md')
MIRRORED = os.path.join('archituner', 'presentation', 'page', 'views',
                        'detail.py')

BLOCK_COMMENT = re.compile(r'/[*].*?[*]/', re.S)
LINE_COMMENT = re.compile(r'[/]{2}.*')
WHITESPACE = re.compile(r'\s+')

RAW = (
    "findings <span class='count'>\" + DATA.findings.length",
    "invariants <span class='count'>\" + DATA.invariants.length",
    "\"<p><b>\" + p.state + \"</b> (\" + p.kind + \")</p>\"",
    "\"<p>\" + p.reason + \"</p>\"",
    "\"<li>\" + i.file + \"<br>",
    "\"<p><b>Responsibility.</b> \" + l.responsibility + \"</p>\"",
    "\"<p><b>Rationale.</b> \" + l.rationale + \"</p>\"",
    "\"<p>\" + l.files.length + \" file(s)</p>\"",
    "\"<p class='count'>\" + found.files.length + \" file(s)</p>",
    "\"<li data-file='\" + m + \"'>\" + m + \"</li>\"",
    "\"<p class='count'>\" + found.pairs.length + \" pair(s)</p>",
    "\"<li data-pair='\" + p.source + \"->\" + p.target + \"'>\""
    " + p.source + \" → \" + p.target + \" <span class='count'>\"",
    "\" <span class='count'>\" + p.state + \"</span></li>\"",
    "\"claimed by <b>\" + box.layer + \"</b>\"",
    "\"<p>\" + box.files + \" file(s)</p>\"",
    "\"<li>\" + i.module + \" <span class='count'>\"",
    "\"<li>\" + i + \"</li>\"",
    "\"<li data-file='\" + f.path + \"'><span class='p'>\" + f.path + \"</span>",
    "\"</span><span class='n'>\" + f.imports.length + \"</span><span class='n'>\"",
    "\" + f.importers.length + \"</span></li>\"",
    "n.innerHTML = p.source + \" → \" + p.target;",
    "n.innerHTML = l.name;",
    "n.innerHTML = (box.path || \".\") + (box.opened ? \"/\" : \"\");",
    "n.innerHTML = f.path;",
    "- it left \" + relocation(f.path).was + \" for \" + relocation(f.path).now",
    "layer: \" + (f.layer || \"<span class='unclaimed'>unclaimed</span>\")",
    "+ (i.layer || \"unclaimed\")",
    "? \"unclaimed\" : layer) + \"</span>",
)


def flat_of(text):
    return WHITESPACE.sub(' ', LINE_COMMENT.sub(' ', BLOCK_COMMENT.sub(
        ' ', text))).strip()


def test_the_panel_writes_no_value_into_its_markup_without_the_escape():
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


def test_the_detail_module_sits_within_its_limits():
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
