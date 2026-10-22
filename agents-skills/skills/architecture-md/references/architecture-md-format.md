# The ARCHITECTURE.md format

Contents: **§1** the machine block · **§2** the body and its coverage questions · **§3** how a consumer grades a defect · **§4** what a statement must be to belong in the file · **§5** worked skeleton

**Read §1 and §2 as two halves of one encoding: the block, and the prose it cannot express.**

An ARCHITECTURE.md prescribes the ideal target shape and never documents the tree - §4 states that rule and what it costs, and every rule below serves it.

**Give the file both halves: YAML front matter (the machine block), then a body starting at `## Layers`.**

## 1. Front matter - the machine block

### What the block must contain, and where it comes from

Between `---` fences at the very top. §5 carries the complete block; the fragment here shows only the shape of the keys it carries.

```yaml
---
layers:
  web:        ["app/controllers/**"]
  web.api:    ["app/controllers/api/**"]
  web.pages:  ["app/controllers/pages/**"]
  domain:     ["app/models/**"]
dependencies:
  allow:
    - web -> domain
    - web.api -> web.pages
  forbid:
    - domain -> web
    - web.pages -> web.api
ignore:
  - "app/controllers/generated/**"
limits:
  size: 8000
  defs: 8
  overrides:
    - "size `web`: 12000 - the transport's controllers are wide but shallow"
naming:
  - "*.interface.* must not import *.impl.*"
---
```

| Key | Required | What it holds |
|---|---|---|
| `layers` | yes | a map of `layer_name: [path globs]`, relative to the contract's own directory - a contract governs the tree it sits in. A name carries one dot per level below the top (`presentation.page`), a file is assigned to the deepest name whose globs match it, and globs must not overlap across two names neither of which is an ancestor of the other - the sublayer section below carries what a dot then owes |
| `dependencies` | yes | two lists of `A -> B` edges between sibling names, total between them per sibling set: every ordered pair of siblings in exactly one list. `archituner` reads both as the contract - a realised `allow` is a convergence and a realised `forbid` a divergence - and refuses a pair set that is not total |
| `naming` | no | free-text rules that are not pure dependency edges: suffix conventions, interface/impl separation. Reviewer-judged unless a rule happens to be expressible as a path or import constraint |
| `ignore` | no | a list of globs naming walked files no rule reaches, written as an inline list or one `- ` item per line. The walk drops each match before claiming, so an ignored file is neither claimed nor unclaimed, carries no measure, and no import resolves to it - its own imports included (`archituner/source/claim.py:66`). A glob matching nothing is a finding, and one taking a file a layer's glob would claim is stated as a finding that says the ignore wins (`archituner/source/findings.py:29`) |
| `limits` | no | measured numbers for the block to enforce, each as `number: count`, with `overrides` narrowing a number to the files a selector reaches - the limits section below carries the six numbers, the override's one shape and every refusal the key earns |
| `package_root` | no | a scalar naming the directory the tree's imports resolve from, taking precedence over the inferred common prefix - that directory is on `sys.path`, so its children are top-level and the inferred prefix names nothing. Declared for the one tree no inference recovers - a plugin bundle whose files live under `Plugin.bundle/Contents/Resources/` and whose imports resolve from `Resources` - and never as a general escape hatch (`archituner/source/__init__.py:116`, `import_root`) |

**Treat the schema as closed: `layers`, `dependencies`, `naming`, `package_root`, `ignore` and `limits` are every key the block reads.** Another key is not a rule; what is worse than inert sits in the table below and §3's unknown-key row. A fact that fits no key belongs in `## Invariants`, labelled in `## Enforcement` as reviewer work.

**Keep the pair set total: a sibling set of N layers gives N(N-1) ordered pairs, and each belongs in one list.** An unlisted pair is not "undecided" - it is permitted, by every tool and by every reader who assumed the block was a contract.

**Name only declared layers on an edge.** An edge naming a layer `layers` does not carry makes `archituner` refuse the block outright - ``rejected: edge names an unknown layer`` - so nothing is counted, enforced or audited until the line is fixed.

**Name two different layers on every edge.** The table below has what a self-pair costs, and the pair arithmetic above cannot catch one because N(N-1) excludes self-pairs.

**Never write `A -> *` in the `forbid` list.** A wildcard in the machine half has no expansion any two consumers agree on: `archituner` reads the target as a layer name, finds no such layer, and refuses the block - ``rejected: edge names an unknown layer: A -> *`` - so nothing downstream decides anything until it is gone.

**Never write `A -> *` in the `allow` list either.** The same refusal meets it: the target names no declared layer, so the line stops the run rather than reading as a decision that decides nothing.

**Derive the block from the project's own boundary tool where one exists, so the two cannot disagree.**

### How a dotted name names a sublayer, and what the block then owes

**Write a sublayer as one more flat key beside its parent - `presentation.page` beside `presentation` - never as a nested block.** The name is the hierarchy: one spelling serves every level, and nothing about a layer's shape changes on its first child (`archituner/contract/names.py:4`).

A segment is an identifier - letters, digits and underscore - with no depth limit, and a block with no dot at all is a valid one-level hierarchy.

**Declare every ancestor of a dotted name as a layer in its own right.** A skipped level refuses the block outright - ``rejected: a dotted name's parent is not declared: web.page names web`` - so nothing is counted until the ancestor arrives (`archituner/contract/names.py:14`).

**Let a child claim only files its parent also claims.** A file a child's glob matches and no glob of the parent's is a finding the run states at exit 0 - ``<path> is claimed by web.page's <glob> but no glob of its parent web claims it`` (`archituner/source/findings.py:47`).

**Leave a parent that has children no file of its own.** The deepest matching name claims each file (`archituner/source/claim.py:18`), and a file only the parent's glob matches is a finding: ``<path> is claimed by web's <glob> and no child claims it`` (`archituner/source/findings.py:49`).

**Set totality against each sibling set: the names sharing one parent, undotted names forming the top one.** A set of one owes no pair; the refusal sums the sets - ``rejected: pair set is not total, N of M missing, first: <pair>`` (`archituner/contract/pairs.py:42`).

**Write an edge between siblings only.** An edge between names of two different parents refuses the block - ``rejected: edge is not between siblings: <edge>`` (`archituner/contract/pairs.py:16`) - and the same pair on a `## Boundaries` line is a finding: ``Boundaries line names a non-sibling pair`` (`archituner/contract/edges.py:29`).

**Let the parents' edge judge traffic between their descendants.** An import is counted against the pair of claiming names lifted to the level the two diverge - `web.page` into `other` reads under `web -> other`, `web.page` into `web.report` under the child pair (`archituner/source/reading.py:45`).

**Narrow downward only: a child decides its own sibling set and lifts nothing above it.** The edge that would state a child's crossing of its parent's decision is the refused non-sibling one, so a parent's `forbid` - and its `allow` - reaches every descendant file.

**Use the full dotted name everywhere a layer is named: `## Layers` rows, `## Boundaries` lines, an `overrides` selector, `--layer`.** The bare segment names no layer the tool reads, so a rule written on it governs nothing.

### What the `limits` block measures, and how an override narrows a default

**Give every number the contract wants enforced a default, as `number: count` lines under `limits:`.** No number carries a default of the tool's own: an absent one is measured nowhere, and no count names the silence.

| Number | What one file's count is |
|---|---|
| `size` | its decoded characters |
| `defs` | every `def`, `async def` and `class` in it, nested ones included |
| `depth` | its deepest nesting of function, class and flow-break bodies; a bare module statement sits at 0 |
| `cyclomatic` | 1, plus one per `if`/`elif`, loop, `except` handler, ternary, `assert`, match case, comprehension clause and boolean operand past the first |
| `cognitive` | the same constructs, each scoring 1 plus its nesting, with `else`, `break` and `continue` scoring too |
| `prose_count` | its comment and docstring entries - `#` comments past the shebang and a leading `# covers:` line, plus every module, class and function docstring |

**Treat the six numbers as the closed set, each default a plain count of digits.** A seventh name under `limits:` refuses the block - ``rejected: a limits key names a number no file record carries: <number>`` - and a non-digit default is refused the same way (`archituner/contract/limits.py:10`).

**Read a default as binding every file the walk reads and the `ignore` list does not remove, a file no layer claims included.** `prose_count` is the one exception: it is measured on claimed files alone, so an unclaimed file's comments breach nothing (`archituner/source/limits.py:44`).

**Write each override in its one shape - ``number `selector`: value - reason`` - as one `- ` item under `overrides:`.** An entry in any other shape refuses the block: ``rejected: a limits override is not its one shape - number, selector, value, reason: <entry>`` (`archituner/contract/syntax.py:15`).

| Part | What it is |
|---|---|
| number | one of the six above, whose default the block declares: an override naming a number with no default is refused - ``rejected: an override names a number whose default is absent: <number>`` |
| selector | a declared layer name in backticks - a dotted name in full - or any path glob; the files it reaches take the override's value in place of the default |
| value | a plain count, or `none`: `none` removes the number for the files reached, so no limit, no share and no breach reach them |
| reason | free text after ` - `, handed to the reader of a breach |

The `- ` form carries an entry whole; the inline `overrides: [...]` form splits at a comma, and a reason holding one fails the entry's shape with the refusal naming the fragment after the comma.

**Let the first override declared govern a file two of them reach.** The overrides are walked in declaration order and the first match wins, so a wide selector declared early shadows a narrow one declared late (`archituner/source/limits.py:27`).

**Expect a finding from a selector that reaches no file.** The run states ``limits selector reaches no file: <selector>`` at exit 0, so a stale selector is reported rather than silently ungoverning (`archituner/source/limits.py:14`).

### Where a glob may point, and the shape it is written in

**Give each directory one layer.** A directory holding two layers leaves the boundary invisible in the tree, and a consumer assigning one layer per path cannot see the second layer at all.

**Let a layer's globs span several directories.** The constraint above runs one way only.

**Point every glob at a directory, never at a literal file.** A literal file makes the layer exactly one path wide while its `Paths` cell names a home; resolution reaches it like any other claimed file, and the table below has what such a glob still costs.

A home no import in this language can name is legal, so long as `## Enforcement` says so.

**Point no glob at a home that resolves through a symlink.** The walk follows no symlinked directory - `archituner` runs `os.walk` with its defaults - so the home reads as legal, matches its own glob, and yields nothing the run can report.

**State an entry point nothing imports as the one exception to the directory rule above.**

**Write every glob in the `dir/**` shape, with that entry point as the only exception.** A prefix means something only where it lands on a directory boundary, and this shape is what puts it there.

`archituner` has no attribution prefix: a file is claimed only by a glob that matches it (`archituner/source/__init__.py:30`, `LayerMap.layer_of`), never by a prefix cut from one, so the prefix concerns that once filled this section name what no consumer can read. The `dir/**` rule stands on the boundary it draws and on the read-back below, not on a prefix.

**Make the glob denote exactly what the `Paths` cell of the `## Layers` row (§2) says.** Where the two disagree, the `dir/**` rule above wins and the `Paths` cell changes to match.

**Write out the concrete directories where a `Paths` cell names a level rather than a place.** A cell reading `modules/<concept>/` has no `dir/**` form - name the directories the architecture calls for, rather than reaching for `modules/*/**`.

**Write the glob for the intended home, not for today's files.** `controllers/workspaces/**` states where a workspace belongs; hand-listing the four files that exist now makes the fifth fall outside every rule.

### Which layer an import counts against

**Walk attribution as the ordered algorithm below, never as a set of independent facts.** `archituner` claims a file first and resolves an import second, so a reader resolving imports before claiming files counts traffic the run never counts.

0. **The walk reads the tree first: `.py` files, minus `__pycache__`, `.git`, any directory holding a `.git` of its own, everything the tree's own `.gitignore` hides, and everything the block's `ignore` list names.** A path none of those reaches is what every count below sits on.
1. **The deepest name whose glob matches a walked file claims it, declaration order inside a depth.** A sublayer takes what its parent's glob also matches, and an overlap between names neither an ancestor of the other is a finding at read time.
2. **An import counts against the pair of claiming names lifted to the level the two diverge.** Resolution is by module name against the walked files - as written, then under every top-level package the globs name, or from a declared `package_root` alone.
3. **An import resolving to no walked file, or to one whose claiming name lifts to the same judged layer as the importer's, counts nowhere.** No prefix channel, no attribution by text: an unresolvable import is invisible to every count, and an import inside one family - one layer, or two names the rule above lifts to one - is invisible to every pair.

Where an import resolves to an unclaimed file, no crossing forms either - a pair needs two claimed layers - so an unclaimed file's own traffic goes unreported alongside the imports reaching into it.

**Read silence as proving nothing until resolution is confirmed.** A tree whose imports resolve to nothing reads as silence in every pair while the code crosses edges freely, and no count separates it from a compliant one. Opening claimed files and resolving their imports by hand is the only thing that separates the two.

The distinction is internal: the document carries `crossings` and the four `counts`, so hand-resolving the imports is the only thing that separates an unresolved tree from a silent one - in a dot-import repo and an absolute-import one alike.

### Whether the consumer actually read the rule you wrote

**Treat a rule no consumer can read as no rule at all.** It is not a weaker rule, and its only symptom is a clean result.

**Read every rule back out of the consumer, and treat any difference from what you wrote as an `Error` (§3).** `archituner` refuses most differences itself - the structural rejections name their subject at exit 2 - so the comparisons below catch what still passes silently.

Two comparisons cover the block:

- [ ] The layer names the document's `layers` rows carry - one row per layer, its name in `name`, beside its globs, the paths it claims and the Responsibility and Rationale cells - against the layer names the block declares: same set, same spelling, no extras. Read them from ``python3 -m archituner <path>/ARCHITECTURE.md --json``. The rows and `order` sit in dependency order - checked as the rule alone: every `allow` edge's source above its target in `order`, which holds unless the `allow` edges close a cycle, a block the tool still runs and no linear order can satisfy - and never as the block's own declaration sequence, which the document may reorder even where every source is declared above its target.
- [ ] The pairs the document's `crossings` realise, against the pairs the block writes - every crossing carries its `source`, `target`, `kind` and `state`. A pair the block writes and no crossing realises is an absence or a silence, which is a state to explain and never a silent drop: the tool refuses a non-total pair set and an edge naming an unknown layer, so neither drop can happen quietly.

**Assume an unreported rule is unenforced, never that the consumer abbreviated.** A parser drops what it cannot read and says nothing, so silence on your side of the comparison is the finding.

**Check what a glob claims for attribution separately from what it matches.** The two came apart in both directions under the prefix consumer; under `archituner` the claim is the match, and the table below has what that still costs.

An import *naming* a file no layer claims creates no crossing at all - the pair needs two claimed layers - so that traffic goes unreported in both directions.

**Read the counts for the shapes the comparison cannot reach.** A block can report exactly what you wrote and still enforce nothing; the four `counts` and a reading of the globs against the tree find some of those.

**Read the table itself for the rest.** The shapes no count reaches at all are in there too, each with its own remedy.

A home the walk never enters and a file it cannot parse are found by the tree beside the globs; a crossing that is never an import, only by opening the claimed files.

The rows below fall in three groups: what the comparison catches, what it misses while the run succeeds, and what leaves no run to compare against.

A shape the tool refuses, or a repo it cannot walk, ends the run before either comparison exists. No group is the extent.

The second column is `archituner`'s behaviour, except where a row names what no consumer can read; another consumer built to this format may differ, and the read-back rule above is what covers that.

| Shape | What actually happens |
|---|---|
| `forbid` written in flow style (`forbid: [...]`), or a `layers` flow list wrapped across lines | Those entries parse to nothing. A flow-style `forbid` drops every edge at once, the pair set stops being total, and `archituner` refuses at exit 2 naming the first missing pair - while the block still reads as a full contract. A wrapped layer list keeps the fragment before the line break and drops the rest silently, so the layer survives with half its globs; reading each glob against its `Paths` cell is what catches it |
| A quoted edge (`- "web -> domain"`), or a layer name outside `[\w-]+` | The quoted edge is refused: `archituner` hand-parses the line quotes included, the source reads `"web`, no declared layer matches, and the run stops at exit 2 - ``rejected: edge names an unknown layer``. The bad layer name is what no consumer can read: the parser anchors a name on nothing but the `:`, so it accepts what you wrote and the read-back matches |
| Layer entries written as nested maps, each layer's value an indented `paths: [...]` | The layer entry itself parses to no globs, so `archituner` refuses - ``rejected: a layer has no globs: <name>`` - while the indented `paths` key parses as a layer of its own under that name. The refusal names the layer, which is what separates it from an absent home |
| An invented key whose value is an inline list, sitting between `layers:` and the next top-level key | It parses as a layer under its own name - the parser reads any `name: [globs]` line in the section - and the invented layer has no edges, so the pair set stops being total and the run refuses at exit 2 naming a missing pair. Sitting later in the block, the key is dropped with everything under it, and any edge written there takes its pair with it into the same refusal |
| A `forbid` edge whose source and target are the same layer | It parses and the run states it as a finding - `a layer names itself, which is not a pair` - so it surfaces among the findings the report counts, never as a crossing. The pair arithmetic never sees it, since N(N-1) excludes self-pairs |
| A `forbid` edge naming a layer absent from `layers` | Refused at exit 2, ``rejected: edge names an unknown layer: <edge>``. The count-never-matches reading is what no consumer can read - the tool stops before any counting |
| An empty `forbid` list | Every pair is permitted, so nothing can ever diverge and the run cannot exit 1 - which reads as no enforcement rather than as enforcement. Only the pair arithmetic finds it |
| A glob whose matches include, at any depth, a directory the walk skips - the home, any directory inside it, or any ancestor of it (`__pycache__`, `.git`, any directory holding a `.git` of its own, or anything the tree's own `.gitignore` hides) | Never walked. Where the layer's other globs match files, every pair the home would touch sits in its unrealised state and no count names the layer |
| A glob whose home resolves through a symlink - the home itself, or any ancestor of it - to a target *inside* the contract's directory | The home is never entered, because the walk follows no symlinked directory; the target is walked only where the walk reaches it by its real path, and claimed by whatever layer's globs match that path. The layer's own count falls to zero only where the symlink is its sole glob. Where another layer claims the target and the layer has a further matching glob, no field records the home at all. Either way the crossings enforce under the other layer's name, or not at all |
| A glob whose home resolves through a symlink out of the contract's directory, or names a directory the process cannot open | Never walked. `archituner`'s walk runs `os.walk` with its defaults, which follow no symlink and swallow a listing error, so the signature matches the skipped case above |
| A forbidden crossing written in a form the reader does not parse - `importlib.import_module(...)`, `__import__`, a string-built import path - or sitting in any file that is not Python | A `.py` file is walked, claimed and opened; the crossing is simply never an import. Python's own `import` and `from` statements are read whole - in-function ones, and every name of a multi-name import - so the residue is the dynamic and the non-Python, and no count marks either |
| A glob whose home holds files in extensions the walk does not read - everything but `.py` | Those files are never walked, so neither claimed nor unclaimed. Where they are the home's only files the glob contributes nothing; where the home mixes them with `.py` ones, the layer reads non-zero and nothing marks the half that went unread |
| A claimed source file the reader cannot parse - a file whose parse raises, or whose bytes are not decodable | It yields no imports silently while still counting as claimed, so its crossings reach no pair and no count says so. A file the walk cannot list or open at all fails the run outright - a plain exception naming the fact, no verdict |
| A source file matched by no layer's globs | Its imports are read - the walk needs the file as an import target - but no crossing can name it in either direction, because a pair needs two claimed layers. The unclaimed count the report prints counts the file, and no field says its traffic went unreported |
| A layer that is the source of no `forbid` edge | Nothing special: `archituner` reads every claimed file whatever its edges, so the layer's convergences and absences are stated like any other's. The ratio-over-a-subset reading is what no consumer can read - no attribution ratio exists |
| A layer whose globs name a path the tree does not hold - a stale path, or a brace expansion the parser splits at the comma | The layer is reported and its edges are stated, but every pair it touches sits in its unrealised state: no file, no witness. A stale path is silent in both directions - the prefix channels that once fired on imports naming no file are what no consumer can read. The comma cut is real: `{app,lib}/models/**` parses as the globs `{app` and `lib}/models/**`, neither of which any path matches, so the layer claims nothing - and where it was the only layer, the run fails at exit 3 |
| A layer key declared twice, the later one overwriting the earlier | The first glob list is discarded silently - the parser's dict assignment keeps the later one. The layer stays populated wherever the surviving glob matches files, so the read-back on names catches nothing; reading each glob against its `Paths` cell is what catches it, and nothing does where another layer claims the dropped glob's files. Resolving those paths as out of scope would cement the dropped glob into the contract |
| A glob whose attribution prefix names **more** files than the glob matches (`app/services/*_workspace.py` → prefix `app/services`) | What no consumer can read: `archituner` has no attribution prefix, so the glob claims exactly the files it matches and no import outside them is taken. The wider harm survives only through the glob's own width, which the manufactured-crossing test in `architect-cli` reads against the `## Layers` table |
| An import carrying a layer's prefix but naming no file in the repo (`@acme/app/models/user`, or `lib.app.models.rules`, against prefix `app/models`) | What no consumer can read as a crossing: the tool resolves an import against walked files only, so one naming no file creates nothing. The manufactured-crossing channel died with the prefix; a third-party or vendored path is invisible, and nothing separates it from an import the tree never wrote |
| A glob whose attribution prefix names **fewer** (`app/mod*/**` → prefix `app/mod`) | What no consumer can read: no prefix exists to truncate. The glob matches what it matches, and an import resolves to a claimed file or to nothing - the truncated-prefix escapes are gone with the channel |
| A prefix whose last segment names any directory an import can reach from a package root (`app/models/**` against `from models.lead import ...`) | What no consumer can read: the first-segment disjunct died with the prefix. The tool resolves `models.lead` by module name under the packages the globs name, so the import finds the file it actually names - claimed by whichever layer's glob matches that file, wherever it lives |
| A glob resolving to a literal file, with no `*` | The file is claimed, and imports resolve to it by its dotted name like any other. What the shape costs sits in the `Paths` cell it cannot denote, not in resolution |
| A dot-leading import that names a package directory rather than a file (`from ..models import user`) | The stem resolves to the package's `__init__` and the names to the modules beside it, by dotted name - the prefix stage that mishandled the dots is what no consumer can read |
| Prose-only dependency rule with no block edge | Reads as enforced; no consumer will ever see it |
| A repo in a language the walk does not read - it takes `.py` only | Zero files claimed, so the run fails at exit 3: its `reason` reads ``failed run: N file(s) walked, none claimed by any layer``, N counting the `.py` files tooling left in the tree. N above zero makes this signature indistinguishable from the skipped and symlinked-home rows above; N = 0 is its own case. The block is untested, not broken |

## 2. Body - the prose

**Give each concern one section, and no concern two.** §4 settles the unit every statement below must take.

**Keep the block the source of truth for dependency rules.** No section may add a dependency edge the block does not carry - the prose-only row of the table above is what that costs.

A `## Invariants` line narrowing an edge the block does carry is the narrowing rule below, not an addition.

**Give the body everything the block has no vocabulary for.** The coverage questions below name what that is.

**Give every layer in `layers` a `## Layers` row, and every row a layer.** A row with no layer is claimed by no glob and constrained by no edge, so nothing else reports it.

**Give every `forbid` edge a `## Boundaries` line, and every line an edge.** A line with no edge in the block is prose no consumer enforces.

**Add no section without a membership test.** Such a section collects whatever fits nowhere else and grows without limit; `## Do / Don't` and `## Concerns` are the ones that keep getting written.

Everything that would go in one is either a boundary with a reason or an invariant.

### Which section answers each coverage question, and how the answer is written

Completeness against the block proves only that the file describes its own layers, not that those layers describe an architecture.

The file is a contract when every question below has an answer in the section the answer-to-section table names.

| Question | Why silence means the file is not yet a contract |
|---|---|
| Where the outside world is touched - database, network, filesystem, clock, OS | Every architecture has an I/O edge; unnamed, nothing constrains it |
| How a lower layer receives what a higher layer owns - injection, callbacks, events, a composition root | The entire forbid list depends on this and the block cannot state it. Left unsaid, nothing in the file distinguishes "may not import" from "may not use", and it constrains neither |
| What may block, who owns the main or UI thread, where long work lives | An app with a responsiveness budget meets it structurally or not at all; the budget belongs to the product doc, the structure that makes it reachable belongs here |
| Which failures cross which boundary, and in what form | Otherwise every layer invents its own error contract at the moment it first needs one, and they disagree |
| How the largest layer is constrained internally | Two files in one layer name have **no rule between them** - a same-layer edge never fires, per §1's table - so a layer of many modules and no children is an unconstrained region, usually the one holding the most value |
| When a new unit of that layer is warranted | Without a growth rule the layer expands by accretion and the contract governs only the shape it already had |
| Who owns the data, and what laws bind its shape - the source of truth, a concept's identity, the law by which a persisted shape changes | Data outlives the code and is the most expensive thing to change; silent, identity defaults to whichever integration arrived first, and its key becomes the app's spine by accident |

**Give every answer the owning section the answer-to-section table below names, never a section of its own.**

| Answer | Its owning section |
|---|---|
| the I/O edge | a `## Layers` row - it is a layer |
| wiring, threading, failure propagation, same-layer scope, the growth rule, data ownership | a `## Invariants` line |
| any of these the architecture genuinely lacks | a `## Enforcement` out-of-scope line |

**Put the most precision where the value is.** If the layer holding the most value carries the fewest rules, the contract is inverted - and size is only usually that layer.

**Answer each concern in the shape its section takes.** A concern answered in the wrong shape is still unanswered - an I/O boundary recorded as a naming convention gives an audit nothing to act on.

### What a `## Layers` row must say

**Write one row per layer, in a table of layer | paths | responsibility | rationale.** The `Paths` cell is settled in §1, against the glob it must denote; what any one cell may hold is §4's.

**Fill the rationale cell with the distinction the split protects, never with what the folder holds.** Responsibility answers "what goes here" for the files already anticipated; rationale is what places the file nobody anticipated.

**Reject a rationale that is only "it is a different folder".** That layer is a folder, and the table should not pretend otherwise.

**Keep the Responsibility cell inside what the block permits that layer.** A cell naming work the layer cannot legally reach prescribes a contract nobody can build, and the completeness checks all still pass.

**Make every permission exercisable by that same Responsibility cell.** An `allow` edge the stated job has no use for means one of the two is wrong - and it is the fingerprint of an edge copied off the code rather than decided.

### What each `## Boundaries` line must contain, and where the work it displaces goes

**Give every `forbid` edge a line stating its reason.** A boundary with no reason gets deleted by the first person who finds it inconvenient.

**Say on that line where the work the edge displaces now lives.** A forbid removes a route, whatever used it still has to exist somewhere, and a boundary with no destination makes work homeless.

**Do not write the edge until its destination exists.** Ban domain modules from importing each other while naming no home for their shared vocabulary, and every cross-concept feature has nowhere legal to live but the UI.

**Never restate the layer's Rationale cell as the boundary's reason.** The Rationale says which distinction the split protects; this line says what the edge costs and where that cost now lands.

**Open a `-` item with its edge in backticks - or several, separated by ` / ` - then `: `, then the reason.** A wildcard may carry `except` and its backticked list before the `: `; what one `-` item may carry at all is §4's.

A consumer (§3) reading this section can only do so against a stated syntax; unstated, two built to this format disagree about what a legal line is.

### How many edges one `## Boundaries` line may carry, and when the compressed form is earned

**Let edges share one line only when they genuinely share one reason.** Grouping edges whose reasons differ hides the weaker reason inside the stronger one, and the weak rule is the one deleted later.

**Write the principle the group shares on that one line, never the incident behind any one edge.** A shared line is where §4's rule about stating a principle above the set it generates lands in this section.

| Form | Shape |
|---|---|
| Enumerated - the default | one or more edges sharing one reason, in the syntax above |
| Wildcard | denotes every forbidden pair among `A`'s siblings - the names sharing `A`'s parent - minus the exceptions and minus anything in `allow` |

**Earn the wildcard form; do not prefer it.** It states a group as a rule rather than as a list, which is the better shape - but its denotation changes the moment a layer is added, *without the line being edited*.

**Compress a `## Boundaries` line only where a reader expands it in both directions.** Both directions means every `forbid` edge reached by some line, and no line claiming an allowed pair is forbidden.

The mechanical check never reads this section and a person does, so the check is a person holding the layer list.

**Never compress because a tool prefers the shape.** The question is whether the group is one rule, never whether the file is shorter.

### Whether a pattern gets named at all, and where it goes instead of a `## Patterns` section

**Name a pattern only where some `forbid` edge is unbuildable without it.** The edge removes a route, and the pattern is the route replacing it.

That admits the seam-crossing patterns - Adapter, Facade, Mediator, Observer, Template Method - and essentially no creational one.

**Write the pattern on that edge's `## Boundaries` line, as the destination the line already owes.** A pattern with no edge behind it has no home in this file, which is the point.

**Write the property, with the well-known name in parentheses where one fits exactly.** "One gate per service (Facade)" - the name is a pointer, never the rule itself.

What makes a seam architectural is the interface and who owns it, never the mechanism that picks an implementation: whether the composition root uses a factory, a dict or an `if` is nobody's business.

**Add no `## Patterns` section.** Every pattern this file admits already has a home on the `## Boundaries` line of the edge it replaces, so a section collecting them has no membership test left.

### What goes in `## Invariants` that no edge and no cell can hold

**Write this section into every file.** It holds cross-cutting truths no single dependency edge can express, each violable by a diff, and the answer-to-section table above sends most of its answers here.

**Write only the two shapes below here.**

**Write neither anywhere else in the body.** A `## Boundaries` line may name the same mechanism again where it is the destination that edge owes.

**Send a contents-condition that fits one free-text line to the block's `naming` key instead.** One needing a layer name, a path standing in for one, an edge or a scope qualifier is this section's.

| Shape | What it looks like |
|---|---|
| A rule the block structurally cannot express | Same-layer scope is the common case - §1's table has what the consumer does with a `panels -> panels`. A condition on a file's *contents* rather than its path is a second; narrowing a permission to part of a layer, below, is a third |
| A recurring project-specific mistake | stated as the positive rule it violates, with its reason, in one sentence |

**Narrow a permission here that only part of a layer needs.** An `allow` edge is granted to every file the layer's globs match, so where the justification covers one component, only an invariant keeps the rest out.

### What `## Enforcement` must declare

The statements below, and the file is not honest without them.

- [ ] **That the file prescribes and the code is what moves** - the consumer meets a tree contradicting the file and must read the gap as migration, and only the file can tell them so.
- [ ] **What a machine fails on** - the `forbid` edges, plus anything the project's own boundary tool checks.
- [ ] **What only a reviewer can judge** - `naming` on §1's terms, every invariant, the responsibility and rationale cells, any layer home the consumer does not read, and every crossing form its patterns miss. Say plainly that this is most of the words.
- [ ] **What the contract does not claim** - source paths deliberately outside every layer (tests, scripts, generated code, tooling), and any coverage question declared out of scope.

**State each of them without a count.** A numeral is a second call site for a list that will change, and the first author to add a layer leaves it behind while every completeness check still passes.

Without *what a machine fails on*, nothing separates what a tool catches from what it does not; without *what only a reviewer can judge*, nothing names the far larger half no tool reads at all.

Without *what the contract does not claim*, an audit cannot tell a stray file from a test - opposite conclusions that both look like a clean result.

## 3. How a consumer grades a defect

How a well-behaved consumer - an agent, or the audit's mechanical check - treats input the format did not anticipate.

**Work the three steps below before the numbered rules under them.** The steps decide which row or rule applies; the rules decide the verdict.

1. **Take a row's verdict where the table below names the defect; otherwise take the first rule that reaches it, and stop.** The rules are ordered and the order decides the verdict, so a defect two of them reach is graded by the lower number.
2. **File two rows as two findings unless one fix closes both and the rows name one object.** A symlinked home and the unclaimed target it produces are two objects, and reporting the cheaper alone buries the other.
3. **Take the first row reading down only where both of those hold.** An undeclared layer on an edge and that edge's missing `## Boundaries` line are one object needing two fixes, so they are two findings too.

The rules:

1. **Grade a defect `Error` when it leaves a rule unevaluable or uncitable, or silently permits what the file means to forbid.** All three leave a rule the file states and no process can act on. A gap `## Enforcement` declares is not silent, and falls to rule 4.
2. **Grade it `Error` when a rule fires where the file permits.** Over-enforcement is not the safe direction - the rule that cried wolf is the one deleted next.
3. **Grade input the schema does not admit `Not a rule`, unless a consumer reads it - and then on what that consumer does with it.** Absent input is neither wrong nor enforced, and grading it otherwise implies something read it.
4. **Grade it `Warning` where the architecture may genuinely be right, no stated rule is breached, and only the file can say so.** The reviewer resolves it against `## Enforcement`, not against the tree.
5. **Grade a defect whose correction the file itself determines `Error`.** Nothing waits on the author, so the fix is not a judgement call and the loop cannot close over it.
6. **Grade `Warning` every defect this format names that no row of the table below names.** The rule is stated but only the author's intent can say whether it was meant differently, so they close it by fixing it or by declining in writing.

§1, §2 and §4 define more defects than this table lists, and rule 6 is what reaches them.

| Scenario | Verdict |
|----------|----------|
| Unknown top-level block key - one outside `layers`, `dependencies`, `naming`, `package_root`, `ignore` and `limits` | Not a rule; report it, with the home §1 assigns - unless it parses as a layer, per §1's table, or anything a `layers` or `dependencies` entry would hold is written under it, and then Error against the block. Nothing nested under such a key is read: a `-` item outside `allow`, `forbid`, `naming`, `ignore` and `overrides` reaches no list, and a `name: [globs]` line is a layer only inside the `layers` section. The pair-set refusal catches every drop an edge was in; what survives it is dropped at exit 0 while the block still reads as a full contract |
| Layer named in a `forbid` edge but absent from `layers` | Error |
| Edge between names of two different parents | Error; §1's sublayer rules - the parents' edge already judges the crossing, and the block is refused outright |
| Dotted name whose parent is not declared | Error; §1's sublayer rules - the refusal names both names and nothing runs |
| `## Boundaries` line naming a pair of non-siblings | Error; §1's sublayer rules - it states a second opinion about a pair the parents' edge already decides, so it names no edge of its own |
| File a child's glob claims and no glob of the parent's | Error; §1's claim rules - the claim sits outside the set the parent's edges govern |
| File claimed by a parent with children and by no child | Error; §1's claim rules - the file escapes the sibling pairs that decide its family |
| `limits` override whose selector reaches no file | Warning; the override governs nothing, and only the author knows whether the selector is stale |
| `ignore` glob matching no walked file, or taking a file a layer's glob would claim | Warning; the tool states both as findings - the first is a dead glob, the second a file every rule lost - and only the author knows which was meant |
| `forbid` edge whose source and target are the same layer | Error; per §1's table, it reads as enforced and cannot fire |
| `A -> *` in the block's `forbid` list | Error; per §1's rule against a wildcard in the machine half |
| `A -> *` in the block's `allow` list | Error; per §1's rule against a wildcard in the `allow` list |
| A file whose rules describe the tree rather than prescribe a target shape | Error; §4's thesis, judged by the reasoning order §4 names. A Rationale cell claiming no more than a different folder is the one tell the artifact carries; a layer set matching the tree is not, since a finished migration produces that too |
| A laundering move §4 names, in the block or the prose | Error; the rule was reached by asking what makes the code legal, and §4 denies the file can settle that |
| A fact stated in both this file and an agent-facing sibling | Error; §4's one-home rule, and where the sibling does not link to this file the pair is uncitable too |
| A link in this file to anything outside itself - an issue, the decision log, the README, another repo, a plan, a skill, a path | Error; §4's self-contained rule - the sibling's link into this file is the one legal direction |
| Two layers, neither an ancestor of the other, whose globs match the same file | Error |
| Ordered sibling pair in neither `allow` nor `forbid` | Error |
| Layer that is the *source* of no `forbid` edge | No finding where the layer sits at the top of a strictly downward layering; otherwise Warning, an enumeration gap. Either way §1's table has what the run states for such a layer, and check it against the pair set rather than against `## Enforcement` |
| `allow` edge the layer's Responsibility cell has no use for | Error |
| Responsibility cell naming work the block forbids that layer | Error; the contract cannot be built |
| A source path matched by no layer's globs | Warning; resolve against `## Enforcement`, and note that §1's table has what the run does with an unclaimed file |
| A layer home that resolves through a symlink to a target inside the root | Error; per §1's table, and resolving its files out of scope buries the home |
| Section referenced by a sibling doc but absent from the file | Error; the file is depended on from outside. §4 sends the fix to the sibling's anchor - inventing the section to receive it is the move §2 bans |
| `forbid` edge named by no `## Boundaries` line, reading each wildcard at the expansion §2 defines | Error |
| `## Boundaries` line whose syntax departs from the shape §2 states | Error; §2 has a consumer reading this section against that syntax and no other, so the line names no edge and the row above reaches its edge too |
| `## Boundaries` line whose edges, at the expansion §2 defines, include one absent from `forbid` | Error |
| Layer in `layers` with no row in `## Layers` | Error |
| `## Layers` row for a layer absent from `layers` | Error; no glob claims it and no edge constrains it, so nothing else reports the gap |
| `## Enforcement` missing any of its statements | Error |
| The I/O-edge or the wiring question, unanswered and undeclared | Error; §2's why for each is that the file then constrains nothing at all |
| Any other coverage question unanswered and undeclared | Warning |
| Duplicate section heading | Error; reject the file |

## 4. What a statement must be to belong in the file

### What makes a statement checkable by a diff

**Make every rule violable by a diff.** Facts and invariants, not vibes: "the layering is clean" fails; "`domain` imports nothing outside `domain`" passes.

The `## Enforcement` statements and the Rationale cells are the exceptions §2 mandates: they describe the file, not the code.

**Write declaratively, not imperatively.** State the invariant and its reason, not "Do not make controllers import models."

### Where a negation belongs and where the positive rule goes

**Keep the `forbid` list and every `## Boundaries` edge negative.** A forbidden pair is the only form a consumer can test - "the domain is self-contained" is not a predicate while `domain -> web` is.

**Keep the reason half of a `## Boundaries` line positive.** It names where the displaced work now lives.

**State the positive rule in `## Invariants` wherever a positive form exists and no `## Boundaries` reason already carries it.** A prohibition closes the one door it names; the positive form tells the reviewer what the right shape *is*, in the same sentence count.

**Admit those two kinds of negation anywhere in the file.** One is the *reason*, naming the failure mechanism; one is the case where the *contrast is the content*, a named trap - "names the capability, never the vendor" is that second kind.

**Keep the positive half when you catch yourself writing a rule and its negation in one sentence, unless the negation is one of the two kinds above.** That pairing is the common mistake, and the negative clause usually restates the positive one.

### What unit a rule is written in

**Write one sentence per cell.** A second sentence in a cell is a rule with no `-` of its own, so nothing can cite it and nothing can delete it cleanly.

**Write one rule per `-` item.** Split when a second imperative hides inside, one a diff could break while the first holds - except a `## Boundaries` line carrying several edges that share one reason, which §2 settles as one rule.

**Write no paragraph anywhere in an ARCHITECTURE.md.** Anything that is not a rule in a `-` item, a table cell or a heading has no home - and bare sentences between blocks render as one paragraph, which nothing can cite.

### What bounds the file's growth

**Bound the file's growth deliberately, because nothing else does.** Each added sentence is justified on its own and none of them is weighed against the total.

**Move a rule that is not holding into the block or into a test; do not write it more carefully.** More careful prose is the lever that already failed once, and a second pass at it buys length rather than enforcement.

**Cut what an expert reader knows.** A boundary's line carries the *reason* the edge is forbidden - the part only the architecture knows - not what an import is, and not the block's edges restated in prose.

### Whether a rule came from the ideal or from the code, and which of the two gives

**State the target shape, never the current one.** Where the code has not arrived, the gap is drift for an audit to report; a contract describing what exists is an inventory, and an inventory constrains nothing.

**State a reason in a Rationale or Boundaries cell for every deviation from the best-practice shape for this class of product.** A deviation with no reason is the existing tree showing through, and nothing downstream can tell it from a decision.

**Refuse every move below that launders the code into the contract.** Some live in the block and some in the prose; widening a glob takes the unclaimed count to zero and retires the §3 Warning that pointed at the stray, so no count records that move either.

- [ ] widening a glob to cover a stray
- [ ] deleting a `forbid` edge because something violates it
- [ ] promoting `forbid` to `allow` because the code crosses it
- [ ] leaving a pair unlisted once you find the code crosses it
- [ ] rewriting a rule's *reason* until an existing crossing is justified
- [ ] widening a layer's *definition* until today's occupants qualify

**Decide a layer's membership by a fact inside the file.** A test resolvable only by how many things use a file or how long it is flips that file's layer without an edit to it, which is the same failure as laundering.

**Judge laundering by the order of reasoning, never by the wording.** A rule reached by asking *"how do I make what exists legal?"* is laundering however defensible it reads afterwards.

**Verify against the code to learn what the drift is, never to decide what the rule should be.**

**Leave a file that sits outside its home where it is.** The audit reports the gap; the glob does not move to cover it.

### Which doc owns a fact the agent-facing siblings share

**Give every fact one home across the agent-facing docs.** The operational doc (AGENTS.md / CLAUDE.md) states the same architectural facts as instructions while this file states them as properties, so a text search never finds the pair.

**Link this file to nothing outside itself: no issue, decision log, README, another repo, plan, skill or path.** A reader holding this file alone must hold the whole contract; the link is the sibling's to carry - into this file, never out of it.

Three steps, in order:

1. Compare by fact, never by wording.
2. Decide which doc owns it.
3. Remove the duplicate; where a link remains, it runs from the sibling - never from this file.

**Name every agent-facing sibling where the body says which one owns what, the operational doc first.** It has the largest overlap and is the one nobody thinks to list.

**Never rename a heading an agent-facing sibling anchors into.** The link is the sibling's, but the heading is this file's to keep, and renaming one silently breaks a dependency stated outside the file.

**Send an anchor naming a heading this file does not owe back to the sibling.** The fix is the link, not a section invented to receive it - §2 bans several such sections outright.

### Which level a rule is stated at

**State the principle that generates a set of rules above the set.** A forbid list that is the closure of "dependencies point downward" costs one rule to carry, not one per edge - and one resolver rule beats three bullets naming three resolvers.

**State the method that generates rules, not the incidents that produced them.** This binds `naming` hardest: free text invites an incident log - a banned-name list, a named class, a transcribed convention - legible only to whoever lived it.

**Treat a rule naming a class, a file or a number as an instance of a general rule.** The general rule belongs here; the specifics are handed to the feature's doc, the test that pins them, or the decision log's owner.

**History belongs to the decision log, handed to its owner - never an entry written here; this file states the rule that holds now.**

## 5. Worked skeleton

```markdown
---
layers:
  web:    ["app/controllers/**", "app/views/**"]
  app:    ["app/services/**"]
  domain: ["app/models/**"]
  infra:  ["app/adapters/**"]
dependencies:
  allow:
    - web -> app
    - web -> infra
    - app -> domain
    - infra -> app
    - infra -> domain
  forbid:
    - web -> domain
    - app -> web
    - app -> infra
    - domain -> web
    - domain -> app
    - domain -> infra
    - infra -> web
naming:
  - "a port names the capability, never the vendor"
---

## Layers

| Layer  | Paths | Responsibility | Rationale |
|---|---|---|---|
| web | app/controllers, app/views | HTTP in/out, and the composition root that constructs `app` and `infra` and wires them together | the transport is the part most likely to be replaced, so nothing else may depend on its shape |
| app | app/services | orchestrates use-cases; calls domain; declares the interfaces infra implements | a use-case spans several domain objects, and that coordination belongs to neither of them |
| domain | app/models | business rules; depends on nothing | rules that depend on nothing can be tested and reused from a job, a CLI, or another app |
| infra | app/adapters | DB, external APIs, the clock; implements the interfaces app declares, mapping domain objects across that edge | external systems fail and change on someone else's schedule, so they are held at one edge |

## Boundaries

- `web -> domain`: a controller reaches domain rules through the service that orchestrates them, so a rule change lands in one place and not in every controller that copied it.
- `app -> infra`: `app` declares the interface and is handed an implementation by the composition root, so a use-case can be tested against a fake (Adapter).
- `app -> web` / `infra -> web`: a lower layer that needs a transport decision receives it as a parameter from its caller, so neither is pinned to the surface that happened to call it first.
- `domain -> web` / `domain -> app` / `domain -> infra`: what the domain needs from outside arrives as a value, or as an interface `app` declares on its behalf, so the rules stay runnable with no framework loaded.

## Invariants

- A layer receives what a higher layer owns by constructor injection from the composition root in `web`.
- Only the composition root in `web` names `infra`.
- A controller reaches an infra capability through `app`.
- Only `infra` blocks.
- `app` runs on the caller's thread.
- `domain` runs on the caller's thread.
- Long work lives behind an `infra` port.
- Only `web` and `infra` start a thread.
- A failure leaves `domain` as a domain error type.
- A failure is translated at the `web` edge.
- Only the `web` edge names a status code.
- A `domain` module imports another domain module's top-level interface only.
- A new `domain` module is warranted when a concept owns its own persistence; short of that it is a type inside an existing one.
- A concept's identity is owned by its `domain` module.
- That `domain` module is the source of truth for the concept; no integration's key displaces it.
- A persisted shape changes only by a migration that preserves the identity its `domain` module owns.

## Enforcement

- This file states the target shape; where the code differs, the code is what moves.
- Machine-checked: the `forbid` edges, run in CI by the repo's boundary check.
- Reviewer judgement: `naming`, every `## Invariants` line, every Responsibility and Rationale cell, all of `app/views`, whose templates no walked extension reaches, and every dynamic `importlib` call - reviewer judgement is most of the words in this file.
- Not claimed: `spec/**`, `db/migrate/**`, `config/**`, `lib/tasks/**`, `bin/**` and the generated API client sit outside every layer deliberately.
```

Read off the skeleton: four layers give twelve ordered pairs, and the block names twelve - five permitted, seven forbidden.

`web -> infra` is permitted because `web` holds the composition root, which must name what it constructs; the `Only the composition root in web names infra` invariant then keeps the rest of `web` out of that edge, which the block alone cannot do.

Every coverage question has the one owning section the answer-to-section table names - I/O the `web` and `infra` Layers rows, the other six one or more `## Invariants` lines. The two lines narrowing `web`'s reach into `infra` are the permission narrowing, not a coverage answer.

`app -> infra` names the composition root again, which §2's exception permits.
