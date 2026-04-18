#!/usr/bin/env bash
# ABOUTME: installs post-merge and post-commit git hooks that keep HANDBOOK.md fresh.
# ABOUTME: idempotent; backs up any existing hooks as .bak before overwriting.

set -euo pipefail

GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [ -z "$GIT_ROOT" ]; then
  echo "ERROR: not inside a git repository" >&2
  exit 1
fi

HOOKS_DIR="$GIT_ROOT/.git/hooks"
mkdir -p "$HOOKS_DIR"

PLUGIN_ROOT="${TOOLKIT_PLUGIN_ROOT:-}"
if [ -z "$PLUGIN_ROOT" ]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  PLUGIN_ROOT="$(dirname "$SCRIPT_DIR")"
fi

if [ ! -f "$PLUGIN_ROOT/scripts/update-handbook.sh" ]; then
  echo "ERROR: $PLUGIN_ROOT/scripts/update-handbook.sh not found" >&2
  exit 1
fi

install_hook() {
  local hook_name="$1"
  local hook_path="$HOOKS_DIR/$hook_name"

  if [ -f "$hook_path" ] && ! grep -q "TOOLKIT_AUTO_HANDBOOK" "$hook_path" 2>/dev/null; then
    cp "$hook_path" "$hook_path.bak"
    echo "  backed up existing hook → $hook_path.bak"
  fi

  cat > "$hook_path" <<EOF
#!/usr/bin/env bash
# TOOLKIT_AUTO_HANDBOOK — installed by plugins/toolkit/scripts/install-git-hooks.sh
# Runs handbook refresh; failures never block the commit/merge.
bash "$PLUGIN_ROOT/scripts/update-handbook.sh" || true
EOF

  chmod +x "$hook_path"
  echo "✓ installed $hook_name → $hook_path"
}

install_hook post-commit
install_hook post-merge

echo ""
echo "Git hooks installed. HANDBOOK.md will auto-refresh after each commit/merge."
echo "For LLM-assisted refresh (opt-in): export CLAUDE_HANDBOOK_LLM_REFRESH=1"
