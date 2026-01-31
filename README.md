<p align="center">
  <img src="assets/toolkit.png" alt="Toolkit" width="400">
</p>

<p align="center">
  <strong>A Claude Code plugin with multi-agent orchestration, TDD workflows, and advanced productivity commands.</strong>
</p>

---

## Installation

```bash
# Clone this repository
git clone https://github.com/ruizrica/agent-toolkit.git

# Install the toolkit plugin
claude plugins add ./agent-toolkit/plugins/toolkit
```

### Setup Scripts (Required for /handbook and /review)

```bash
mkdir -p ~/.claude/slash_commands
cp plugins/toolkit/scripts/handbook.py ~/.claude/slash_commands/
cp plugins/toolkit/scripts/coderabbit_workflow.py ~/.claude/slash_commands/
```

---

## Quick Start

### Multi-Agent Development
```bash
/team Implement user authentication with OAuth support
```
Spawns multiple specialized agents to work on your feature in parallel.

### Code Review & Fixes
```bash
/review --base main
```
Runs CodeRabbit review, creates parallel fix tasks, and verifies completion.

### Session Continuity
```bash
/compact    # Before /clear
/clear      # Clear context
/restore    # Resume seamlessly
```

### Git Worktree Workflow
```bash
/setup      # Create isolated worktree
# ... develop ...
/save       # Merge back to main
```

---

## Documentation

| Section | Description |
|---------|-------------|
| [Commands](docs/commands/README.md) | All 12 commands with usage and examples |
| [Agents](docs/agents/README.md) | All 9 specialized agents with invocation patterns |
| [Optional Commands](docs/optional/README.md) | MCP-dependent commands (Commander + Photon) |

---

## Commands at a Glance

### Core Commands

| Command | Description | Docs |
|---------|-------------|------|
| `/team` | Multi-agent parallel implementation | [→](docs/commands/team.md) |
| `/haiku` | 10 Haiku agents managed by Opus | [→](docs/commands/haiku.md) |
| `/review` | CodeRabbit review + parallel fixes | [→](docs/commands/review.md) |
| `/handbook` | Generate AI-optimized project docs | [→](docs/commands/handbook.md) |
| `/@implement` | Process @implement comments | [→](docs/commands/implement.md) |
| `/rlm` | Large document processing | [→](docs/commands/rlm.md) |
| `/gherkin` | Extract business rules to Gherkin | [→](docs/commands/gherkin.md) |

### Session & Git

| Command | Description | Docs |
|---------|-------------|------|
| `/compact` | Save session state | [→](docs/commands/compact.md) |
| `/restore` | Restore after /clear | [→](docs/commands/restore.md) |
| `/setup` | Create WIP worktree | [→](docs/commands/setup.md) |
| `/save` | Commit, merge, cleanup | [→](docs/commands/save.md) |
| `/stable` | Create stable checkpoint | [→](docs/commands/stable.md) |

---

## Agents at a Glance

| Agent | Specialty | Docs |
|-------|-----------|------|
| **gemini-agent** | Large codebase analysis (1M tokens), Google Search | [→](docs/agents/gemini.md) |
| **cursor-agent** | Code review, refactoring, sessions | [→](docs/agents/cursor.md) |
| **codex-agent** | Natural language → code, translation | [→](docs/agents/codex.md) |
| **qwen-agent** | Agentic coding, workflow automation | [→](docs/agents/qwen.md) |
| **opencode-agent** | 75+ AI models via OpenRouter | [→](docs/agents/opencode.md) |
| **groq-agent** | Fast inference, rapid iteration | [→](docs/agents/groq.md) |
| **crush-agent** | Media compression/optimization | [→](docs/agents/crush.md) |
| **droid-agent** | Enterprise development, Jira/Notion | [→](docs/agents/droid.md) |
| **rlm-subcall** | Document chunk analysis for /rlm | [→](docs/agents/rlm-subcall.md) |

### Using Agents

```
Task tool with:
- subagent_type: "toolkit:gemini-agent"
- prompt: "Analyze the authentication module..."
```

---

## Requirements

### Core
- Claude Code 2.1+
- Python 3.8+ (for /handbook, /review, /rlm scripts)

### Optional
- **agent-browser** - For /gherkin visual analysis (`npm install -g agent-browser`)
- **Commander MCP** - For task orchestration commands
- **Photon MCP** - For memory and semantic search commands

---

## Directory Structure

```
agent-toolkit/
├── plugins/toolkit/
│   ├── agents/          # 9 specialized agents
│   ├── commands/        # 12 commands
│   ├── scripts/         # Python scripts
│   └── optional/        # MCP-dependent commands
├── docs/
│   ├── commands/        # Command documentation
│   ├── agents/          # Agent documentation
│   └── optional/        # MCP commands documentation
├── assets/              # Images
├── CLAUDE.md            # Global instructions template
└── LICENSE              # MIT license
```

---

## License

MIT License - See [LICENSE](LICENSE) file.
