#!/usr/bin/env bash
# ABOUTME: readiness check for the toolkit's cohesive system.
# ABOUTME: reports on agent-memory, agent-viewer, HANDBOOK.md, session state, and daily logs.

set -uo pipefail

print_row() { printf "%-18s %s\n" "$1:" "$2"; }

# agent-memory
if command -v agent-memory >/dev/null 2>&1; then
  STATUS="$(agent-memory status 2>/dev/null | tr '\n' ' ' || true)"
  print_row "agent-memory" "✓ installed   ${STATUS:-(status unavailable)}"
else
  print_row "agent-memory" "✗ missing — run: bash plugins/toolkit/scripts/install-agent-memory.sh"
fi

# agent-viewer
if command -v agent-viewer >/dev/null 2>&1; then
  VERSION="$(agent-viewer --version 2>/dev/null || echo '?')"
  print_row "agent-viewer" "✓ installed   $VERSION"
else
  print_row "agent-viewer" "✗ missing — run: bash plugins/toolkit/scripts/install-agent-viewer.sh"
fi

# HANDBOOK.md
GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
if [ -f "$GIT_ROOT/HANDBOOK.md" ]; then
  LINES="$(wc -l < "$GIT_ROOT/HANDBOOK.md" | tr -d ' ')"
  print_row "HANDBOOK.md" "✓ present ($LINES lines)"
else
  print_row "HANDBOOK.md" "— not generated (run /handbook or /setup)"
fi

# CLAUDE.md
if [ -f "$GIT_ROOT/CLAUDE.md" ]; then
  if grep -q "Orchestration Manifest" "$GIT_ROOT/CLAUDE.md"; then
    print_row "CLAUDE.md" "✓ present   ✓ orchestration manifest"
  else
    print_row "CLAUDE.md" "✓ present   ⚠ orchestration manifest missing"
  fi
else
  print_row "CLAUDE.md" "— missing (run /setup)"
fi

# session state
if [ -f "$GIT_ROOT/.context/session-state.json" ]; then
  print_row "session-state" "✓ saved"
else
  print_row "session-state" "— (no saved session)"
fi

# daily logs
LOG_DIR="$HOME/.claude/agent-memory/daily-logs"
if [ -d "$LOG_DIR" ]; then
  RECENT="$(find "$LOG_DIR" -name '*.md' -mtime -7 2>/dev/null | wc -l | tr -d ' ')"
  print_row "daily logs" "$RECENT entries in last 7 days"
else
  print_row "daily logs" "— no log directory"
fi

# git hooks
HOOK_DIR="$GIT_ROOT/.git/hooks"
if [ -f "$HOOK_DIR/post-commit" ] && grep -q "TOOLKIT_AUTO_HANDBOOK" "$HOOK_DIR/post-commit" 2>/dev/null; then
  print_row "git hooks" "✓ post-commit + post-merge"
else
  print_row "git hooks" "— not installed (run /setup)"
fi
