# Commands Overview

The toolkit ships **15 commands** organized into three categories: **Core** (development workflows), **Session Management** (context preservation), and **Git Workflow** (version control).

> **v1.3.0 — refined release.** The command surface was cleaned up so that every entry earns its slot. The three near-identical `/haiku` + `/opus` + `/sonnet` commands collapsed into a single `/haiku [--model …]` meta command. Commands that depended on fragile external setup (`/review`, `/rlm`, `/gherkin`) and the redundant `/plan` + `/just-bash` wrappers were retired. Nothing else was cut.

## Quick Reference

| Command | Description | Category |
|---------|-------------|----------|
| [/setup](setup.md) | Bootstrap CLIs, memory index, handbook, git hooks, CLAUDE.md | Core |
| [/haiku](haiku.md) | 10-agent team — `--model haiku\|sonnet\|opus` (default haiku) | Core |
| [/team](team.md) | Multi-agent parallel implementation (external CLIs) | Core |
| [/kiro](kiro.md) | Spec-driven development with Kiro methodology | Core |
| [/handbook](handbook.md) | Refresh AI-optimized project handbook | Core |
| [/code2course](../../plugins/toolkit/commands/code2course.md) | Turn a codebase into an interactive HTML course | Core |
| [/@implement](implement.md) | Process `@implement` comments | Core |
| [/design](design.md) | Interactive design-token pipeline | Core |
| [/agent-memory](agent-memory.md) | Hybrid search + CRUD for the memory CLI | Core |
| [/compact](compact.md) | Memory-aware session compact (daily log + state) | Session |
| [/compact-min](compact.md#compact-min) | Ultra-minimal session compact (fast, no memory) | Session |
| [/restore](restore.md) | Restore session with daily log bootstrap | Session |
| [/worktree](worktree.md) | Create isolated worktree (auto wip branch) | Git |
| [/save](save.md) | Commit, merge, cleanup worktree | Git |
| [/stable](stable.md) | Create stable checkpoint (tag + branch) | Git |

---

## Core Commands

Commands for bootstrap, feature development, documentation, and search.

### Bootstrap

- **[/setup](setup.md)** — Self-bootstrapping entry point. Detects and installs missing external CLIs (`agent-memory`, `agent-viewer`), indexes the codebase, seeds `HANDBOOK.md`, installs post-commit/post-merge git hooks that keep the handbook fresh, and writes a project `CLAUDE.md` encoding the cohesion rules. Idempotent.

### Multi-Agent Coordination

- **[/haiku](haiku.md)** — Spawn a team of 10 agents orchestrated by Opus. Uses a phased approach: context gathering → decomposition → implementation → validation → synthesis. The tier of the spawned agents is controlled by `--model`:

  ```bash
  /haiku analyze the auth module                # haiku (default)
  /haiku --model sonnet refactor payments        # sonnet
  /haiku --model opus design an event pipeline   # opus
  ```

- **[/team](team.md)** — Coordinate multiple external-CLI agents (`gemini`, `cursor`, `codex`, `droid`, `opencode`) to implement features in parallel. Automatically decomposes tasks and assigns them to appropriate agents.

### Documentation

- **[/handbook](handbook.md)** — Refresh `HANDBOOK.md` with four layers: System Overview, Module Map, Integration Guide, Extension Points. `/setup` seeds it on first run; git hooks keep it fresh automatically after every commit/merge.

- **[/@implement](implement.md)** — Find `@implement` comments in code, implement the requested functionality, and convert the comments into proper documentation.

### Spec-Driven Development

- **[/kiro](kiro.md)** — Generate EARS-format requirements, design docs, and task breakdowns through interactive Q&A phases. Each phase is reviewed through `agent-viewer spec` (editable browser) before moving forward. Execution uses parallel agents (Cursor default, Haiku optional).

### Design Systems

- **[/design](design.md)** — Interactive design-token pipeline. Gathers brand preferences through Q&A, generates semantic tokens (`brand-*`, `content-*`, `surface-*`) with Tailwind integration and optional CSS/SCSS/iOS/Android outputs.

### Education

- **/code2course** — Transforms any codebase into a stunning single-page HTML course with scroll-based modules, animated visualizations, embedded quizzes, and plain-English code explanations. Backed by the bundled `codebase-to-course` skill (see [skills](../skills/README.md)).

### Memory & Search

- **[/agent-memory](agent-memory.md)** — Dispatcher for the local `agent-memory` CLI. Search across all memory files (MEMORY.md, daily logs, session snapshots) using hybrid vector + BM25 search, or manage entries (add/get/list).

---

## Session Management

Commands for preserving context across `/clear` operations.

- **[/compact](compact.md)** — Memory-aware session compact. Writes a daily log entry to `~/.claude/agent-memory/daily-logs/`, saves session state to `.context/session-state.json`, and optionally updates `MEMORY.md` with stable facts.

- **[/compact-min](compact.md#compact-min)** — Ultra-minimal session compact. Writes only `.context/session-state.json` with no memory system writes. Faster when you just need a quick checkpoint.

- **[/restore](restore.md)** — Restore session from saved state and immediately continue working. Bootstraps context from today's and yesterday's daily logs.

**Workflow:**
```bash
/compact      # Save state + write daily log
/clear        # Clear context
/restore      # Resume with daily log context
```

For a faster checkpoint without memory writes: `/compact-min`.

**Heads up:** the memory-cycle hook also writes daily logs and session snapshots automatically during every native compaction — you do not have to call `/compact` manually for that to happen. Use the explicit commands when you want richer logs or immediate checkpointing.

---

## Retired in 1.3.0 (for reference)

These commands were removed because they duplicated functionality or depended on fragile external setup. Their responsibilities live elsewhere now:

| Retired | Replacement |
|---------|-------------|
| `/plan` | The `agent-viewer` skill auto-triggers in plan mode — see [skills/agent-viewer](../skills/agent-viewer.md) |
| `/opus`, `/sonnet` | `/haiku --model opus` / `/haiku --model sonnet` |
| `/review` | Run CodeRabbit manually (the automated wrapper was fragile) |
| `/rlm` | Use a subagent with large context directly |
| `/gherkin` | Generate specs through `/kiro` |
| `/just-bash` | Use Bash directly; the `just-bash` skill was also retired |

---

## Git Workflow

Commands for isolated development using git worktrees.

- **[/worktree](worktree.md)** — Create isolated worktree with auto-generated branch (`wip-YYYYMMDD-HHMMSS`). Runs dependency install and optional editor launch.

- **[/save](save.md)** — Commit all changes, merge WIP branch to main, and clean up the worktree and branch. Handles merge conflicts interactively via `AskUserQuestion`.

- **[/stable](stable.md)** — Create a stable checkpoint with an annotated tag, checkpoint branch, and documentation.

**Workflow:**
```bash
/setup      # Once per project — bootstraps everything
/worktree   # Create isolated worktree (auto wip branch)
# ... develop ...
/save       # Merge back to main
/stable     # Optional: create stable checkpoint
```
