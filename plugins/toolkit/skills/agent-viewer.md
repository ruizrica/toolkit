---
name: agent-viewer
description: >
  Use this skill any time Claude is about to write or present an implementation plan,
  show a Mermaid/graph/architecture diagram, generate a spec set, or deliver a
  completion/summary report. The skill wraps the `agent-viewer` CLI to open an
  editable browser review, collect edits, and only proceed once the user approves.
  TRIGGER when: plan mode is active; a plan file has just been written; the user
  asks for a diagram, architecture overview, or visual summary; Kiro spec documents
  are ready for review; or a work-completion summary is about to be presented.
---

# agent-viewer — The Round-Trip Review Skill

`agent-viewer` is the canonical mechanism for any round-trip review — plans, specs, completion reports, diagrams, and historical report indexes. It replaces ad-hoc "print a plan and hope the user reads it" workflows with an editable browser UI that returns a machine-readable decision.

This skill is the **single contract** for every viewer-backed interaction in the toolkit. `/kiro` uses it for specs. Plan-mode workflows use it for plans. Completion summaries use it for closeouts.

## When to invoke

Run the viewer **before** proceeding in any of these situations:

1. **Plan mode is active** — you've written an implementation plan to disk (`.context/todo.md`, `~/.claude/plans/<slug>.md`, or similar). Must be approved before exiting plan mode.
2. **A plan/spec file has just been written or revised** — same as above, regardless of plan mode state.
3. **The user asks for a diagram** — architecture overview, sequence diagram, Mermaid graph. Render the diagram into a markdown file with a fenced ```mermaid block and show it via `agent-viewer plan` so the user can edit the source.
4. **Kiro spec documents are ready** — the 3-document set (requirements / design / tasks) is presented via `agent-viewer spec` with the multi-document `documents[]` payload shape.
5. **Work is complete and ready to summarize** — build a rich completion payload (summary + Mermaid diagram + task checklist + file diffs) and present via `agent-viewer completion`.
6. **Browsing historical reports** — past plans, specs, and completions are indexed and browsable via `agent-viewer reports`.

## Prerequisites

The `agent-viewer` CLI must be on PATH. One-time install:

```bash
bash plugins/toolkit/scripts/install-agent-viewer.sh
```

Verify:

```bash
agent-viewer --help
```

If install fails, run `/setup` — it detects missing dependencies and installs them.

## Mandatory Workflow

### 1. Choose a report type

| Type | Command | When |
|------|---------|------|
| `plan` | `agent-viewer plan --file <file>.md --json` or `--stdin --json` | Single-document plan review, diagram presentation |
| `spec` | `agent-viewer spec --folder <dir> --json` | Multi-document spec set (Kiro requirements/design/tasks) |
| `completion` | `agent-viewer completion --file <file>.json --json` | Work-complete summary with diffs, tasks, Mermaid |
| `reports` | `agent-viewer reports --dir <dir> --json` | Browse historical reports index |

### 2. Build the payload — use rich shapes, not minimal ones

The payload MUST follow the canonical shapes in `plugins/toolkit/templates/agent-viewer/` (mirrors the sibling agent-viewer repo's `examples/`). Do **not** send bare markdown when the richer shape applies.

#### plan-payload.json
```json
{
  "title": "Implementation Plan",
  "filePath": "./examples/sample-plan.md",
  "markdown": "# Plan: …\n\n## Context\n\n…\n\n## Phase 1\n\n- step\n- step"
}
```

#### spec-payload.json
```json
{
  "title": "Sample Auth Spec",
  "folderPath": "./examples/sample-spec",
  "documents": [
    { "filePath": "requirements.md", "label": "Requirements", "markdown": "…" },
    { "filePath": "design.md",       "label": "Design",       "markdown": "…```mermaid\ngraph LR\n  A --> B\n```" },
    { "filePath": "tasks.md",        "label": "Tasks",        "markdown": "- [ ] task 1\n- [ ] task 2" }
  ]
}
```

#### completion-payload.json (rich — required for completion reports)
```json
{
  "title": "Feature Complete — <name>",
  "summary": "# Summary\n\n…\n\n```mermaid\ngraph LR\n  A[Before] --> B[After]\n```",
  "baseRef": "HEAD",
  "totalAdditions": 120,
  "totalDeletions": 24,
  "taskMarkdown": "- [x] done 1\n- [x] done 2\n- [ ] follow-up",
  "files": [
    { "path": "…", "status": "modified", "additions": 40, "deletions": 8, "diff": "@@ …" },
    { "path": "…", "status": "added",    "additions": 80, "deletions": 0, "diff": "@@ …" }
  ]
}
```

#### reports-payload.json
```json
{
  "reportType": "reports",
  "title": "Reports Index",
  "entries": [
    {
      "id": "plan-1",
      "category": "plan",
      "title": "…",
      "summary": "…",
      "updatedAt": "ISO-8601 timestamp",
      "sourceLabel": "…",
      "searchText": "…"
    }
  ]
}
```

### 3. Invoke the CLI

Two invocation styles:

- **File-backed** (preferred for plans/specs so edits persist to disk):
  ```bash
  agent-viewer plan --file .context/todo.md --json
  agent-viewer spec --folder ~/.claude/plans/my-spec --json
  ```
- **Payload via stdin** (preferred for computed payloads like completion reports):
  ```bash
  cat completion.json | agent-viewer completion --stdin --json
  ```

### 4. Parse the result

The CLI emits JSON on stdout:

```json
{
  "reviewId": "plan-1776065617387",
  "lastAction": "approved",
  "updatedAt": "2026-04-13T07:33:53.598Z",
  "comments": []
}
```

`lastAction` will be one of:
- `approved` — proceed with the planned work
- `changes_requested` — read edits/comments, revise the source file, re-invoke
- `declined` — revise based on comments, re-invoke

### 5. Loop until approved

Do **not** proceed to implementation until the result is `approved`. Every round trip is normal and expected — the viewer is designed for back-and-forth review.

## Plan-Mode Integration

When plan mode is active (or you've just written a plan file):

1. Write the plan to `.context/todo.md` (default) or `~/.claude/plans/<slug>.md`.
2. `agent-viewer plan --file <path> --json`
3. Parse `lastAction`. Loop until `approved`.
4. Only then call `ExitPlanMode` (if in plan mode) or begin implementation.

This replaces the old `/plan` command — that command has been removed in favor of this skill being the automatic plan-mode hook.

## Diagram / Graph Integration

When the user asks for a diagram or architecture view:

1. Render the diagram as a markdown file with one or more fenced ```mermaid blocks.
2. Present via `agent-viewer plan --file <file>.md --json` (or embed as `summary` in a completion payload).
3. The viewer natively renders Mermaid — the user can edit the source and re-approve.

## Critical Rules

1. **Never skip the viewer** because the plan/spec "looks good enough."
2. **Never send bare markdown when the richer shape applies.** Completion reports with diffs MUST use the full `completion-payload.json` shape, not a plain summary.
3. **Never assume hooks will auto-launch this.** Invoke the CLI explicitly.
4. **Re-running is expected** — that is how review works.
5. **Treat the CLI output as source of truth** for the review round. User edits in the browser overwrite the file on disk.

## Quick Reference

```bash
# Help
agent-viewer --help
agent-viewer plan --help
agent-viewer spec --help
agent-viewer completion --help
agent-viewer reports --help

# Common invocations
agent-viewer plan --file .context/todo.md --json
agent-viewer spec --folder ~/.claude/plans/<spec> --json
cat completion.json | agent-viewer completion --stdin --json
agent-viewer reports --dir ~/.claude/plans --json
```

## JSON payload templates

Canonical shapes are stored at:

```text
plugins/toolkit/templates/agent-viewer/plan-payload.json
plugins/toolkit/templates/agent-viewer/spec-payload.json
plugins/toolkit/templates/agent-viewer/completion-payload.json
plugins/toolkit/templates/agent-viewer/reports-payload.json
```

Always build payloads by starting from these templates; do not invent fields.
