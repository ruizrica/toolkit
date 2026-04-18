# agent-viewer

ABOUTME: Documentation for the agent-viewer skill — round-trip plan/spec/completion/reports review.
ABOUTME: Covers trigger conditions, workflow, rich payload shapes, and prerequisites.

## What is it?

`agent-viewer` is the toolkit's single round-trip review skill. It wraps the external `agent-viewer` CLI to open an editable browser UI for any plan, spec, completion report, or diagram, collects the user's edits and approval decision, and returns a machine-readable result.

It replaces the old `/plan` command — instead of a separate slash command, the skill activates automatically whenever the trigger conditions match.

## When it triggers

The skill auto-activates when:

- **Plan mode is active** — any time Claude is writing or revising an implementation plan
- **A plan file has just been written** — `.context/todo.md`, `~/.claude/plans/<slug>.md`, or similar
- **The user asks for a diagram** — architecture overview, Mermaid graph, sequence diagram
- **Kiro spec documents are ready for review** — the 3-document set (requirements, design, tasks)
- **A work-completion summary is about to be presented** — rich payload with diffs, tasks, Mermaid

## Prerequisites

The `agent-viewer` CLI must be on PATH. One-time install:

```bash
bash plugins/toolkit/scripts/install-agent-viewer.sh
```

Or, simpler: run `/setup` — it installs `agent-viewer` (and `agent-memory`) automatically.

Verify:

```bash
agent-viewer --help
```

## The Four Report Types

| Type | Command | Payload shape | Use |
|------|---------|---------------|-----|
| `plan` | `agent-viewer plan --file <file>.md --json` | `plan-payload.json` | Single-document plan review, diagram presentation |
| `spec` | `agent-viewer spec --folder <dir> --json` | `spec-payload.json` | Multi-document spec set (Kiro) |
| `completion` | `cat payload.json \| agent-viewer completion --stdin --json` | `completion-payload.json` | Work-complete summary with diffs, tasks, Mermaid |
| `reports` | `agent-viewer reports --dir <dir> --json` | `reports-payload.json` | Browse historical reports index |

Canonical payload templates live at `plugins/toolkit/templates/agent-viewer/`. **Use the rich shape — do not send bare markdown when the richer shape applies.**

## Workflow

1. **Write / update the source** — markdown file(s) on disk, or build a JSON payload matching the template shape.
2. **Invoke the CLI** — `agent-viewer plan|spec|completion|reports …`.
3. **Parse the JSON result** — fields `reviewId`, `lastAction` (`approved` / `changes_requested` / `declined`), `comments`, edited markdown.
4. **Loop:**
   - `approved` → proceed with implementation
   - `changes_requested` → read edits/comments, revise, re-invoke
   - `declined` → revise, re-invoke

Do **not** proceed to implementation until the result is `approved`.

## Skill File Location

Installed to `~/.claude/skills/agent-viewer.md` via the plugin. Source lives in `plugins/toolkit/skills/agent-viewer.md`.

## See Also

- [Kiro command](../commands/kiro.md) — Uses the skill for spec review at each phase
- [agent-memory](agent-memory.md) — Local hybrid search skill
- [agent-viewer source repo](https://github.com/ruizrica/agent-viewer) — CLI implementation and examples
