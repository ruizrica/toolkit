# Toolkit · v1.3.2

A cohesive Claude Code plugin. Multi-agent orchestration, round-trip plan/spec/completion review via `agent-viewer`, hybrid semantic memory via `agent-memory`, and an auto-refreshing project handbook.

Every piece knows about the others. Run `/setup` once and the toolkit wires itself together.

> **v1.3.0 is a refined release.** The command surface was cleaned up, duplicates were consolidated, and every remaining command earns its slot. Highlights: `/haiku` is now a single meta command with `--model haiku|sonnet|opus`; the vendored plan-viewer script was replaced by the external `agent-viewer` CLI with an installer; `/setup` now bootstraps the entire dependency chain end-to-end. See the root `README.md` for the full "What's new" list.

## Installation

```bash
claude plugins add ./plugins/toolkit
```

Then inside any project:

```bash
/setup
```

`/setup` detects missing dependencies (`agent-memory`, `agent-viewer`), installs them, indexes the codebase, generates `HANDBOOK.md`, installs git hooks that keep it fresh, and writes a `CLAUDE.md` with the orchestration manifest.

## External CLI dependencies

| CLI | Purpose | Installer |
|-----|---------|-----------|
| `agent-viewer` | Editable browser review for plans, specs, completions, reports | `scripts/install-agent-viewer.sh` |
| `agent-memory` | Hybrid semantic + BM25 search over memory and daily logs | `scripts/install-agent-memory.sh` |

Both installers are idempotent. `/setup` invokes them automatically; you can also run them directly.

Source repos (bundled inside this plugin):
- agent-viewer — `plugins/toolkit/tools/agent-viewer/` (override: `AGENT_VIEWER_SRC`)
- agent-memory — `plugins/toolkit/tools/agent-memory/` (override: `AGENT_MEMORY_SRC`)

## Contents

### Agents (5)

| Agent | Specialty |
|-------|-----------|
| gemini-agent | Large codebase analysis (1M tokens), Google Search |
| cursor-agent | Advanced code review, refactoring, sessions |
| codex-agent | Natural language to code, multi-language |
| droid-agent | Enterprise code generation, codebase analysis |
| opencode-agent | 75+ AI models via OpenRouter |

### Commands (15)

| Command | Description |
|---------|-------------|
| `/setup` | Bootstrap: install CLIs, index memory, seed handbook, install git hooks, write CLAUDE.md |
| `/haiku [--model haiku\|sonnet\|opus] <task>` | Spawn a team of 10 agents managed by Opus (haiku tier by default) |
| `/team <task>` | Coordinate mixed external-CLI agents (gemini, cursor, codex, droid, opencode) |
| `/kiro <feature>` | Spec-driven development: requirements → design → tasks → viewer review → execution |
| `/handbook` | Refresh `HANDBOOK.md` on demand (git hooks handle automatic updates) |
| `/code2course [path]` | Turn a codebase into an interactive HTML course |
| `/design [name]` | Interactive design-token pipeline (CSS/Tailwind/SCSS/iOS/Android) |
| `/@implement [target]` | Convert `@implement` comments to implementations + documentation |
| `/agent-memory <subcmd>` | Dispatcher for the `agent-memory` CLI (search, add, index, code-nav) |
| `/compact` | Memory-aware compaction (delegates to pi's native hook) |
| `/compact-min` | Ultra-minimal session snapshot |
| `/restore` | Restore session context after `/clear` or new session |
| `/worktree` | Create isolated git worktree with auto-generated wip branch |
| `/save [msg]` | Commit, merge WIP back to main, cleanup worktree |
| `/stable` | Tag a stable checkpoint and create a recovery branch |

### Skills (4)

| Skill | Description |
|-------|-------------|
| agent-viewer | Round-trip review loop for plans, specs, completions, reports, diagrams — triggers in plan mode and when visuals are needed |
| agent-memory | Local hybrid search (vector + BM25) for memory files and daily logs |
| autoresearch | Autonomous goal-directed iteration (Karpathy-style loop) |
| codebase-to-course | Generate interactive single-page HTML course from a codebase |

### Scripts (`scripts/`)

| Script | Purpose |
|--------|---------|
| `install-agent-viewer.sh` | Install the `agent-viewer` CLI |
| `install-agent-memory.sh` | Install the `agent-memory` CLI + embedding model |
| `install-git-hooks.sh` | Install post-commit/post-merge hooks that auto-refresh the handbook |
| `update-handbook.sh` | Called by the git hooks; regenerates `HANDBOOK.md` |
| `handbook.py` | Deterministic handbook generator (no LLM required) |
| `install-statusline.sh` | Install the status-line script for Claude Code |
| `doctor.sh` | Readiness check — reports whether every dependency is wired correctly |

### Templates (`templates/agent-viewer/`)

Canonical JSON payload shapes for the four `agent-viewer` report types:

- `plan-payload.json` — single-document plan review
- `spec-payload.json` — multi-document spec review (Kiro)
- `completion-payload.json` — rich completion summary with Mermaid, diffs, task checklist
- `reports-payload.json` — historical reports index

`skills/agent-viewer.md` enforces payloads match these shapes.

## Cohesion rules

These rules are written into the `CLAUDE.md` generated by `/setup`, so any agent working in a setup-initialized project follows them automatically:

1. **Handbook-first** — read the relevant layer of `HANDBOOK.md` for architecture/module questions.
2. **Memory-first** — query `agent-memory search` before reading files for "what did we decide / where is X" questions.
3. **Memory-write** — record significant decisions via `agent-memory add` (compaction auto-logs everything else).
4. **Plan-via-viewer** — plan mode + plan files go through `agent-viewer plan` and require approval.
5. **Spec-via-viewer** — Kiro's 3-document set goes through `agent-viewer spec` with the rich `documents[]` payload.
6. **Completion-via-viewer** — finished work produces a rich `completion-payload.json` shown via `agent-viewer completion`.
7. **Compact/restore loop** — new sessions auto-restore; long sessions auto-compact.

## License

MIT
