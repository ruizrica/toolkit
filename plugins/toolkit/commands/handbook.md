---
description: Generate comprehensive project handbook
argument-hint: [--path PROJECT_PATH] [--output FILENAME] [--verbose]
allowed-tools: Bash(python3:*)
context: fork
agent: general-purpose
---

Generate a comprehensive, AI-optimized handbook for this project.

Structure:
- **Layer 1** — System Overview (Purpose, Tech Stack, Architecture)
- **Layer 2** — Module Map (Core Modules, Data Layer, Utilities)
- **Layer 3** — Integration Guide (APIs, Interfaces, Configuration)
- **Layer 4** — Extension Points (Design Patterns, Customization Areas)

The generator is bundled with the plugin at `scripts/handbook.py`. `/setup` seeds `HANDBOOK.md` on first run, and git hooks keep it fresh on every commit/merge — call this command only when you want to refresh on demand or pass custom flags.

Running handbook generation with arguments: $ARGUMENTS

```bash
!TOOLKIT_PLUGIN_ROOT="${TOOLKIT_PLUGIN_ROOT:-$HOME/.claude/plugins/cache/toolkit/toolkit}"
if [ ! -f "$TOOLKIT_PLUGIN_ROOT/scripts/handbook.py" ]; then
  TOOLKIT_PLUGIN_ROOT="$HOME/Workshop/GitHub/agent-toolkit/plugins/toolkit"
fi
python3 "$TOOLKIT_PLUGIN_ROOT/scripts/handbook.py" $ARGUMENTS
```
