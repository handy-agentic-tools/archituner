import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
sys.path.insert(0, REPO)
from archituner.presentation.page.shell.events import SCRIPT

CONTRACT = os.path.join(REPO, 'ARCHITECTURE.md')
MIRRORED = os.path.join('archituner', 'presentation', 'page', 'shell',
                        'events.py')

BLOCK_COMMENT = re.compile(r'/[*].*?[*]/', re.S)
LINE_COMMENT = re.compile(r'[/]{2}.*')
WHITESPACE = re.compile(r'\s+')

SCRIPT_FLAT = (
         'document.addEventListener("click", e => { const t = e.target.closest("[data-'
         'view],[data-pair],[data-layer],[data-file],[data-hit]," + "[data-isolate],[d'
         'ata-reset],[data-findings],[data-region],[data-reading]," + "[data-figure],['
         'data-cmd]"); if (!t) return; if (t.dataset.cmd) { asking = !asking; draw(); '
         '$(asking ? "#search" : "#ask button").focus(); return; } if (t.dataset.readi'
         'ng) { reading = CHANGE ? t.dataset.reading : "state"; draw(); return; } if ('
         't.dataset.findings) { selection = {kind: "findings", id: "all"}; draw(); ret'
         'urn; } if (t.dataset.reset) { filters.state = new Set(STATES); filters.layer'
         ' = new Set(DATA.order); filters.outcome = new Set(MOVES); filters.coverage ='
         ' new Set(["mapped", "unmapped"]); filters.weight = 0; } else if (t.dataset.i'
         'solate) { const [axis, value] = t.dataset.isolate.split(":"); if (axis === "'
         'coverage") { const set = filters.coverage; if (set.size === 1 && set.has(val'
         'ue)) set.add("mapped").add("unmapped"); else { set.clear(); set.add(value); '
         '} draw(); } else isolate(axis, value); return; } else if (t.dataset.view) cu'
         'rrent = t.dataset.view; else if (t.dataset.pair) selection = {kind: "pair", '
         'id: t.dataset.pair}; else if (t.dataset.layer) selection = sel("layer", t.da'
         'taset.layer) ? null : {kind: "layer", id: t.dataset.layer}; else if (t.datas'
         'et.file) selection = {kind: "file", id: t.dataset.file}; else if (t.dataset.'
         'region) selection = {kind: "region", id: t.dataset.region}; else if (t.datas'
         'et.figure) selection = {kind: "figure", id: t.dataset.figure}; else if (t.da'
         'taset.hit) { const [kind, ...rest] = t.dataset.hit.split(":"); selection = {'
         'kind, id: rest.join(":")}; current = {pair: "matrix", layer: "layers"}[kind]'
         ' || current; } draw(); }); document.addEventListener("change", e => { const '
         't = e.target; if (t.dataset && t.dataset.axis) { const set = filters[t.datas'
         'et.axis]; t.checked ? set.add(t.value) : set.delete(t.value); } else if (t.i'
         'd === "layerpick") { filters.layer = new Set(Array.from(t.selectedOptions).m'
         'ap(o => o.value)); } else return; draw(); }); document.addEventListener("inp'
         'ut", e => { if (e.target.id === "minw") { filters.weight = +e.target.value |'
         '| 0; draw(); return; } if (e.target.id !== "search") return; query = e.targe'
         't.value; $("#results").innerHTML = hits(); }); document.addEventListener("ke'
         'ydown", e => { if (e.key !== "Escape") return; if (e.target && e.target.id ='
         '== "search" && e.target.value) { query = ""; e.target.value = ""; $("#result'
         's").innerHTML = ""; return; } selection = null; draw(); }); draw();')


def test_the_events_text_holds_byte_for_byte():
    flat = BLOCK_COMMENT.sub(' ', SCRIPT)
    flat = LINE_COMMENT.sub(' ', flat)
    assert WHITESPACE.sub(' ', flat).strip() == SCRIPT_FLAT, flat


def drive():
    return subprocess.run(
        [sys.executable, '-m', 'archituner', CONTRACT,
         '--check', '--file', MIRRORED],
        capture_output=True, text=True, cwd=REPO)


def test_the_events_module_sits_within_its_limits():
    one, two = drive(), drive()
    assert (one.returncode, one.stdout) == (two.returncode, two.stdout), \
        (one.returncode, two.returncode, one.stdout, one.stderr)
    assert one.returncode == 0, (one.returncode, one.stdout, one.stderr)
    assert one.stdout.splitlines() == ['no divergence'], one.stdout


HELD = r'sel\(([\'"])layer\1|=== *["\']layer["\']|["\']layer["\'] *==='
TOGGLE = re.compile(
    '(?:' + HELD + r').*(?P<clear>[=?] *null).*'
    r'\{kind: "layer", id: t\.dataset\.layer\}')
CLEAR = re.compile(r'[=?] *null')


def flatten():
    flat = BLOCK_COMMENT.sub(' ', SCRIPT)
    flat = LINE_COMMENT.sub(' ', flat)
    return WHITESPACE.sub(' ', flat).strip()


def chain(flat):
    return flat[flat.index('else if (t.dataset.pair'):
                flat.index('}); document.addEventListener("change"')]


def cut(text, head, tail):
    left = text.index(head) + len(head)
    return text[left:text.index(tail, left)]


def layer_branch(flat):
    return cut(chain(flat), 'else if (t.dataset.layer)',
               'else if (t.dataset.file)')


KEPT = (cut(chain(flatten()), 'else if (t.dataset.pair)',
            'else if (t.dataset.layer)')
        + ' ' + cut(chain(flatten()), 'else if (t.dataset.file)',
                    'else if (t.dataset.region)')
        + ' ' + cut(chain(flatten()), 'else if (t.dataset.hit)', 'draw();'))


def test_a_second_click_on_the_selected_layer_box_toggles_the_selection():
    whole = chain(flatten())
    found = TOGGLE.search(whole)
    assert found, (
        'a second click on the selected box must land on nothing selected '
        'and a click on another box must move the selection, but the layer '
        'branch never reads the selection it holds, never clears it, or no '
        'longer selects the box that is not held: '
        + layer_branch(flatten()))
    clear = found.start('clear')
    stop = whole.find('return', clear)
    drawn = whole.find('draw()', clear)
    assert stop < 0 or drawn < stop, (
        'the second click clears without a redraw and strands the outlines '
        'the selection left in the view')


def test_escape_and_the_second_click_are_two_spellings_of_one_behaviour():
    flat = flatten()
    key = flat[flat.index('addEventListener("keydown"'):]
    assert 'selection = null; draw();' in key, 'escape stopped clearing'
    assert CLEAR.search(layer_branch(flat)), (
        'the second click keeps what escape clears')


def test_the_caret_in_a_filled_search_field_keeps_escape_for_the_field():
    flat = flatten()
    key = flat[flat.index('addEventListener("keydown"'):]
    head = key[:key.index('selection = null')]
    ask = head.index('id === "search"')
    cond = head[head.rindex('if (', 0, ask):head.index('{', ask)]
    assert 'e.target.value' in cond, (
        'the carve-out fires on the field alone, so an empty field strands a '
        'reader whose caret sits in it: ' + cond)
    assert 'query = ""' in head, (
        'the carve-out stopped clearing the query')


def test_search_hits_and_pair_and_file_clicks_keep_their_selection():
    assert not CLEAR.search(KEPT), (
        'the toggle leaked into the selections the issue leaves unchanged: '
        + KEPT)


if __name__ == '__main__':
    for name, test in sorted(globals().items()):
        if name.startswith('test_'):
            test()
            print(f'PASS  {name}')
    print('all green')
