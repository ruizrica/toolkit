# /agent-spec

Interactive spec-driven development workflow that generates EARS-format requirements, architecture design, and an implementation task breakdown, gates on `agent-viewer spec` approval, and then executes with parallel agents. Follows the same Kiro pattern as `/kiro` — the two are kept as sibling entry points so `/agent-plan` and `/agent-spec` can be memorised as a pair.

## Usage

```bash
/agent-spec [feature idea] [--project PATH] [--name SPEC_NAME] [--agent cursor|haiku]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| feature idea | Yes | Description of the feature to implement |
| --project PATH | No | Project path (defaults to current directory) |
| --name SPEC_NAME | No | Spec name (defaults to `YYYY-MM-DD-<slug>`) |
| --agent cursor\|haiku | No | Agent tier for Phase 4 execution (default: cursor) |

## Workflow Phases

Four interactive phases; each pauses for `AskUserQuestion` clarification.

### Phase 1 — Requirements

- Spawns 2 Haiku agents in parallel (domain explorer + constraints discoverer)
- Generates EARS-format requirements to `1-requirements.md`
- **Q&A pause**: scope, users, constraints, priorities

### Phase 2 — Design

- Spawns 2 Haiku agents in parallel (architecture designer + API designer)
- Generates `2-design.md` with components, data models, API contracts, error handling
- **Q&A pause**: architecture fit, technology choices, trade-offs

### Phase 3 — Tasks

- Spawns 2 Haiku agents in parallel (task decomposer + test planner)
- Generates `3-tasks.md` with phased checklist, dependencies, quality gates
- **Mandatory spec-viewer gate** — `agent-viewer spec --folder ~/.claude/plans/<spec_name> --json` must return `approved` before Phase 4
- **Q&A pause**: granularity, order, scope

### Phase 4 — Execution

- Parses tasks into dependency waves
- Spawns 4 Cursor (or Haiku, with `--agent haiku`) agents per wave in parallel
- Enforces TDD (test first)
- Reports completion summary

## Storage

All artifacts live in `~/.claude/plans/<spec_name>/`:

```
~/.claude/plans/2026-04-18-user-authentication/
├── 1-requirements.md    # EARS requirements
├── 2-design.md          # architecture + APIs
├── 3-tasks.md           # implementation checklist
├── qa-log.md            # Q&A transcript (append-only)
└── metadata.json        # phase status + execution metadata
```

## EARS Format

Requirements use the EARS (Easy Approach to Requirements Syntax) patterns:

| Pattern | Usage |
|---------|-------|
| WHEN [event] THEN [system] SHALL [response] | Event-driven behaviour |
| IF [condition] THEN [system] SHALL [behaviour] | Condition-based behaviour |
| WHILE [state] [system] SHALL [behaviour] | Continuous behaviour |
| WHERE [context] [system] SHALL [behaviour] | Context-specific behaviour |

## Spec-Viewer Gate

Before execution, the three generated docs are loaded into `agent-viewer spec` and the return value is binding:

| `action` | Behaviour |
|----------|-----------|
| `approved` | Proceed to Phase 4 |
| `edited` | Viewer has already written edits back to disk; re-read the docs and proceed |
| `declined` | Halt. Surface `comments[]`, revise, re-invoke the viewer |

See `skills/agent-viewer.md` for the full round-trip contract.

## Examples

### Basic usage

```bash
/agent-spec Add user authentication with OAuth
```

### Custom spec name

```bash
/agent-spec Add payment processing --name payment-integration
```

### Haiku execution tier (cheaper)

```bash
/agent-spec Refactor the database layer --agent haiku
```

### Against a specific repo

```bash
/agent-spec Add dark mode support --project ~/Workshop/frontend
```

## Exit States

| Symptom | Cause | Fix |
|---------|-------|-----|
| `agent-viewer: command not found` | CLI not installed | Run `/setup` or `bash plugins/toolkit/scripts/install-agent-viewer.sh` |
| Viewer never returns | Browser tab closed without clicking approve/decline | Re-run the command; state is preserved in the spec folder |
| Decline loops without progress | Comments unclear | Use AskUserQuestion to restate the intent before the next revision round |
| Phase 4 stalls on a wave | One parallel agent hit a blocker | Check that agent's output; restart with `--agent haiku` if cost is a factor |

## Key Behaviours

- **Mandatory spec-viewer review** — no execution without approval
- **Interactive Q&A** — pauses after each doc phase
- **Date-based naming** — specs named `YYYY-MM-DD-feature-name`
- **Parallel research agents** — 2 Haiku agents per phase for efficiency
- **TDD enforced** — every implementation task includes a test-first step
- **Persistent storage** — all documents under `~/.claude/plans/`

## Relationship to /agent-plan and /kiro

| Command | Artifact | Scale | Storage |
|---------|----------|-------|---------|
| `/agent-plan` | Single-document plan | Small-to-medium tasks, one coherent change | `.context/plans/<name>.md` (project-local) |
| `/agent-spec` | Multi-document spec (3 docs) | Larger features that benefit from requirements/design/tasks split | `~/.claude/plans/<spec_name>/` (global) |
| `/kiro` | Same as `/agent-spec` | Same | Same |

`/agent-spec` and `/kiro` are parallel names for the same workflow; either can be used interchangeably.

## See Also

- [/agent-plan](agent-plan.md) — single-document interactive plan sibling
- [/kiro](kiro.md) — original Kiro-pattern command (same workflow, legacy name)
- [/haiku](haiku.md) — underlying parallel-agent execution tier
- [/handbook](handbook.md) — project documentation generator
