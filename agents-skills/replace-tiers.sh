#!/usr/bin/env bash
# Replace `agent-tier: <name>` tokens with the chosen provider's column of the
# tiers.yaml matrix, in place, over each file or directory named.
#   replace-tiers.sh <provider> <file-or-dir>...
# Unknown tokens are left untouched - a survivor stays grep-visible. A zcode
# cell names both fields a ZCode agent file pins with, so substituting a
# `model: agent-tier: X` line emits two real frontmatter lines: model: and
# thoughtLevel: (the backslash before the real newline is what BSD sed reads
# as a newline in a replacement).
set -euo pipefail

[ $# -ge 2 ] || { echo "usage: replace-tiers.sh <provider> <file-or-dir>..." >&2; exit 2; }
provider="$1"; shift
matrix="$(cd "$(dirname "$0")" && pwd)/tiers.yaml"

plain="" ; pair=""
while read -r tier cc zm zl; do
  if [ "$provider" = zcode ]; then
    plain="$plain;s/agent-tier: $tier/$zm/g"
    pair="$pair;"'s/^model: agent-tier: '"$tier"'$/model: '"$zm"'\'$'\n''thoughtLevel: '"$zl"'/'
  else
    plain="$plain;s/agent-tier: $tier/$cc/g"
    pair="$pair;"'s/^model: agent-tier: '"$tier"'$/model: '"$cc"'/'
  fi
done < <(grep -E '^  [a-z-]+:' "$matrix" | sed -E 's#^  ([a-z-]+):[[:space:]]+([^[:space:]]+)[[:space:]]+\{model: ([^,]+), thoughtLevel: ([a-z]+)\}.*$#\1 \2 \3 \4#')

replace() {
  for f in "$@"; do
    [ -f "$f" ] || continue
    # pair first: plain would otherwise eat the token on a model: line and
    # the thoughtLevel line would never be emitted.
    LC_ALL=C sed -i '' -e "$pair" -e "$plain" "$f"
  done
}
for target in "$@"; do
  if [ -d "$target" ]; then
    while IFS= read -r f; do replace "$f"; done \
      < <(find "$target" -type f \( -name '*.md' -o -name '*.env' \))
  else
    replace "$target"
  fi
done
