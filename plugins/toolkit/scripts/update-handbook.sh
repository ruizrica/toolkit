#!/usr/bin/env bash
# ABOUTME: called by git hooks; regenerates HANDBOOK.md if relevant files changed.
# ABOUTME: never blocks a commit; LLM-assisted refresh is opt-in via CLAUDE_HANDBOOK_LLM_REFRESH=1.

set -uo pipefail

GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
[ -z "$GIT_ROOT" ] && exit 0
cd "$GIT_ROOT" || exit 0

PLUGIN_ROOT="${TOOLKIT_PLUGIN_ROOT:-}"
if [ -z "$PLUGIN_ROOT" ]; then
  for candidate in \
    "$HOME/.claude/plugins/cache/toolkit/toolkit" \
    "$HOME/Workshop/GitHub/agent-toolkit/plugins/toolkit"; do
    [ -f "$candidate/scripts/handbook.py" ] && PLUGIN_ROOT="$candidate" && break
  done
fi

HANDBOOK_PY="$PLUGIN_ROOT/scripts/handbook.py"
[ -f "$HANDBOOK_PY" ] || exit 0

# Fast-skip when only handbook/context/logs/DS_Store changed
CHANGED="$(git diff --name-only HEAD~1 HEAD 2>/dev/null | \
  grep -vE '^(HANDBOOK\.md|\.context/|\.agent-memory/|\.DS_Store)' || true)"
[ -z "$CHANGED" ] && exit 0

# Deterministic regeneration — fast, no LLM cost
python3 "$HANDBOOK_PY" --path . --output HANDBOOK.md --quiet 2>/dev/null || true

# Opt-in LLM refresh
if [ "${CLAUDE_HANDBOOK_LLM_REFRESH:-0}" = "1" ] && command -v claude >/dev/null 2>&1; then
  claude -p "Review the diff in the last commit and refresh stale sections of HANDBOOK.md. Only edit the handbook." \
    --dangerously-skip-permissions \
    --max-turns 10 \
    2>/dev/null || true
fi

# Stage the handbook so it rides along with the next commit.
# Intentionally no auto-commit here — let the user commit naturally.
git diff --quiet HANDBOOK.md 2>/dev/null || git add HANDBOOK.md 2>/dev/null || true

exit 0
