#!/usr/bin/env bash
# ABOUTME: installs the agent-viewer CLI globally so /kiro and skills/agent-viewer.md can use it.
# ABOUTME: prefers `npm install -g` when the package is published; falls back to the local sibling repo.

set -euo pipefail

if command -v agent-viewer >/dev/null 2>&1; then
  echo "✓ agent-viewer already installed: $(command -v agent-viewer)"
  exit 0
fi

LOCAL_SRC="${AGENT_VIEWER_SRC:-$HOME/Workshop/GitHub/agent-viewer}"

if [ -d "$LOCAL_SRC" ] && [ -f "$LOCAL_SRC/install.sh" ]; then
  echo "Installing agent-viewer from local source: $LOCAL_SRC"
  (cd "$LOCAL_SRC" && bash install.sh)
elif command -v npm >/dev/null 2>&1; then
  echo "Attempting npm install -g agent-viewer ..."
  npm install -g agent-viewer
else
  echo "ERROR: agent-viewer not found at $LOCAL_SRC and npm is not available" >&2
  echo "Set AGENT_VIEWER_SRC=/path/to/agent-viewer or install Node.js/npm first." >&2
  exit 1
fi

if ! command -v agent-viewer >/dev/null 2>&1; then
  echo "ERROR: agent-viewer not on PATH after install" >&2
  exit 1
fi

echo "✓ agent-viewer installed: $(agent-viewer --version 2>/dev/null || command -v agent-viewer)"
