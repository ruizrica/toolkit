# Toolkit

Complete Claude Code power-user configuration with multi-agent orchestration, TDD workflows, and advanced productivity commands.

## Installation

```bash
claude plugins add ./plugins/toolkit
```

## Contents

### Agents (9)

| Agent | Specialty |
|-------|-----------|
| gemini-agent | Large codebase analysis (1M tokens), Google Search |
| cursor-agent | Advanced code review, refactoring, sessions |
| codex-agent | Natural language to code, multi-language |
| qwen-agent | Agentic coding, workflow automation |
| opencode-agent | 75+ AI models via OpenRouter |
| groq-agent | Fast inference, lightweight tasks |
| crush-agent | Media compression/optimization |
| droid-agent | Enterprise code generation |
| rlm-subcall | Chunk analysis for RLM workflow |

### Commands (14)

| Command | Description |
|---------|-------------|
| `/team` | Coordinate multi-agent team for parallel implementation |
| `/review` | CodeRabbit review + parallel fixes + verification |
| `/handbook` | Generate comprehensive project handbook |
| `/@implement` | Process @implement comments into documentation |
| `/haiku` | Spawn team of 10 Haiku agents managed by Opus |
| `/rlm` | Recursive Language Model for large documents |
| `/gherkin` | Extract business rules into Gherkin specs |
| `/agent-memory` | Search and manage agent memories with hybrid search |
| `/worktree` | Manage git worktrees for isolated agent workflows |
| `/setup` | Initialize project context and run agent-memory indexing |
| `/save` | Commit, merge WIP to main, cleanup |
| `/stable` | Create stable checkpoint with tags |
| `/compact` | Save session state before /clear |
| `/restore` | Restore session from saved state |

### Skills (2)

| Skill | Description |
|-------|-------------|
| just-bash | Sandboxed bash execution (read-only FS, no network, in-memory writes) |
| agent-memory | Local hybrid search (vector + BM25) for memory files |

Skills are reference files installed to `~/.claude/skills/` that teach Claude when and how to use specific CLI tools.

### Optional MCP Commands (6)

Located in `optional/` - require Commander or Photon MCP servers:

| Command | Requires |
|---------|----------|
| `/commander-task` | Commander MCP |
| `/commander-plan` | Commander MCP |
| `/commander-execute` | Commander MCP |
| `/photon-compact` | Photon MCP |
| `/photon-restore` | Photon MCP |
| `/photon-index` | Photon MCP |

## Setup Scripts

For `/handbook` and `/review` commands:

```bash
mkdir -p ~/.claude/slash_commands
cp scripts/handbook.py ~/.claude/slash_commands/
cp scripts/coderabbit_workflow.py ~/.claude/slash_commands/
```

## License

MIT
