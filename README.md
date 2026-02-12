<p align="center">
  <img src="assets/toolkit.png" alt="Toolkit" width="400">
</p>

<p align="center">
  <strong>A Claude Code plugin with multi-agent orchestration, TDD workflows, and advanced productivity commands.</strong>
</p>

---

## Installation

```bash
# One-line install (recommended)
curl -fsSL https://raw.githubusercontent.com/ruizrica/toolkit/main/install.sh | bash
```

This clones to `~/.toolkit`, registers the plugin, installs scripts/skills, creates agent memory directories (`~/.claude/agent-memory/`), and installs optional tools (agent-browser, just-bash, agent-memory).

### Manual Install

```bash
git clone https://github.com/ruizrica/agent-toolkit.git
claude plugins add ./agent-toolkit/plugins/toolkit
mkdir -p ~/.claude/slash_commands
cp plugins/toolkit/scripts/handbook.py ~/.claude/slash_commands/
cp plugins/toolkit/scripts/coderabbit_workflow.py ~/.claude/slash_commands/
mkdir -p ~/.claude/agent-memory/{daily-logs,sessions,procedures}
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

### Session Continuity with Agent Memory
```bash
/compact      # Save state + write daily log
/clear        # Clear context
/restore      # Resume with daily log context
```
Uses a local memory system (`~/.claude/agent-memory/`) with daily logs, session snapshots, and semantic memory. The PreCompact hook automatically captures session snapshots; `/compact` writes a quality daily log entry; `/restore` bootstraps from today's and yesterday's logs.

For a faster, minimal compact without memory writes: `/compact-min`

### Spec-Driven Development
```bash
/kiro Add user authentication with OAuth
```
Generates requirements, design, and tasks using Kiro methodology, then executes with parallel agents.

### Sandboxed Bash (just-bash)

A sandboxed bash interpreter from [Vercel Labs](https://github.com/vercel-labs/just-bash) that lets Claude run commands safely with a read-only filesystem, no network access, and in-memory-only writes. Includes 75+ built-in commands (jq, yq, xan, sqlite3, rg, awk, sed, etc.).

```bash
# Explore a codebase safely (read-only, can't break anything)
just-bash -c 'find . -name "*.ts" | wc -l'

# Process JSON/CSV/YAML data
just-bash -c 'cat data.json | jq ".items[] | .name"'

# Test destructive scripts safely (writes stay in memory)
just-bash --allow-write -c 'rm -rf src && echo "nothing happened on disk"'
```

The toolkit installs a skill file (`~/.claude/skills/just-bash.md`) that teaches Claude when to use the sandbox vs regular Bash. See [docs](docs/skills/just-bash.md) for the full command list and usage patterns.

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
| [Commands](docs/commands/README.md) | All 15 commands with usage and examples |
| [Agents](docs/agents/README.md) | All 9 specialized agents with invocation patterns |
| [Skills](docs/skills/README.md) | Skill reference files for CLI tools |
| [Optional Commands](docs/optional/README.md) | MCP-dependent commands |

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
| `/kiro` | Spec-driven development with Kiro methodology | [→](docs/commands/kiro.md) |
| `/agent-memory` | Hybrid search over agent memory files | [→](docs/commands/agent-memory.md) |

### Session & Git

| Command | Description | Docs |
|---------|-------------|------|
| `/compact` | Memory-aware session compact (daily log + state) | [→](docs/commands/compact.md) |
| `/compact-min` | Ultra-minimal session compact (fast, no memory) | [→](docs/commands/compact.md#compact-min) |
| `/restore` | Restore after /clear (loads daily logs) | [→](docs/commands/restore.md) |
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

---

## Skills

Skills are reference files installed to `~/.claude/skills/` that teach Claude when and how to use specific CLI tools.

| Skill | Description | Docs |
|-------|-------------|------|
| **just-bash** | Sandboxed bash (read-only FS, no network, 75+ commands) | [→](docs/skills/just-bash.md) |
| **agent-memory** | Local hybrid search over agent memory files | [→](docs/skills/agent-memory.md) |

### Using Agents

Invoke any agent as a slash command:

```bash
/toolkit:gemini-agent Analyze the authentication module for security issues
```

---

## Agent Memory System

The toolkit includes a local memory system at `~/.claude/agent-memory/` that provides continuity across sessions.

| Memory Type | Location | Written By |
|-------------|----------|------------|
| **Semantic** | `~/.claude/projects/{key}/memory/MEMORY.md` | `/compact` (stable facts only) |
| **Daily Logs** | `~/.claude/agent-memory/daily-logs/YYYY-MM-DD.md` | `/compact` + PreCompact hook |
| **Session Snapshots** | `~/.claude/agent-memory/sessions/{project}-{ts}.md` | PreCompact hook (automatic) |
| **Procedural** | `~/.claude/agent-memory/procedures/` | Reserved for future use |

**How it works:**
- `/compact` introspects the session, writes a quality daily log entry, saves session state, and optionally updates MEMORY.md with stable facts
- The PreCompact hook automatically writes raw session snapshots and daily log entries on every compaction
- `/restore` reads today's and yesterday's daily logs to bootstrap cross-session context
- MEMORY.md is auto-loaded by Claude Code every session — stable facts persist without explicit restore

**Searching memories:**
```bash
agent-memory search "what embedding model?"   # Hybrid search (vector + BM25)
agent-memory search "TDD" --keyword           # Exact keyword match
agent-memory index                            # Reindex all memory files
```

See [/compact docs](docs/commands/compact.md) and [/restore docs](docs/commands/restore.md) for details.

---

## Requirements

### Core
- Claude Code 2.1+
- Python 3.8+ (for /handbook, /review, /rlm scripts)

### Optional
- **agent-browser** - For /gherkin visual analysis (`npm install -g agent-browser`)
- **just-bash** - Sandboxed bash for safe exploration (`npm install -g just-bash`)
- **agent-memory** - Hybrid search over memory files (`pip3 install -e ~/.toolkit/tools/agent-memory`)

---

## Directory Structure

```
agent-toolkit/
├── plugins/toolkit/
│   ├── agents/          # 9 specialized agents
│   ├── commands/        # 14 commands
│   ├── skills/          # Skill reference files
│   ├── scripts/         # Python scripts
│   └── optional/        # MCP-dependent commands
├── docs/
│   ├── commands/        # Command documentation
│   ├── agents/          # Agent documentation
│   ├── skills/          # Skill documentation
│   └── optional/        # MCP commands documentation
├── tools/
│   └── agent-memory/    # Hybrid search CLI (Python)
├── assets/              # Images
├── CLAUDE.md            # Global instructions template
└── LICENSE              # MIT license
```

---

## License

MIT License - See [LICENSE](LICENSE) file.
