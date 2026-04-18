<p align="center">
  <img src="assets/toolkit.png" alt="Toolkit" width="400">
</p>

<p align="center">
  <strong>A cohesive Claude Code plugin — multi-agent orchestration, round-trip plan/spec/completion review, hybrid memory search, and an auto-refreshing project handbook.</strong>
</p>

<p align="center">
  <sub><b>v1.3.5</b> — interactive commands (<code>/agent-plan</code>, <code>/agent-spec</code>, <code>/kiro</code>, <code>/design</code>) now run in the main conversation so <code>AskUserQuestion</code> works natively instead of silently falling back to inline markdown Q&A.</sub>
</p>

---

## What's new in 1.3.5

- **Interactive commands get real `AskUserQuestion` popups.** `/agent-plan`, `/agent-spec`, `/kiro`, and `/design` previously declared `AskUserQuestion` in `allowed-tools` but ran under `context: fork`, which spawns a subagent where that tool isn't available — so Q&A silently degraded to inline markdown. Fix drops the fork on all four; `/design` gains `model: opus` to preserve Opus pinning. Heavy work (Repo Scout, execution teams) still delegates via the `Task` tool.

## What's new in 1.3.0

This release is a **cleanup pass** that makes the toolkit act as one cohesive system instead of a bag of independent commands. Nothing useful was lost — duplicates and dead weight were consolidated.

- **Single meta command** — `/haiku`, `/opus`, `/sonnet` collapsed into one `/haiku [--model haiku|sonnet|opus] <task>` (haiku by default). Same behavior, one file to maintain.
- **Bundled installers** — `agent-viewer` and `agent-memory` CLIs install automatically via `/setup`. No manual copy steps.
- **Self-bootstrapping `/setup`** — detects missing CLIs, indexes memory, seeds `HANDBOOK.md`, installs git hooks that auto-refresh the handbook on every commit/merge, writes a `CLAUDE.md` with the cohesion rules.
- **Round-trip review everywhere** — plans, specs, completion reports, and diagrams all flow through the `agent-viewer` skill. Canonical rich JSON payload shapes live in `plugins/toolkit/templates/agent-viewer/`.
- **Bundled skills** — `codebase-to-course` now ships with the toolkit (no separate install).
- **Pruned** — retired commands/agents that duplicated functionality or required fragile external setup: `/review`, `/rlm`, `/gherkin`, `/just-bash`, `/plan`, plus 4 overlapping agents (`crush`, `groq`, `qwen`, `rlm-subcall`).

See [`CHANGELOG`](plugins/toolkit/.claude-plugin/plugin.json) for the full manifest.

---

## Installation

```bash
# One-line install (recommended)
curl -fsSL https://raw.githubusercontent.com/ruizrica/toolkit/main/install.sh | bash
```

This clones to `~/.toolkit`, registers the plugin, installs scripts and skills, and creates agent-memory directories under `~/.claude/agent-memory/`.

### Manual Install

```bash
git clone https://github.com/ruizrica/agent-toolkit.git
claude plugins add ./agent-toolkit/plugins/toolkit
```

Then inside any project:

```bash
/setup
```

`/setup` detects and installs the two external CLIs (`agent-viewer`, `agent-memory`), indexes the codebase, generates `HANDBOOK.md`, installs post-commit/post-merge git hooks that keep the handbook fresh, and writes a `CLAUDE.md` that encodes the cohesion rules. Idempotent — re-run anytime to refresh.

---

## Quick Start

### Multi-Agent Development
```bash
/haiku Implement user authentication with OAuth support
# Or escalate the tier for complex work:
/haiku --model opus Redesign the distributed event pipeline
```
Spawns 10 tier-specific agents managed by Opus. Haiku is the default; `--model sonnet|opus` overrides.

### External-CLI Team
```bash
/team Build a payment integration across the frontend and backend
```
Dispatches to specialized external-CLI agents (`gemini`, `cursor`, `codex`, `droid`, `opencode`) in parallel.

### Session Continuity
```bash
/compact      # Save state + write daily log
/clear        # Clear context
/restore      # Resume with daily log context
```
Writes to `~/.claude/agent-memory/` with daily logs, session snapshots, and MEMORY.md. Compaction is driven by the memory-cycle hook — snapshots and state are captured automatically. Use `/compact-min` when you just need a fast state checkpoint.

### Spec-Driven Development (Kiro)
```bash
/kiro Add user authentication with OAuth
```
Generates EARS-format requirements, design docs, and task breakdowns. Each phase is reviewed through `agent-viewer spec` (editable browser UI) before execution.

### Plans, Specs, Diagrams — Review via agent-viewer
Any time you write a plan, generate a spec set, present a Mermaid diagram, or close out a task with a completion summary, the `agent-viewer` skill opens the content in an editable browser viewer and waits for approval. It replaces the old `/plan` command — now it's an automatic skill that triggers whenever plan mode is active or a plan file is on disk.

### Git Worktree Workflow
```bash
/setup      # Bootstrap the project (once)
/worktree   # Create isolated worktree (auto wip branch)
# ... develop ...
/save       # Merge back to main + cleanup
```

### On-Demand Handbook
```bash
/handbook   # Refresh HANDBOOK.md
```
`/setup` seeds `HANDBOOK.md` on first run; git hooks keep it fresh automatically after every commit/merge. Use `/handbook` when you want an on-demand refresh or custom flags.

---

## Documentation

| Section | Description |
|---------|-------------|
| [Commands](docs/commands/README.md) | All 15 commands with usage and examples |
| [Agents](docs/agents/README.md) | All 5 specialized external-CLI agents |
| [Skills](docs/skills/README.md) | Skill reference files (agent-viewer, agent-memory, autoresearch, codebase-to-course) |

---

## Commands at a Glance

### Core

| Command | Description | Docs |
|---------|-------------|------|
| `/setup` | Bootstrap: install CLIs, index memory, seed handbook, install git hooks, write CLAUDE.md | [→](docs/commands/setup.md) |
| `/haiku [--model …]` | 10-agent team managed by Opus (haiku default; `--model sonnet\|opus` to override) | [→](docs/commands/haiku.md) |
| `/team` | Multi-agent parallel implementation with external CLIs | [→](docs/commands/team.md) |
| `/agent-plan` | Interactive single-doc plan — Q&A → viewer gate → execute → completion report | [→](docs/commands/agent-plan.md) |
| `/agent-spec` | Interactive Kiro-pattern spec — requirements/design/tasks → viewer gate → execute | [→](docs/commands/agent-spec.md) |
| `/kiro` | Same workflow as `/agent-spec` (legacy name) | [→](docs/commands/kiro.md) |
| `/handbook` | Refresh AI-optimized project handbook | [→](docs/commands/handbook.md) |
| `/code2course` | Turn a codebase into an interactive HTML course | — |
| `/@implement` | Process `@implement` comments in code | [→](docs/commands/implement.md) |
| `/design` | Interactive design-token pipeline | [→](docs/commands/design.md) |
| `/agent-memory` | Hybrid search + CRUD dispatcher for the memory CLI | [→](docs/commands/agent-memory.md) |

### Session & Git

| Command | Description | Docs |
|---------|-------------|------|
| `/compact` | Memory-aware session compact | [→](docs/commands/compact.md) |
| `/compact-min` | Ultra-minimal session snapshot (fast, no memory writes) | [→](docs/commands/compact.md#compact-min) |
| `/restore` | Restore after `/clear` (loads daily logs + session state) | [→](docs/commands/restore.md) |
| `/worktree` | Create isolated worktree (auto wip branch) | [→](docs/commands/worktree.md) |
| `/save` | Commit, merge, cleanup worktree | [→](docs/commands/save.md) |
| `/stable` | Create stable checkpoint tag + branch | [→](docs/commands/stable.md) |

---

## Agents at a Glance

| Agent | Specialty | Docs |
|-------|-----------|------|
| **gemini-agent** | Large codebase analysis (1M tokens), Google Search | [→](docs/agents/gemini.md) |
| **cursor-agent** | Code review, refactoring, sessions | [→](docs/agents/cursor.md) |
| **codex-agent** | Natural language → code, translation | [→](docs/agents/codex.md) |
| **droid-agent** | Enterprise development, Jira/Notion | [→](docs/agents/droid.md) |
| **opencode-agent** | 75+ AI models via OpenRouter | [→](docs/agents/opencode.md) |

Invoke any agent as a slash command: `/toolkit:gemini-agent Analyze the auth module`.

---

## Skills

Skills are reference files installed to `~/.claude/skills/` that teach Claude when and how to use specific tools. Unlike commands (which you invoke) or agents (which you dispatch), skills activate automatically when their trigger conditions match.

| Skill | Description | Docs |
|-------|-------------|------|
| **agent-viewer** | Round-trip review loop (plans, specs, completions, reports, diagrams) — auto-triggers in plan mode | [→](docs/skills/agent-viewer.md) |
| **agent-memory** | Local hybrid search (vector + BM25) over all memory files | [→](docs/skills/agent-memory.md) |
| **autoresearch** | Autonomous goal-directed iteration (Karpathy's autoresearch pattern) | [→](docs/skills/autoresearch.md) |
| **codebase-to-course** | Generate interactive single-page HTML course from a codebase | [→](docs/skills/codebase-to-course.md) |

---

## External CLIs

Two external CLIs back the skills that make this cohesive. `/setup` installs both; you can also run the installers directly.

| CLI | Purpose | Installer |
|-----|---------|-----------|
| `agent-viewer` | Editable browser review for plans, specs, completions, reports | `scripts/install-agent-viewer.sh` |
| `agent-memory` | Hybrid semantic + BM25 search over memory and daily logs | `scripts/install-agent-memory.sh` |

Source repos (both ship inside the plugin cache):
- **agent-viewer** — bundled at `plugins/toolkit/tools/agent-viewer/`
- **agent-memory** — bundled at `plugins/toolkit/tools/agent-memory/`

Canonical JSON payload shapes for `agent-viewer` live at `plugins/toolkit/templates/agent-viewer/`:
- `plan-payload.json` — single-document plan review
- `spec-payload.json` — multi-document spec (Kiro)
- `completion-payload.json` — rich completion summary with Mermaid, diffs, task checklist
- `reports-payload.json` — historical reports index

---

## Statusline

The installer configures a Claude Code status line showing model, context usage, and working directory:

```
opus | 67% | Github-Work/commander
```

Context percentage is color-coded: gray (<40%), green (40–59%), yellow (60–79%), red (80–94%), bright red (95%+).

To install standalone: `bash ~/.toolkit/plugins/toolkit/scripts/install-statusline.sh`

---

## Agent Memory System

The toolkit pairs project-local memory (`.context/`) with global memory (`~/.claude/agent-memory/`).

| Memory Type | Location | Written By |
|-------------|----------|------------|
| **Semantic** | `.context/MEMORY.md` | Edited manually or via `/compact` (stable facts only) |
| **Daily Logs** | `~/.claude/agent-memory/daily-logs/YYYY-MM-DD.md` | memory-cycle hook + `/compact` |
| **Session State** | `.context/session-state.json` | `/compact`, `/compact-min` |
| **Session Snapshots** | `~/.claude/agent-memory/sessions/{project}-{ts}.md` | memory-cycle hook (automatic) |

**How it works:**
- The memory-cycle hook writes daily logs and session snapshots automatically on every compaction.
- `/compact` lets you append a richer daily log entry and optionally update MEMORY.md.
- `/restore` reads today's and yesterday's logs plus `session-state.json` to bootstrap cross-session context.
- `MEMORY.md` is auto-loaded every session — stable facts persist without explicit restore.

**Searching memories:**
```bash
agent-memory search "what embedding model?"   # Hybrid (vector + BM25)
agent-memory search "TDD" --keyword           # Exact keyword match
agent-memory index                            # Reindex all memory files
agent-memory add "always use bun" --source daily
agent-memory get <id-or-prefix>
```

**Code navigation** (tree-sitter AST, 165+ languages):
```bash
agent-memory code-index ./src
agent-memory code-nav "authentication"
agent-memory code-tree
agent-memory code-summarize
agent-memory code-refs 42
```

---

## Requirements

### Core
- Claude Code 2.1+
- Python 3.8+ (for `/handbook` and `/setup` scripts)
- Node.js 20+ (for the `agent-viewer` CLI)

### Installed automatically by `/setup`
- **agent-viewer** — editable browser review CLI
- **agent-memory** — hybrid search CLI + embedding model (~67 MB)

Both can also be installed on demand via `scripts/install-agent-viewer.sh` and `scripts/install-agent-memory.sh`.

---

## Directory Structure

```
agent-toolkit/
├── plugins/toolkit/
│   ├── agents/                       # 5 specialized external-CLI agents
│   ├── commands/                     # 15 commands
│   ├── skills/                       # 4 skills (1 directory-style: codebase-to-course)
│   ├── scripts/                      # installers, handbook generator, doctor, statusline
│   ├── templates/agent-viewer/       # canonical rich JSON payload shapes
│   └── .claude-plugin/plugin.json    # manifest (v1.3.5)
├── docs/                             # Per-command / per-agent / per-skill documentation
├── tools/agent-memory/               # Hybrid search CLI (Python)
├── assets/                           # Images
├── CLAUDE.md                         # Global instructions + orchestration manifest
└── LICENSE                           # MIT
```

---

## License

MIT License — see [LICENSE](LICENSE).
