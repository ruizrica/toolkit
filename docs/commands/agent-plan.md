# /agent-plan

Interactive single-document plan workflow. Gathers the full shape of a plan via `AskUserQuestion`, writes a maximally robust markdown plan, gates on `agent-viewer plan` approval, then executes in the same session and closes the loop with an auto-generated completion report.

Sister command to [`/agent-spec`](agent-spec.md), which is the multi-document (requirements/design/tasks) equivalent. Use `/agent-plan` when the work is a single coherent change; use `/agent-spec` when the feature needs requirements/design/tasks separation.

## Usage

```bash
/agent-plan [plan topic] [--name NAME] [--agent inline|haiku|sonnet|opus]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| plan topic | Yes | Plain-language description of the work |
| --name NAME | No | Plan name (defaults to `YYYY-MM-DD-<slug>`) |
| --agent inline\|haiku\|sonnet\|opus | No | Execution mode (default: `inline`) |

## Workflow Phases

The command runs 5 phases end-to-end:

### Phase 1 — Context

Spawns **one** Haiku scout agent that scans the repo for:
- Files/modules/functions relevant to the topic
- Existing patterns, conventions, test styles
- In-progress changes that might conflict

Lightweight by design — plans are single-document and smaller than specs, so one agent is enough.

### Phase 2 — Interactive Q&A

Groups of 2–4 questions per `AskUserQuestion` call, covering:

| Group | Questions |
|-------|-----------|
| Goal & Scope | problem, success criterion, in/out-of-scope |
| Constraints & Approach | technical/time/stakeholder constraints, preferred strategy, things to avoid |
| Staging & Risks | natural breakpoints, failure modes, rollback, external dependencies |
| Verification | test plan, acceptance gate |

All Q&A is appended to `.context/plans/<plan_name>.qa.md` (audit trail).

### Phase 3 — Assemble

Writes the plan to `.context/plans/<plan_name>.md` with **every** section the viewer renders — Context, Goal, Scope, Approach (with Mermaid), per-Phase task checklists with Files-touched lists, Risks table, Verification Plan, Rollback, Open Questions. Sections that don't apply are written as `N/A — reason` rather than omitted.

### Phase 4 — Viewer gate (mandatory)

```bash
agent-viewer plan --file .context/plans/<plan_name>.md --title "Plan: ..." --json
```

| `action` | Behaviour |
|----------|-----------|
| `approved` | Continue to Phase 5 with the current file contents |
| `edited` | Viewer has already written edits back to `filePath`; re-read and continue |
| `declined` | Halt. Surface `comments[]`, ask what to revise, loop back to Phase 3 |

If `agent-viewer` is missing, the command runs `bash plugins/toolkit/scripts/install-agent-viewer.sh` automatically.

### Phase 5 — Execute + completion report

Executes the approved plan based on `--agent`:

- **`inline`** (default) — runs phases sequentially in the current session using Read/Write/Edit/Bash. Checks off tasks in the plan file as they complete.
- **`haiku` / `sonnet` / `opus`** — dispatches to `/haiku --model <tier>` with the plan path as context.

After execution, builds `.context/plans/<plan_name>.completion.json` (summary + Mermaid + task checklist + per-file diffs via `git diff`) and opens it:

```bash
cat .context/plans/<plan_name>.completion.json | agent-viewer completion --stdin --json
```

The completion report is informational (no gate) — it closes the round-trip loop so the work has a reviewable artifact.

## Storage

Project-local, under the git root:

```
.context/plans/
├── <plan_name>.md               # the plan (reviewed by agent-viewer plan)
├── <plan_name>.qa.md            # append-only Q&A transcript
└── <plan_name>.completion.json  # completion payload (audit-retained)
```

## Examples

### Small refactor, inline execution

```bash
/agent-plan Add retry logic to the http client
```

Expect: one scout agent runs, 3–5 Q&A rounds, plan written to `.context/plans/2026-04-18-add-retry-logic-to-the-http-client.md`, browser opens the viewer, on Approve execution starts in-session, completion report opens at the end.

### Named plan

```bash
/agent-plan Add pagination to the search API --name search-pagination
```

### Offload execution to a Haiku team

```bash
/agent-plan Migrate all fetch calls to the new retry client --agent haiku
```

### Edit-in-browser flow

```bash
/agent-plan Reorganise the config loader
```

In the viewer, tweak a Phase, click Approve. The command re-reads from disk (viewer has already written back) and executes the edited version.

## Exit States

| Symptom | Cause | Fix |
|---------|-------|-----|
| `agent-viewer: command not found` | CLI not installed on PATH | Run `/setup` or `bash plugins/toolkit/scripts/install-agent-viewer.sh` |
| Viewer decline loop | Plan draft fundamentally off | Decline with specific comments; command re-asks what to revise |
| `.context/plans/` not created | Not in a git repo and CWD is read-only | Run from inside a writable project directory |
| Completion report empty on diffs | No git changes tracked yet | `git add -A` before execution, or run inline execution which commits nothing by default |
| Inline execution clobbers uncommitted work | Plan touched files you were already editing | Stash first: `git stash && /agent-plan ... && git stash pop` |

## Key Behaviours

- **Every section filled** — the plan is maximally robust; missing sections are written as `N/A — reason`
- **Viewer gate is binding** — declined plans never execute
- **Re-read after edit** — if the viewer returned `edited`, the file is re-read from disk before execution
- **Append-only Q&A log** — the `.qa.md` sibling is never overwritten
- **Inline by default** — parallel agents only engaged with explicit `--agent` flag
- **Round-trip loop always closes** — completion report opens after execution, even on short plans

## When to Use

- Scoping a bug fix that's larger than a one-liner but smaller than a feature spec
- Any change that needs approval before you start coding
- Work you want documented alongside the code (plans live in `.context/`, not `~/.claude/`)

For larger, multi-document feature work (requirements/design/tasks), use [`/agent-spec`](agent-spec.md) instead.

## See Also

- [/agent-spec](agent-spec.md) — multi-document spec sibling (Kiro pattern)
- [/kiro](kiro.md) — equivalent to `/agent-spec`, legacy name
- [/haiku](haiku.md) — parallel-agent execution tier (used by `--agent haiku|sonnet|opus`)
- [agent-viewer skill](../skills/agent-viewer.md) — the round-trip review contract this command honours
