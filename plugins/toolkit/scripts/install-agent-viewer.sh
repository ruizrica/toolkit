#!/usr/bin/env bash
# ABOUTME: installs the agent-viewer CLI globally so /kiro and skills/agent-viewer.md can use it.
# ABOUTME: prefers the plugin-bundled copy at plugins/toolkit/tools/agent-viewer; falls back to legacy paths and npm.

set -euo pipefail

if command -v agent-viewer >/dev/null 2>&1; then
  echo "✓ agent-viewer already installed: $(command -v agent-viewer)"
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="${TOOLKIT_PLUGIN_ROOT:-$(dirname "$SCRIPT_DIR")}"

CANDIDATES=(
  "${AGENT_VIEWER_SRC:-}"
  "$PLUGIN_ROOT/tools/agent-viewer"
  "$HOME/.claude/plugins/cache/toolkit/toolkit/tools/agent-viewer"
  "$HOME/.toolkit/plugins/toolkit/tools/agent-viewer"
  "$HOME/.toolkit/tools/agent-viewer"
  "$HOME/Workshop/GitHub/agent-toolkit/plugins/toolkit/tools/agent-viewer"
  "$HOME/Workshop/GitHub/agent-viewer"
)

SRC=""
for candidate in "${CANDIDATES[@]}"; do
  if [ -n "$candidate" ] && [ -d "$candidate" ] && [ -f "$candidate/package.json" ]; then
    SRC="$candidate"
    break
  fi
done

if [ -n "$SRC" ]; then
  if ! command -v npm >/dev/null 2>&1; then
    echo "ERROR: npm not found — cannot install agent-viewer from $SRC" >&2
    echo "Install Node.js/npm first (https://nodejs.org)." >&2
    exit 1
  fi
  echo "Installing agent-viewer from: $SRC"
  npm install -g "$SRC"
elif command -v npm >/dev/null 2>&1; then
  echo "Attempting npm install -g agent-viewer ..."
  npm install -g agent-viewer
else
  echo "ERROR: agent-viewer source not found and npm is not available" >&2
  echo "Tried: ${CANDIDATES[@]}" >&2
  echo "Set AGENT_VIEWER_SRC=/path/to/agent-viewer or install Node.js/npm first." >&2
  exit 1
fi

if ! command -v agent-viewer >/dev/null 2>&1; then
  echo "ERROR: agent-viewer not on PATH after install" >&2
  exit 1
fi

echo "✓ agent-viewer installed: $(agent-viewer --version 2>/dev/null || command -v agent-viewer)"
