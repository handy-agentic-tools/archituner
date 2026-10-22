# archituner

**Your code is tangling, and you can't see it.**
archituner shows you where, draws the plan your project is missing, and keeps your AI building to it.

## Why

Think of a house built without a plan. Rooms go wherever they fit, cables run through any wall, and
every repair breaks something in another room. Nobody sees the cracks until something falls down.

That is what happens to code your AI writes fast, with no plan to follow.

**Software isn't random. Neither should building it be.**

You do not need to know what good architecture looks like. archituner works like a design firm:
the architect draws the plan and explains it in plain words, you approve it, and the site
supervisor checks the build against it.

## Start in 4 steps

1. Install archituner (under a minute):

   ```sh
   pip install git+https://github.com/handy-agentic-tools/archituner
   ```

2. Give your agent the architect's skills (Claude Code):

   ```sh
   claude plugin marketplace add handy-agentic-tools/archituner
   claude plugin install architect@archituner
   ```

3. Ask your agent:

   *"Look at this project, draw up an ARCHITECTURE.md for it, and explain it to me in plain words."*

   Approve the plan, or ask for changes until you can.

4. Run the supervisor:

   ```sh
   archituner ARCHITECTURE.md
   ```

   It lists every place your code breaks the plan, with the fix. Nothing printed and exit 0 means the build follows the plan. For the whole picture run `archituner ARCHITECTURE.md --report`.

## What it does

A building gets a design firm. Your code gets archituner. It does the firm's three jobs:

| Job | A design firm | archituner |
| --- | --- | --- |
| **Survey** | measures the building that already stands | maps your code: what stands, what works, what does not |
| **Design** | draws the plan; the owner approves it | drafts `ARCHITECTURE.md`: the floors of your project, what may rest on what, and why; you approve it |
| **Supervision** | checks the build against the plan | reports every deviation and names the fix |

Your AI is the construction crew. It builds fast and rarely reads the plan. That is why the plan needs
a supervisor.

## Floors, in one sentence

The plan splits your project into **floors** (developers say *layers*): each floor rests on the ones
the plan allows, never on one it forbids.

## What the supervisor reports

Every pair of floors gets one of four marks:

| Mark | On site | What to do |
| --- | --- | --- |
| ✓ | rests where the plan says | nothing |
| ✗ | rests where the plan forbids | remove it: the report names the exact lines |
| ○ | the plan allows it, nobody built it | fix the plan, or ask why the code went around it |
| · | the plan forbids it, nobody built it | nothing: the rule holds |

It also lists what no plan covers: **files on no floor**, and **floors with nothing built**.

A deviation looks like this:

```console
$ archituner ARCHITECTURE.md
divergence: api -> db
    shop/api/admin.py imports shop.db
    shop/api/admin.py imports shop.db.session
    contract: a handler that queries storage skips the rules, so every write goes through `domain`.
    remedy: remove the 1 import statement(s) in 1 file(s) crossing api -> db, starting with shop/api/admin.py:1
```

The report quotes the plan's own reason for the rule, then the fix.

The whole picture, in the terminal:

```console
$ archituner ARCHITECTURE.md --report
ARCHITECTURE.md in demo
verdict: divergent
counts: ✓ convergence 1  ✗ divergence 1  ○ absence 1  · silence 3
  claimed 7  unclaimed 1
  prose 0.0% of claimed non-blank lines
findings
  no findings
limit breaches
  no limit breaches
matrix: rows import columns; layers in dependency order
          api     domain  db
  api             ✓       ✗
  domain  ·               ○
  db      ·       ·
```

## Read it from your phone

Coding with an agent from a phone or a cloud session means reading results in a chat or a pull request, not in a terminal. `archituner ARCHITECTURE.md --report --format md` turns the whole reading into Markdown. Paste it into the chat with your agent or into a pull request comment, and it reads on a phone screen:

```markdown
|  | api | domain | db |
| --- | --- | --- | --- |
| api |   | ✓ | ✗ |
| domain | · |   | ○ |
| db | · | · |   |
```

## Every room gets inspected too

Besides what rests on what, the supervisor measures each file and function against limits written in the plan:

| Limit | What a breach tells you |
| --- | --- |
| `size` | a file grew big enough to split |
| `defs` | a file does too many things at once (count of functions and classes) |
| `depth` | code nested too deep to follow |
| `cyclomatic` | a function with so many paths it is hard to test |
| `cognitive` | code that is hard for a person to read |
| `prose_count` | code that needs comments to explain it instead of reading clearly |

The check fails on any breach:

```console
limit breach: shop/domain/orders.py: size 56 over 20
```

You set the limits in the plan's `limits` block, and a floor can get its own overrides with a stated reason.

## Keep the supervisor on site

Add one line to your CI. Every pull request that breaks the plan stops until it is fixed:

```sh
archituner ARCHITECTURE.md
```

<details>
<summary>GitHub Actions example, checking only what the pull request changed</summary>

```yaml
# .github/workflows/architecture.yml
name: architecture
on: [pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install git+https://github.com/handy-agentic-tools/archituner
      - run: archituner ARCHITECTURE.md --file $(git diff --name-only origin/${{ github.base_ref }}...HEAD)
```

`--file` checks only the deviations the changed files cause, so old ones do not block new work.
Paths are relative to the plan's directory, forward-slashed.

</details>

## For developers

<details>
<summary>Write the plan by hand</summary>

The plan is a Markdown file with a YAML block on top. Floors (layers) are path globs. Every ordered pair of
floors is allowed or forbidden. Every forbidden pair gets one sentence saying why.

```markdown
---
limits:
  size: 8000
  defs: 8
  depth: 4
  cyclomatic: 30
  cognitive: 50
  prose_count: 0

layers:
  api:    ["shop/api/**"]
  domain: ["shop/domain/**"]
  db:     ["shop/db/**"]

dependencies:
  allow:
    - api -> domain
    - domain -> db
  forbid:
    - api -> db
    - domain -> api
    - db -> api
    - db -> domain
---

# Shop architecture

`api` handles HTTP, `domain` holds the rules, `db` talks to storage.

## Boundaries

- `api -> db`: a handler that queries storage skips the rules, so every write goes through `domain`.
- `domain -> api`, `db -> *`: the rules and the storage know nothing about HTTP, so either can be tested alone.
```

Every limit is optional, and overrides per floor go under `limits:` as `overrides:`, each line naming the limit, the floor, the new value and the reason, for example ``- "cognitive `cli`: 20 - argv to intent to exit code, almost no decisions"``.

archituner checks the plan too: it refuses a plan that leaves a pair undecided, the check fails on a glob that matches nothing, and `--report` names any forbidden pair no Boundaries line explains.

</details>

<details>
<summary>Every output</summary>

| Command | Output |
| --- | --- |
| `archituner ARCHITECTURE.md` | the check: every deviation, limit breach and plan finding, each deviation with its fix; exit 1 on any |
| `--report` (`--format md`) | the whole reading in the terminal, or as Markdown for a pull request comment |
| `--json` | the whole reading as one JSON document, for an agent or a script: per floor what it uses and what uses it (`uses`, `used_by`), how many steps it sits from the program's entry point (`chain`), and the longest chain of imports (`shape.longest_chain`, e.g. `cli -> run -> conformance -> vocabulary`) |
| `--baseline` | stores this reading; later runs show what moved since |
| `--version` | the version |

Narrow any of them with `--layer`, `--state`, `--file`, `--min-weight`.

</details>

<details>
<summary>The architect's seven skills</summary>

| Skill | Job |
| --- | --- |
| `architect` | designs, reviews and maintains the plan; answers "where does this belong?" while code is written |
| `architecture-cartograph` | surveys an existing project into a plan |
| `architecture-democrat` | shapes the plan with the team |
| `architecture-autocrat` | holds the plan: the code gets no vote on the design |
| `architecture-audit` | reviews the plan, and finds the deviations no import scan proves |
| `architecture-md` | owns the plan's format |
| `architect-cli` | runs archituner and reads what it reports |

Not on Claude Code? Copy them to any agent that reads `~/.agents/skills/`:

```sh
git clone https://github.com/handy-agentic-tools/archituner
cp -R archituner/agents-skills/skills/* ~/.agents/skills/
```

</details>

<details>
<summary>Limits</summary>

- Python projects only, and only import statements are judged: dynamic imports (`importlib.import_module`, `__import__`) are invisible.
- Files your `.gitignore` excludes are never walked, and a file that does not parse is read as having no imports.
- Your own package named like a standard library module (a local `json` or `logging`) is never judged.
- It supervises the floors, what rests on what, and the limits. It does not replace tests or code review.
- Version 0.1.0. The plan's format may still change.
- No interactive page yet: it comes in the next release.

</details>

<details>
<summary>Contributing</summary>

Found a bug or missing a feature? [Open an issue](https://github.com/handy-agentic-tools/archituner/issues/new/choose).

Run the suite from a clone:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python tests/run.py
.venv/bin/archituner ARCHITECTURE.md --check
```

The last line is archituner supervising its own code.

</details>

## What comes next

archituner is built in the open, one release at a time. No dates, only the order.

1. **The plan and the build, on one page.** An interactive page that draws your floors, what rests on what, and every deviation. Designed for a phone first, so you can read it during remote vibe coding. It ships with its own agent skill.
2. **Copy-paste detection.** The supervisor finds functions whose bodies are duplicated across your project.
3. **The page in your terminal.** The same views, without leaving the shell.
4. **More languages.** The plan format is not tied to Python; other languages can be read by adapters over the same format.

Have a need that is not on the list? [Open a feature request](https://github.com/handy-agentic-tools/archituner/issues/new/choose).

## License

[GPL-3.0](LICENSE)

---

**Next:** run step 1 above.
