# architect

One [Agent Skill](https://agentskills.io), `skills/architect`, split out of
[handy-agentic-tools](https://github.com/handy-agentic-tools) skills collection
into its own plugin so it can be installed, versioned and updated on its own.

Beside it ship its siblings - `architecture-md`, `architecture-autocrat`,
`architecture-democrat`, `architecture-cartograph`, `architecture-audit` and
`architect-cli` - and `architecture-ui`, a release 2 skill: it reads the HTML
page, which release 1 does not ship.

## Install

**Claude Code**

```sh
claude plugin marketplace add handy-agentic-tools/archituner
claude plugin install architect@archituner
```

The same two steps work inside a running session as `/plugin marketplace add`
and `/plugin install`. The skill is then invoked as `/architect:architect`.

**ZCode**

1. Settings → Plugins → **Add marketplace** → `handy-agentic-tools/archituner`.
2. Install architect from its card - new installs are enabled by default.

**Codex, Cursor, and the rest**

```sh
git clone https://github.com/handy-agentic-tools/archituner
cp -R archituner/agents-skills/skills/* ~/.agents/skills/
```

`~/.agents/skills/` is every project; `.agents/skills/` inside a repo is that
repo only. Cursor can also pull the repository directly - **Customize → Rules →
Add Rule → Remote Rule (GitHub)** - no clone needed.

## Updating

A client re-copies a plugin only when its `version` bumps - a push without a
bump reaches nobody.

```sh
claude plugin marketplace update archituner
claude plugin update architect
```

Restart the session to load what changed.

## Paths

No path in the skill is machine-specific - its commands address the skill's own
directory as `<skill-dir>`, resolved to wherever the plugin is installed.

## Model tiers

The skill's agent files and spawn rules name a tier, never a provider's model:
`agent-tier: cheap|standard|deep`. [tiers.yaml](tiers.yaml) at the plugin root is the
matrix - a row per tier, a column per provider - and `replace-tiers.sh` resolves it in
place over any file or directory:

```sh
replace-tiers.sh <provider> <file-or-dir>...
```

The chosen provider's cell replaces every `agent-tier: <name>` token. Run it with
`zcode` and each `model: agent-tier: <name>` frontmatter line turns into two real
lines, `model:` and `thoughtLevel:`; a token the matrix does not know is left as it is,
so a survivor stays findable by grep. The committed files are the neutral source; the
resolved flavour exists only where the script has run.
