# rr-config

Complete Claude Code power-user configuration with multi-agent orchestration, TDD workflows, and advanced productivity commands.

## Installation

```bash
claude plugins add ./plugins/rr-config
```

## Contents

### Agents (8)

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

### Commands (6)

| Command | Description |
|---------|-------------|
| `/team` | Coordinate multi-agent team for parallel implementation |
| `/review` | CodeRabbit review + parallel fixes + verification |
| `/handbook` | Generate comprehensive project handbook |
| `/@implement` | Process @implement comments into documentation |
| `/save` | Git: stage, commit, rebase, merge |
| `/stable` | Create stable checkpoint with tags/branches |

### Optional MCP Commands (7)

Located in `optional/` - require Commander or Photon MCP servers:

| Command | Requires |
|---------|----------|
| `/commander-task` | Commander MCP |
| `/commander-plan` | Commander MCP |
| `/commander-execute` | Commander MCP |
| `/photon-compact` | Photon MCP |
| `/photon-restore` | Photon MCP |
| `/photon-index` | Photon MCP |
| `/haiku` | - |

## Setup Scripts

For `/handbook` and `/review` commands:

```bash
mkdir -p ~/.claude/slash_commands
cp scripts/handbook.py ~/.claude/slash_commands/
cp scripts/coderabbit_workflow.py ~/.claude/slash_commands/
```

## License

MIT
