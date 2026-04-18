# Skills Overview

ABOUTME: Overview documentation for toolkit skill files.
ABOUTME: Explains what skills are and lists all available skills.

Skills are reference files the Claude Code harness auto-loads based on context. Unlike commands (which you invoke) or agents (subagent types), skills activate passively when their trigger conditions match — Claude reads the skill and follows its guidance.

> **v1.3.0 — refined release.** The skill roster was refocused around the cohesive toolkit workflow: `agent-viewer` is now the canonical round-trip review skill (it replaces the old `/plan` command), `codebase-to-course` is bundled directly, and `just-bash` was retired. `agent-memory` and `autoresearch` are unchanged.

## Available Skills

| Skill | CLI / Tool | Description |
|-------|------------|-------------|
| [agent-viewer](agent-viewer.md) | `agent-viewer` | Round-trip review for plans, specs, completions, reports, diagrams — auto-triggers in plan mode |
| [agent-memory](agent-memory.md) | `agent-memory` | Local hybrid search (vector + BM25) over all memory files |
| [autoresearch](autoresearch.md) | git + a verify command | Autonomous goal-directed iteration (modify → verify → keep/discard → repeat) |
| [codebase-to-course](codebase-to-course.md) | (no external CLI) | Generate a beautiful interactive single-page HTML course from a codebase |

### agent-viewer — the plan/spec/completion review loop

`agent-viewer` is how the toolkit enforces human-in-the-loop review on plans, specs, completion reports, and diagrams. Whenever Claude writes a plan, generates a Kiro spec set, presents a Mermaid graph, or wraps up a task, the skill routes the content through an editable browser viewer and waits for `approved` before proceeding.

The skill defines the canonical rich JSON payload shapes for each report type. Templates live at `plugins/toolkit/templates/agent-viewer/`.

### codebase-to-course — bundled directory-style skill

Unlike the other skills (single `.md` files), `codebase-to-course` is a directory containing `SKILL.md` plus `references/design-system.md` and `references/interactive-elements.md`. It ships with the toolkit — no external install needed.

## How Skills Work

1. The plugin manifest registers each skill under `skills/`.
2. Claude Code loads the skill file (or directory) into its skill index at session start.
3. When the user's request matches a skill's trigger description, Claude activates the skill and follows its documented workflow.

## Installation

Skills are installed automatically by the toolkit plugin. No manual copy step is needed when the plugin is registered via `claude plugins add`.

For skills that wrap an external CLI (`agent-viewer`, `agent-memory`), run `/setup` once — it installs the CLIs and wires everything together.
