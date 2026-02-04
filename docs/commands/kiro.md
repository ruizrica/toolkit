<p align="center">
  <img src="../../assets/kiro.png" alt="Kiro" width="120">
</p>

# /kiro

Spec-driven development workflow that generates professional requirements, design, and task documentation using the Kiro methodology, then executes with parallel agents.

## Usage

```bash
/kiro [feature idea] [--project PATH] [--name SPEC_NAME] [--agent cursor|haiku]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| feature idea | Yes | Description of the feature to implement |
| --project PATH | No | Project path (defaults to current directory) |
| --name SPEC_NAME | No | Spec name (defaults to date-based format) |
| --agent cursor\|haiku | No | Agent type for execution (default: cursor) |

## Workflow Phases

The Kiro workflow has 4 interactive phases, each pausing for clarifying questions:

### Phase 1: Requirements Generation

- Spawns 2 Haiku agents to gather context (domain exploration, constraints discovery)
- Generates EARS-format requirements document
- **Pauses for Q&A**: scope, users, constraints, priorities

### Phase 2: Design Generation

- Spawns 2 Haiku agents (architecture designer, API designer)
- Generates comprehensive design document
- **Pauses for Q&A**: architecture approval, technology choices, trade-offs

### Phase 3: Tasks Generation

- Spawns 2 Haiku agents (task decomposer, test planner)
- Generates implementation task breakdown
- **Pauses for Q&A**: task granularity, implementation order, scope

### Phase 4: Execution

- Parses tasks into dependency waves
- Executes with parallel agents (4 Cursor or Haiku agents)
- Follows TDD approach (test first)
- Reports completion summary

## Document Storage

All documents are saved to `~/.claude/plans/{spec_name}/`:

```
~/.claude/plans/2026-02-01-user-authentication/
├── 1-requirements.md    # EARS format requirements
├── 2-design.md          # Architecture, components, APIs
├── 3-tasks.md           # Implementation task breakdown
├── qa-log.md            # Clarifying questions and answers
└── metadata.json        # Spec metadata, phase status
```

## EARS Format

Requirements use the EARS (Easy Approach to Requirements Syntax) format:

| Pattern | Usage |
|---------|-------|
| WHEN [event] THEN [system] SHALL [response] | Event-driven behavior |
| IF [condition] THEN [system] SHALL [behavior] | Condition-based behavior |
| WHILE [state] [system] SHALL [behavior] | Continuous behavior |
| WHERE [context] [system] SHALL [behavior] | Context-specific behavior |

## Examples

### Basic Usage

```bash
/kiro Add user authentication with OAuth
```

### With Custom Name

```bash
/kiro Add payment processing --name payment-integration
```

### With Haiku Agents

```bash
/kiro Refactor database layer --agent haiku
```

### Specific Project

```bash
/kiro Add dark mode support --project /path/to/frontend
```

## Key Behaviors

- **Interactive Q&A** - Pauses after each phase for clarification
- **Date-Based Naming** - Specs named as `YYYY-MM-DD-feature-name`
- **Parallel Agents** - Uses 2-4 agents per phase for efficiency
- **TDD Approach** - All implementation tasks include test-first methodology
- **Persistent Storage** - All documents saved to ~/.claude/plans/

## Agent Types

| Type | Agents | Best For |
|------|--------|----------|
| cursor (default) | 4 parallel | Faster execution, complex code |
| haiku | 4 parallel | Cost-effective, simpler tasks |

## When to Use

- Starting new features that need planning
- Complex implementations requiring design documentation
- Features that benefit from structured requirements
- Projects where documentation is important
- When you want interactive refinement of scope

## See Also

- [/haiku](haiku.md) - Multi-agent task execution
- [/team](team.md) - Multi-agent coordination
- [/handbook](handbook.md) - Project documentation generation
