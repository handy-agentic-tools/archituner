import os

from archituner.theme import REFUSAL


REJECTED = """<!doctype html>
<meta charset="utf-8">
<title>archituner - contract rejected</title>
<style>
  :root {
    --scheme: __light-scheme__;
    --ink: __light-ink__;
    --surface: __light-surface__;
    --sunken: __light-sunken__;
    --accent: __light-accent__;
    --u: __light-u__;
    --mono: __light-mono__;
    --type-body: __light-type-body__;
    --face: __light-face__;
    --line: __light-line__;
    --pad: __light-pad__;
    --head: __light-head__;
    --code-pad: __light-code-pad__;
    color-scheme: var(--scheme);
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --scheme: __dark-scheme__;
      --ink: __dark-ink__;
      --surface: __dark-surface__;
      --sunken: __dark-sunken__;
      --accent: __dark-accent__;
      --u: __dark-u__;
      --mono: __dark-mono__;
      --type-body: __dark-type-body__;
      --face: __dark-face__;
      --line: __dark-line__;
      --pad: __dark-pad__;
      --head: __dark-head__;
      --code-pad: __dark-code-pad__;
    }
  }
  body { font: var(--type-body)/var(--line) var(--face); color: var(--ink);
    background: var(--surface); margin: 0; padding: var(--pad); }
  h1 { color: var(--accent); font-size: var(--head); }
  code { background: var(--sunken); padding: var(--code-pad); }
</style>
<h1>Contract rejected</h1>
<p>__REASON__</p>
<p>Nothing was measured, so no view can be drawn: a page of empty cells over a
contract the tool refused would read as a tree with no findings.</p>
<p>Contract: <code>__NAME__</code></p>
"""


def spent(page, ground, label):
    for name, value in ground.items():
        page = page.replace(f"__{label}-{name}__", value)
    return page


def render_rejection(contract_path, reason):
    name = os.path.basename(contract_path)
    page = (REJECTED
            .replace("__REASON__", reason.replace("<", "&lt;")
                     .replace(contract_path, name))
            .replace("__NAME__", name.replace("<", "&lt;")))
    return spent(spent(page, REFUSAL["light"], "light"),
                 REFUSAL["dark"], "dark")
