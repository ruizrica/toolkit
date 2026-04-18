#!/usr/bin/env bash
# ABOUTME: installs the agent-memory CLI so /setup, /restore, /agent-memory, and skills can use it.
# ABOUTME: prefers pip editable install from ~/.toolkit/tools/agent-memory; falls back to other known paths.

set -euo pipefail

if command -v agent-memory >/dev/null 2>&1; then
  echo "✓ agent-memory already installed: $(command -v agent-memory)"
  exit 0
fi

CANDIDATES=(
  "${AGENT_MEMORY_SRC:-}"
  "$HOME/.toolkit/tools/agent-memory"
  "$HOME/Workshop/GitHub/agent-toolkit/tools/agent-memory"
)

SRC=""
for candidate in "${CANDIDATES[@]}"; do
  if [ -n "$candidate" ] && [ -d "$candidate" ] && [ -f "$candidate/pyproject.toml" -o -f "$candidate/setup.py" ]; then
    SRC="$candidate"
    break
  fi
done

if [ -z "$SRC" ]; then
  echo "ERROR: agent-memory source not found." >&2
  echo "Tried: ${CANDIDATES[@]}" >&2
  echo "Set AGENT_MEMORY_SRC=/path/to/agent-memory and re-run." >&2
  exit 1
fi

echo "Installing agent-memory from: $SRC"

PIP_FLAGS=(-e "$SRC")
if pip3 install --help 2>/dev/null | grep -q -- "--break-system-packages"; then
  PIP_FLAGS=(--break-system-packages "${PIP_FLAGS[@]}")
fi

pip3 install "${PIP_FLAGS[@]}"

if ! command -v agent-memory >/dev/null 2>&1; then
  echo "ERROR: agent-memory not on PATH after install." >&2
  echo "You may need to add pip's user bin to PATH." >&2
  exit 1
fi

echo "✓ agent-memory installed: $(command -v agent-memory)"

# Best-effort: fetch the embedding model the CLI needs for semantic search
if agent-memory install --help >/dev/null 2>&1; then
  echo "Downloading embedding model (~67MB) ..."
  agent-memory install || echo "⚠ agent-memory install (model download) failed — run it manually later."
fi
