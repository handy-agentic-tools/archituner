---
package_root: "."

limits:
  size: 8000
  defs: 8
  depth: 4
  cyclomatic: 30
  cognitive: 50
  prose_count: 0

  overrides:
    - "size `cli`: 4000 - argv to intent to exit code, almost no decisions"
    - "defs `cli`: 5 - argv to intent to exit code, almost no decisions"
    - "cyclomatic `cli`: 15 - argv to intent to exit code, almost no decisions"
    - "cognitive `cli`: 20 - argv to intent to exit code, almost no decisions"
    - "cyclomatic `run`: 20 - the stage order is linear and decides nothing"
    - "cognitive `run`: 30 - the stage order is linear and decides nothing"
    - "defs `vocabulary`: 15 - many small value types, almost no logic"
    - "depth `vocabulary`: 3 - many small value types, almost no logic"
    - "cyclomatic `vocabulary`: 15 - many small value types, almost no logic"
    - "cognitive `vocabulary`: 20 - many small value types, almost no logic"
    - "size `tests_unit`: 10000 - many short trivial test functions"
    - "defs `tests_unit`: 20 - many short trivial test functions"
    - "depth `tests_unit`: 3 - many short trivial test functions"
    - "cyclomatic `tests_unit`: 25 - many short trivial test functions"
    - "cognitive `tests_unit`: 30 - many short trivial test functions"
    - "size `tests_integration`: 12000 - tree setup, a process run, several assertions per flow"
    - "defs `tests_integration`: 15 - tree setup, a process run, several assertions per flow"
    - "size `tests_lints`: 4000 - one rule over source text"
    - "defs `tests_lints`: 5 - one rule over source text"
    - "cyclomatic `tests_lints`: 20 - one rule over source text"
    - "cognitive `tests_lints`: 30 - one rule over source text"

layers:
  cli:          ["archituner/cli/**", "archituner/__main__.py"]
  run:          ["archituner/run/**"]
  report:       ["archituner/report/**"]
  conformance:  ["archituner/conformance/**"]
  contract:     ["archituner/contract/**"]
  source:       ["archituner/source/**"]
  matching:     ["archituner/matching/**"]
  vocabulary:   ["archituner/vocabulary/**"]
  tests_unit:        ["tests/unit/**"]
  tests_integration: ["tests/integration/**"]
  runner:            ["tests/run.py"]
  tests_lints:       ["tests/lints/**"]

dependencies:
  allow:
    - cli -> run
    - cli -> report
    - cli -> vocabulary
    - report -> vocabulary
    - run -> conformance
    - run -> contract
    - run -> source
    - run -> vocabulary
    - conformance -> vocabulary
    - contract -> matching
    - contract -> vocabulary
    - source -> matching
    - source -> vocabulary
    - tests_unit -> cli
    - tests_unit -> run
    - tests_unit -> report
    - tests_unit -> conformance
    - tests_unit -> contract
    - tests_unit -> source
    - tests_unit -> matching
    - tests_unit -> vocabulary
  forbid:
    - cli -> conformance
    - cli -> contract
    - cli -> source
    - cli -> matching
    - run -> cli
    - run -> report
    - run -> matching
    - report -> cli
    - report -> run
    - report -> conformance
    - report -> contract
    - report -> source
    - report -> matching
    - conformance -> cli
    - conformance -> run
    - conformance -> report
    - conformance -> contract
    - conformance -> source
    - conformance -> matching
    - contract -> cli
    - contract -> run
    - contract -> report
    - contract -> conformance
    - contract -> source
    - source -> cli
    - source -> run
    - source -> report
    - source -> conformance
    - source -> contract
    - matching -> cli
    - matching -> run
    - matching -> report
    - matching -> conformance
    - matching -> contract
    - matching -> source
    - matching -> vocabulary
    - vocabulary -> cli
    - vocabulary -> run
    - vocabulary -> report
    - vocabulary -> conformance
    - vocabulary -> contract
    - vocabulary -> source
    - vocabulary -> matching
    - cli -> tests_unit
    - cli -> tests_integration
    - cli -> runner
    - run -> tests_unit
    - run -> tests_integration
    - run -> runner
    - report -> tests_unit
    - report -> tests_integration
    - report -> runner
    - conformance -> tests_unit
    - conformance -> tests_integration
    - conformance -> runner
    - contract -> tests_unit
    - contract -> tests_integration
    - contract -> runner
    - source -> tests_unit
    - source -> tests_integration
    - source -> runner
    - matching -> tests_unit
    - matching -> tests_integration
    - matching -> runner
    - vocabulary -> tests_unit
    - vocabulary -> tests_integration
    - vocabulary -> runner
    - tests_unit -> tests_integration
    - tests_unit -> runner
    - tests_integration -> cli
    - tests_integration -> run
    - tests_integration -> report
    - tests_integration -> conformance
    - tests_integration -> contract
    - tests_integration -> source
    - tests_integration -> matching
    - tests_integration -> vocabulary
    - tests_integration -> tests_unit
    - tests_integration -> runner
    - runner -> cli
    - runner -> run
    - runner -> report
    - runner -> conformance
    - runner -> contract
    - runner -> source
    - runner -> matching
    - runner -> vocabulary
    - runner -> tests_unit
    - runner -> tests_integration
    - cli -> tests_lints
    - run -> tests_lints
    - report -> tests_lints
    - conformance -> tests_lints
    - contract -> tests_lints
    - source -> tests_lints
    - matching -> tests_lints
    - vocabulary -> tests_lints
    - tests_unit -> tests_lints
    - tests_integration -> tests_lints
    - runner -> tests_lints
    - tests_lints -> cli
    - tests_lints -> run
    - tests_lints -> report
    - tests_lints -> conformance
    - tests_lints -> contract
    - tests_lints -> source
    - tests_lints -> matching
    - tests_lints -> vocabulary
    - tests_lints -> tests_unit
    - tests_lints -> tests_integration
    - tests_lints -> runner

naming:
  - "archituner/** imports only the Python standard library and archituner itself"
  - "every archituner import is resolvable by reading the importing file, so it is written at the top and never assembled from a name at runtime"
---

## Layers

| Layer | Home | Responsibility | Rationale |
|---|---|---|---|
| cli | `archituner/cli/`, and `archituner/__main__.py` as the entry point nothing imports | Turns the arguments into a stated intent, chooses which artifact the intent asks for and hands `run` that artifact's builder as a value, and turns the outcome into an exit code | the invocation is the part a second consumer replaces first, so the work must be reachable without it, and an artifact left out of a release is one no import beneath the invocation names |
| run | `archituner/run/` | Executes one intent end to end: orders the stages, passes each one's value to the next, calls the builder it is handed on the reading, reads and writes every file that is neither the contract nor the analysed tree, and decides whether the run succeeded; it names no artifact | the order of the stages is a decision of its own, and a decision belonging to no layer is one each caller reinvents |
| report | `archituner/report/` | Builds the text artifacts: the check report, the terminal and markdown reading, the machine document, and the sections they are assembled from | the text is what an agent and a gate read, so it changes with the gate's needs alone |
| conformance | `archituner/conformance/` | Answers every question about a contract and a file graph already in hand: the state of each pair, the shape measures, the coverage regions, and how one reading differs from another | this is the only claim the tool makes, so it stays a pure function of the values handed in and can be refuted by a table rather than by a tree |
| contract | `archituner/contract/` | Turns one `ARCHITECTURE.md` into a contract value: the block, the refusals it earns, the prose the body carries, and the findings that are about the contract's own shape | the format is written by another skill and will grow keys, so exactly one layer may know its shape |
| source | `archituner/source/` | Everything about the analysed language: which files a tree holds, which layer claims each, what each imports, and what names the entry layer exposes | a second language is the one growth the product has promised, and it arrives here or it arrives everywhere |
| matching | `archituner/matching/` | Decides whether a glob claims a path, and whether two globs can claim one path | it is the vocabulary in which both input formats state where things live, so it belongs to neither of them and is provable on strings alone |
| vocabulary | `archituner/vocabulary/` | Every value a stage may hand to another - a contract, a pair and its state, a file and its imports, a finding, a reading, a comparison - each holding the law that makes a wrong one unconstructible | a stage is replaceable and the values crossing between stages are not, so naming them is what lets any stage be rewritten without the others agreeing to something new |
| tests_unit | `tests/unit/` | Proves one source file's behaviour by calling that file's functions with values built in memory | a unit test that reached past its own module would fail for a change it does not cover, and a red line would stop naming the file that moved |
| tests_integration | `tests/integration/` | Proves one CLI flow end to end by running the tool as a user runs it and reading what it wrote and how it exited | the invocation is the contract a user holds, so the flow is proved through it rather than through the stages behind it |
| runner | `tests/run.py` | Turns a set of changed paths into the tests that verify them, runs them, and says whether all of them passed | a gate pays for the change in front of it, so choosing which tests a change owes is a decision of its own rather than each caller's habit |
| tests_lints | `tests/lints/` | Proves one rule over the source text that holds across files - no literal colour, no forbidden call, a size or naming limit - by reading the files, never by running them | a rule over the whole tree is checked by reading it, so it holds for code no test executes and cannot be bent by the code it judges |

## Boundaries

- **Only `run` may know that more than one stage exists; every other layer knows the values it is handed and nothing about who handed them.** Each line below is that one rule applied to a group, not a separate prohibition to carry.
- `vocabulary -> *`: a value and its law compute nothing and depend on nothing, which is what lets every stage share one vocabulary while sharing nothing else; a rule about one value belongs to its own type, and a rule about two belongs to the stage holding both.
- `matching -> *`: glob semantics are string algebra and know neither a contract, a tree, nor a value of this product, so a caller passes in the two strings and reads the answer.
- `report -> *` except `vocabulary`: a text artifact is built from a finished reading alone, so a value it needs that the reading lacks is a gap in the reading, filled by `conformance`.
- `conformance -> *` except `vocabulary`: the tool's one claim is refutable only if it is a pure function of values, so the contract and the file graph arrive as arguments and never as something this layer went to get; fetching either is `run`'s.
- `contract -> *` except `matching`, `vocabulary`: knowing anything about the analysed tree would let a rule of the format be decided by what some tree happens to hold, so what the block means for real paths is `source`'s question and what the tree lacks is `conformance`'s finding.
- `source -> *` except `matching`, `vocabulary`: the language adapter is the seam a second language replaces whole, so it must not know what a conformance state is, what the contract's prose says, or that an artifact exists; it answers what the tree holds and stops.
- `cli -> *` except `run`, `report`, `vocabulary`: an invocation that reaches a stage directly has bound the stages to argument parsing, and the second consumer then has to satisfy an argument parser to run anything.
- `run -> cli`: the sequence must be executable with no invocation present, or it can only be tested through the one that exists.
- `run -> matching`: the orchestrator constructs and orders, so a root reaching into glob internals has taken over a layer's job and that layer can no longer be reasoned about alone.
- `run -> report`: the root runs one sequence whatever artifact closes it, so it calls the builder it is handed and imports none; a release that leaves an artifact out changes the invocation and nothing beneath it.
- `run -> tests_unit`, `run -> tests_integration`, `run -> runner`, and every other `archituner/` layer's line above: the product ships without its tests, so nothing it runs may need one present.
- `tests_unit -> *` except the `archituner/` layers: a unit test proves one module, so it shares no helper with another test and needs no runner to be run.
- `tests_integration -> *`: a flow is proved through the entry point a user holds, so it imports nothing of the tool and reaches it only as a process.
- `runner -> *`: the runner selects and runs tests by their paths, so it imports neither a test nor the tool, and a test that only passes under it is a test that cannot be run alone.
- `run -> tests_lints`, `tests_lints -> *`: a lint reads the source as text, so it imports nothing of the tool and nothing the tool ships imports it, and a module it judges cannot change what it measures.

## Invariants

### Where the outside is

- Of the `archituner/` layers, exactly three reach outside the process: `source` reads the analysed tree, `contract` reads the one contract it is given, and `run` reads and writes everything else - artifacts, baselines, and any sibling contract the surface reading needs.
- Nothing under `archituner/**` reads the clock, opens a socket, or resolves a name on the network.
- A conformance run is drivable from a file graph built in memory, so the tool's one claim can be exercised with no tree on disk.

### Construction and wiring

- Construction is chained from `run` down: each layer receives what it does not own as an argument, so a forbidden upward edge never costs a capability.
- A stage returns a value and never a callback into whoever called it, so the pipeline stays a sequence a reader follows in one direction.
- Two readings compared arrive as the same value type, so the comparison cannot tell which of them came from disk.

### What a run must establish

- A run in which no layer claimed a file has evaluated no rule and is a failed run, not a clean one, because an unrun check and a passing check produce the same silence.
- Every gate the tool offers fails on every class of defect the run can detect, so a gate that passes means the run found nothing rather than that it looked for one thing.
- Two runs over one unchanged tree produce identical bytes, so a difference between two artifacts means the code moved.

### Failure

- A structural defect in the contract raises before any tree is walked and ends the run as a refusal, which is an outcome an artifact renders rather than a state the tool exits silently on.
- Everything that is not a refusal is a finding carried inside the reading: `contract` states the findings about the contract's own shape, `conformance` states those that need the tree.
- A finding names the contract line or the import statement that produced it, so nothing is drawn that the run did not measure.
- A failure leaves any layer as a plain exception naming the fact, so no caller parses a message to learn what went wrong.

### Inside conformance

- A conformance module answers one question and imports another module's public function only, never its internals.
- A new conformance module is warranted when its question can be stated and refuted independently of the questions beside it; a variant of a question already answered is a parameter.
- The reading carries the counts and the groupings; how any of it is laid out in space belongs to whoever draws it.

### Inside source

- An adapter is reached only through the file graph it returns, and no adapter imports another, so a second language is added without the first being consulted.
- What a file's imports mean is the adapter's alone: no layer above it re-parses a source file to decide anything.

### Inside tests

- A unit test file mirrors one source file: `archituner/<dir>/<name>.py` is proved by `tests/unit/<dir>/test_<name>.py`, and a layer's `__init__.py` by `tests/unit/<dir>/test_<dir>.py`.
- A unit test imports the module it mirrors, and `vocabulary` for the values that module is handed; it never imports another module of the tool, so a red unit test names the file that broke.
- An integration test file proves one CLI flow, runs the tool as `python -m archituner` in its own process, and imports nothing of the tool, so the flow is proved exactly as a user meets it.
- Every test file runs alone, as `python <file>`, and imports only the Python standard library and the tool, so the runner is a convenience and never a precondition.
- `tests/run.py` given paths runs the unit tests mirroring the changed source files and the integration flows that exercise them; given none it runs every test, and either way it ends with `all green` only when every test it ran passed.
- A test is written for the behaviour its unit adds or changes; code no unit touched is not backfilled.
- A lint file states one rule over the source text, reads the files it judges with the Python standard library alone, and imports nothing of the tool.
- `tests/run.py` given paths also runs every lint whose rule covers a changed file, and given none it runs every lint.
- An integration or lint file names what it exercises on its first line, or its second after a shebang, as `# covers:` followed by space-separated globs relative to the repository root, matched as `fnmatch` patterns, so `*` crosses `/` and a pattern can only select more tests than the contract's own glob reading would, never fewer. That line is a directive the runner reads, not prose, and nowhere else in the file does `# covers:` mean anything. A file with no such line covers every path and runs on every scoped run, so a missing declaration costs time and never a skipped check.

### Limits

- An override tightens `cyclomatic` and `cognitive` and never loosens them, so decision-dense code has no home where its complexity is excused.
- A file reaches a looser limit only through a layer or a glob in this file, never through a list of files or a marker inside the file, so the code under judgement cannot choose its own limit.
- Every override marks a weak spot and its reason names the change that removes it; an override whose reason names no such change is not granted, so a looser limit is a debt with its repayment written down, never a permanent home.
- Literal text a module carries - markup, style, data in strings - is measured apart from `size`, so a module holding an artifact's text needs no looser limit for its code.

### Data

- The contract file is the source of truth and every artifact is derived, so a run may be thrown away and repeated without the user losing anything they wrote.
- A baseline is a document this tool wrote for itself to read back, so it carries no rule, and its absence is a state rather than an error.

## Enforcement

- **This file states the shape this tool is meant to have.** Where the code differs, the code is what moves, and a gap the size of the whole tree is the migration rather than evidence against the contract.
- Machine-checked: every `forbid` edge, and the totality of the pair set - each ordered pair of layers named exactly once across the two lists; and every number under `limits`, each file against the default or the layer's own figure.
- Reviewer judgement, and it is most of the words here: both `naming` rules, every line under `## Invariants`, and every Responsibility and Rationale cell. **No tool reads them**, and none is claimed to.
- Not claimed, deliberately: `archituner/__init__.py`, which is the package root and holds no module of its own; the project's own documents; and anything the repository's `.gitignore` excludes. Any other unclaimed source path is drift.
- The re-exports `archituner/__init__.py` holds produce no edge, and are therefore a route around every rule here that only a reviewer closes. Also not claimed: a derivation script the product does not ship, whose output a test pins.
- Out of scope: what may block and who owns a thread. The generator is a batch run that holds no thread of its own, and the rendered artifact's own responsiveness is a budget measured in interactions.
- What a `forbid` edge means is that no **import** crosses it, which is narrower than the boundary it names: an edge is also crossed when a layer is handed an object of another and calls through it, when a routine is written a second time rather than imported, and when a stage does the next one's work inline instead of returning a value. Those are the reviewer's.

### Not this file's subject

- This file states the shape and its rules, never their history, the product's purpose, or the state of the work.
