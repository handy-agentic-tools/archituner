import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
sys.path.insert(0, REPO)
from archituner.presentation.page.views.rules import RULES

CONTRACT = os.path.join(REPO, 'ARCHITECTURE.md')
MIRRORED = os.path.join('archituner', 'presentation', 'page', 'views',
                        'rules.py')

BLOCK_COMMENT = re.compile(r'/[*].*?[*]/', re.S)
LINE_COMMENT = re.compile(r'[/]{2}.*')
WHITESPACE = re.compile(r'\s+')
RULE = re.compile(r'([^{}]+)\{([^{}]*)\}')

RULES_FLAT = (
         ':root { color-scheme: light dark; } body { font: var(--type-body)/var(--line) var(--mono); margin: 0; display: flex; flex-wrap: wrap; height: 100vh;'
         ' color: var(--ink); background: var(--surface); } #main { flex: 1 1 var(--main-w); min-width: 0; overflow: auto; padding: var(--step-4); } #detail {'
         ' flex: 0 0 var(--panel-w); max-width: 100%; overflow: auto; border-left: var(--step-1) solid var(--rule); padding: var(--step-4); } __PANEL_STYLE__ '
         '#cmd { height: 0; overflow: hidden; } #cmd[data-open] { height: auto; overflow: auto; display: flex; flex-wrap: wrap; align-items: center; gap: var('
         '--step-3); padding: var(--step-3) 0; } #ask { margin-top: var(--step-3); } button { font: inherit; cursor: pointer; } nav button { margin-right: var'
         '(--step-2); cursor: pointer; } nav button.active { font-weight: bold; text-decoration: underline; } nav button:hover { text-decoration: underline; }'
         ' #panel-tabs button { font: inherit; cursor: pointer; color: var(--ink-muted); background: var(--surface-sunken); border: var(--hair) solid var(--ru'
         'le); } #panel-tabs button.on { color: var(--ink); background: var(--surface); border: var(--hair) solid var(--rule-strong); font-weight: bold; } #de'
         'tail .head .label.unc { color: var(--unclaimed); } #tree { color: var(--ink-muted); margin: var(--step-3) 0 var(--step-2); } h1 { font-size: var(--t'
         'ype-body); letter-spacing: var(--track-wide); text-transform: uppercase; margin: 0 0 var(--step-3); } h2 { font-size: var(--type-body); letter-spaci'
         'ng: var(--track-wide); text-transform: uppercase; color: var(--ink-muted); font-weight: bold; margin: var(--step-4) 0 var(--step-2); } #verdict.bad '
         '{ color: var(--verdict-bad); } #verdict.good { color: var(--verdict-good); } table { border-collapse: collapse; } #matrix td, #matrix th { border: v'
         'ar(--hair) solid var(--rule); width: var(--cell); height: var(--cell-h); text-align: center; font-size: var(--type-small); cursor: pointer; } #matri'
         'x th { width: auto; padding: 0 var(--step-2); font-weight: normal; } td.convergence { background: var(--state-convergence); } td.divergence { backgr'
         'ound: var(--state-divergence); } td.absence { background: var(--state-absence); } td.silence { background: var(--state-silence); color: var(--ink-mu'
         'ted); } td.improved { background: var(--change-improved); } td.unchanged { background: var(--change-unchanged); color: var(--ink-muted); } td.regres'
         'sed { background: var(--change-regressed); } td.dropped { background: var(--surface-sunken); color: var(--ink-muted); } td.diagonal { background: va'
         'r(--ink-muted); } td.sel { outline: var(--step-1) solid var(--selected); } .layerbox { border: var(--hair) solid var(--rule-strong); padding: var(--'
         'step-2) var(--step-3); margin: var(--step-2) 0; cursor: pointer; } .layerbox.sel { outline: var(--step-1) solid var(--selected); } #matrix td:hover,'
         ' .layerbox:hover { border-color: var(--rule-strong); } __COVERAGE_STYLE__ .unclaimed { color: var(--unclaimed); font-weight: bold; } #search { width'
         ': var(--search-w); } #minw { width: var(--number-w); } #search, #minw, #layerpick { font: inherit; color: var(--ink); background: var(--surface); bo'
         "rder: var(--hair) solid var(--rule-strong); } input[type='checkbox'] { accent-color: var(--selected); } button.key, button.hit, #reading button, #as"
         'k button { font: inherit; cursor: pointer; color: var(--ink); border: var(--hair) solid var(--rule-strong); background: var(--surface); padding: var'
         '(--hair) var(--step-3); } button.key, button.hit { margin-right: var(--step-2); } .hidden { display: none; } .count { color: var(--ink); font-size: '
         'var(--type-small); } p.count, td.count, li .count, h2 .count { color: var(--ink-muted); } .hiddencount { color: var(--unclaimed); font-size: var(--t'
         'ype-small); } button.key.convergence { background: var(--state-convergence); } button.key.divergence { background: var(--state-divergence); } button'
         '.key.absence { background: var(--state-absence); } button.key.silence { background: var(--state-silence); } button.key.improved { background: var(--'
         'change-improved); } button.key.unchanged { background: var(--change-unchanged); } button.key.regressed { background: var(--change-regressed); } butt'
         'on.key.dropped { background: var(--surface-sunken); color: var(--ink-muted); } button.key.unclaimedkey { color: var(--unclaimed); font-weight: bold;'
         ' } button.key.off { opacity: var(--fade-off); } #shellbar { display: flex; flex-wrap: wrap; align-items: center; gap: var(--step-3); } button.key:ho'
         'ver, button.hit:hover, #reading button:hover, #ask button:hover, #panel-tabs button:hover, button.tally:hover { background: var(--surface-raised); }'
         ' #reading button.on, #ask button.on { font-weight: bold; text-decoration: underline; } #reading button[aria-disabled] { color: var(--ink-muted); bac'
         'kground: var(--surface-sunken); cursor: not-allowed; } #provenance { color: var(--ink-muted); font-size: var(--type-small); margin: var(--step-2) 0;'
         ' } #provenance code { background: var(--surface-sunken); padding: 0 var(--step-1); } .axis { margin: var(--step-1) 0; } __LAYERS_STYLE__ .empty { bo'
         'rder: var(--hair) solid var(--unclaimed); padding: var(--step-3); } button[data-reset] { cursor: pointer; } button[data-reset]:hover { background: v'
         'ar(--surface-raised); } .tallies { margin: var(--step-2) 0; } button.tally { font: inherit; font-size: var(--type-small); background: none; border: '
         'var(--hair) solid var(--rule); cursor: pointer; margin-right: var(--step-2); padding: var(--hair) var(--step-3); color: var(--ink); } button:focus-v'
         'isible, input:focus-visible, select:focus-visible { outline: var(--focus-ring) solid var(--selected); outline-offset: var(--focus-gap); }'
        )


def test_the_rules_text_holds_byte_for_byte():
    flat = BLOCK_COMMENT.sub(' ', RULES)
    flat = LINE_COMMENT.sub(' ', flat)
    assert WHITESPACE.sub(' ', flat).strip() == RULES_FLAT, flat


def spent_at(sheet):
    return {' '.join(selector.split()): [' '.join(one.split())
                                         for one in body.split(';')]
            for selector, body in RULE.findall(sheet)}


def spend_problem(rules, selector, prop, token):
    held = rules.get(selector)
    if held is None:
        return f'no rule names {selector}'
    if f'{prop}: var({token})' not in held:
        return (f"{selector} holds {'; '.join(filter(None, held))}; "
                f'{prop} spends no var({token})')


RULES_SPENT = spent_at(LINE_COMMENT.sub(' ', BLOCK_COMMENT.sub(' ', RULES)))

SPENT = (
    ('button.key.off', 'opacity', '--fade-off'),
    ('#search, #minw, #layerpick', 'color', '--ink'),
    ('#search, #minw, #layerpick', 'background', '--surface'),
    ('button.key, button.hit, #reading button, #ask button',
     'color', '--ink'),
    ('button.key, button.hit, #reading button, #ask button',
     'background', '--surface'),
    ("input[type='checkbox']", 'accent-color', '--selected'),
    ('#panel-tabs button', 'color', '--ink-muted'),
    ('#panel-tabs button', 'background', '--surface-sunken'),
    ('#panel-tabs button.on', 'color', '--ink'),
    ('#panel-tabs button.on', 'background', '--surface'),
    ('#detail .head .label.unc', 'color', '--unclaimed'),
)


def test_the_rules_spend_the_tokens_by_name():
    problems = list(filter(None,
                           map(lambda row: spend_problem(RULES_SPENT, *row),
                               SPENT)))
    assert not problems, (
        'the rules do not spend the tokens by name: ' + '; '.join(problems))
    assert 'font-weight: bold' in \
        RULES_SPENT.get('#panel-tabs button.on', ''), \
        RULES_SPENT.get('#panel-tabs button.on', '')


def drive():
    return subprocess.run(
        [sys.executable, '-m', 'archituner', CONTRACT,
         '--check', '--file', MIRRORED],
        capture_output=True, text=True, cwd=REPO)


def test_the_rules_module_sits_within_its_limits():
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
