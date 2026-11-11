import os
import re
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
sys.path.insert(0, REPO)
from archituner.presentation.page.views.grounds import GROUND

CONTRACT = os.path.join(REPO, 'ARCHITECTURE.md')
MIRRORED = os.path.join('archituner', 'presentation', 'page', 'views',
                        'grounds.py')

BLOCK_COMMENT = re.compile(r'/[*].*?[*]/', re.S)
LINE_COMMENT = re.compile(r'[/]{2}.*')
WHITESPACE = re.compile(r'\s+')

GROUND_FLAT = (
         ':root { --ink: __light-ink__; --ink-muted: __light-ink-muted__; --su'
         'rface: __light-surface__; --surface-sunken: __light-surface-sunken__'
         '; --rule: __light-rule__; --rule-strong: __light-rule-strong__; --st'
         'ate-convergence: __light-state-convergence__; --state-divergence: __'
         'light-state-divergence__; --state-absence: __light-state-absence__; '
         '--state-silence: __light-state-silence__; --change-improved: __light'
         '-change-improved__; --change-unchanged: __light-change-unchanged__; '
         '--change-regressed: __light-change-regressed__; --unclaimed: __light'
         '-unclaimed__; --selected: __light-selected__; --verdict-bad: __light'
         '-verdict-bad__; --verdict-good: __light-verdict-good__; --u: __light'
         '-u__; --step-1: __light-step-1__; --step-2: __light-step-2__; --step'
         '-3: __light-step-3__; --step-4: __light-step-4__; --hair: __light-ha'
         'ir__; --type-micro: __light-type-micro__; --type-dense: __light-type'
         '-dense__; --cell-h: __light-cell-h__; --main-w: __light-main-w__; --'
         'panel-w: __light-panel-w__; --search-w: __light-search-w__; --number'
         '-w: __light-number-w__; --type-small: __light-type-small__; --type-b'
         'ody: __light-type-body__; --cell: __light-cell__; --mono: __light-mo'
         'no__; --line: __light-line__; --track-wide: __light-track-wide__; --'
         'stroke-hair: __light-stroke-hair__; --stroke-mark: __light-stroke-ma'
         'rk__; --stroke-node: __light-stroke-node__; --stroke-emphasis: __lig'
         'ht-stroke-emphasis__; --stroke-selection: __light-stroke-selection__'
         '; --dash-vacant: __light-dash-vacant__; --dash-absence: __light-dash'
         '-absence__; --dash-dropped: __light-dash-dropped__; --radius-s: __li'
         'ght-radius-s__; --radius-m: __light-radius-m__; --focus-ring: __ligh'
         't-focus-ring__; --focus-gap: __light-focus-gap__; --surface-raised: '
         '__light-surface-raised__; --fade-aside: __light-fade-aside__; --fade'
         '-off: __light-fade-off__; }'
         )


def test_the_light_ground_holds_byte_for_byte():
    flat = BLOCK_COMMENT.sub(' ', GROUND)
    flat = LINE_COMMENT.sub(' ', flat)
    light = flat.partition('@media')[0]
    assert WHITESPACE.sub(' ', light).strip() == GROUND_FLAT, flat


def drive():
    return subprocess.run(
        [sys.executable, '-m', 'archituner', CONTRACT,
         '--check', '--file', MIRRORED],
        capture_output=True, text=True, cwd=REPO)


def test_the_grounds_module_sits_within_its_limits():
    one, two = drive(), drive()
    assert (one.returncode, one.stdout) == (two.returncode, two.stdout), \
        (one.returncode, two.returncode, one.stdout, one.stderr)
    assert one.returncode == 0, (one.returncode, one.stdout, one.stderr)
    assert one.stdout.splitlines() == ['no divergence'], one.stdout


TAB = re.compile(r'(#panel-tabs[^{}]*)\{([^{}]*)\}')
VAR = re.compile(r'var\((--[a-z-]+)\)')
TOKEN = re.compile(r'(--[a-z-]+):')


def sheet_of(page):
    return page.partition('<style>')[2].partition('</style>')[0]


def tab_spends(sheet):
    spent = set()
    for selector, body in TAB.findall(sheet):
        spent.update(VAR.findall(body))
    return spent


def declared():
    return set(TOKEN.findall(GROUND.partition('@media')[0]))


def page_of():
    with tempfile.TemporaryDirectory() as home:
        path = os.path.join(home, 'page.html')
        done = subprocess.run([sys.executable, '-m', 'archituner', CONTRACT,
                               '-o', path], capture_output=True, text=True,
                              cwd=REPO, timeout=120)
        assert done.returncode == 0, (done.returncode, done.stderr)
        with open(path, encoding='utf-8') as handle:
            return handle.read()


def test_the_panel_s_tab_dress_spends_tokens_the_grounds_declare():
    spent = tab_spends(sheet_of(page_of()))
    assert spent, "the page's sheet carries no #panel-tabs dress"
    light = declared()
    for token in sorted(spent):
        assert token in light, token


if __name__ == '__main__':
    for name, test in sorted(globals().items()):
        if name.startswith('test_'):
            test()
            print(f'PASS  {name}')
    print('all green')
