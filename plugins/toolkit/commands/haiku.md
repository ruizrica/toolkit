---
description: "Spawn a team of 10 agents managed by Opus. Defaults to Haiku tier; override with --model sonnet|opus."
argument-hint: "[--model haiku|sonnet|opus] [task description]"
allowed-tools: ["Task", "Read", "Glob", "Grep", "Bash", "Write", "Edit"]
context: fork
agent: general-purpose
---

# Meta Team Command (Haiku default)

You are an Opus orchestrator managing a team of 10 agents to accomplish the user's task. The tier of the spawned agents is controlled by the `--model` flag; Haiku is the default.

## Parse Arguments

Read `$ARGUMENTS` and extract:
- `--model haiku|sonnet|opus` — the tier for all spawned subagents (default: `haiku`)
- remainder — the task description passed to the agents

Call the resolved tier `{tier}` below. Wherever the protocol says "tier agent" or "`{tier}` agent", spawn subagents at that tier. The orchestrator (you) remain Opus regardless of tier.

## User's Task

The task description remaining after `--model` is stripped out.

## Team Structure (11 agents total)

- **You (Opus)** — Orchestrator: parse task, assign work, synthesize results
- **4 Context {tier}** — Gather context before implementation begins
- **4 Implementation {tier}** — Execute the main work in parallel
- **2 Validator {tier}** — Verify and cross-check results

## Execution Protocol

### Phase 1: Context Gathering

Spawn 4 Context `{tier}` agents IN PARALLEL (single message, 4 Task tool calls) to gather context:

```
Context 1 — Code Explorer:
- Find relevant files and patterns
- Locate similar implementations
- Identify code conventions

Context 2 — Architecture Scout:
- Map dependencies and imports
- Identify entry points
- Understand module structure

Context 3 — History Investigator:
- Check git history for related changes
- Find recent modifications
- Identify file ownership patterns

Context 4 — Test Analyst:
- Find existing test patterns
- Identify coverage gaps
- Note quality requirements
```

Each Context agent MUST return structured findings as JSON:
```json
{
  "agent": "Context [N]",
  "role": "[role name]",
  "findings": {
    "relevant_files": ["path1", "path2"],
    "patterns": ["pattern1", "pattern2"],
    "insights": ["insight1", "insight2"]
  },
  "recommendations": ["rec1", "rec2"]
}
```

### Phase 2: Task Decomposition

After ALL 4 Context agents complete:
1. Analyze their combined findings
2. Classify the task type (research, implementation, analysis)
3. Create 4 specific subtasks informed by the gathered context
4. Each subtask should be independent and parallelizable

### Phase 3: Implementation

Spawn 4 Implementation `{tier}` agents IN PARALLEL (single message, 4 Task tool calls).

Assign roles dynamically based on task type:

**For Research Tasks:**
- Deep Dive Reader — Thorough file analysis
- Documentation Analyzer — Docs, comments, README
- Pattern Finder — Similar code patterns
- Edge Case Hunter — Find gotchas, edge cases

**For Implementation Tasks:**
- Core Implementer — Main logic
- Test Writer — Unit/integration tests
- API Handler — Endpoints/interfaces
- Integration Specialist — Wire components together

**For Analysis Tasks:**
- Code Quality Reviewer — Issues, smells
- Performance Investigator — Bottlenecks
- Security Auditor — Vulnerabilities
- Test Coverage Analyzer — Gaps in testing

Each Implementation agent prompt MUST include:
1. The specific subtask to accomplish
2. Relevant context from Phase 1 findings
3. Expected output format
4. Success criteria

Each Implementation agent MUST return structured results:
```json
{
  "agent": "Implementation [N]",
  "role": "[role name]",
  "task": "[assigned subtask]",
  "results": {
    "completed": true,
    "output": "[main output]",
    "files_touched": ["file1", "file2"],
    "key_findings": ["finding1", "finding2"]
  },
  "issues": ["issue1", "issue2"]
}
```

### Phase 4: Validation

After ALL 4 Implementation agents complete, spawn 2 Validator `{tier}` agents IN PARALLEL:

```
Validator 1 — Completeness Checker:
- Verify all subtasks were addressed
- Check for gaps in coverage
- Ensure nothing was missed

Validator 2 — Quality Checker:
- Cross-check consistency across outputs
- Verify accuracy of findings
- Check for contradictions
```

Provide validators with:
1. The original user task
2. All Implementation agent outputs
3. Specific validation criteria

Each Validator agent MUST return:
```json
{
  "agent": "Validator [N]",
  "role": "[role name]",
  "validation": {
    "passed": true,
    "issues_found": ["issue1", "issue2"],
    "gaps": ["gap1", "gap2"],
    "recommendations": ["rec1", "rec2"]
  }
}
```

### Phase 5: Synthesis

After ALL validators complete:
1. Synthesize all findings from all 10 agents
2. Address any issues raised by validators
3. Present a cohesive final output to the user
4. Include:
   - Summary of what was accomplished
   - Key findings organized by relevance
   - Any issues or concerns that need attention
   - Recommendations for next steps

## Critical Rules

1. **PARALLEL LAUNCH**: Always launch agents in groups using SINGLE messages with MULTIPLE Task tool calls:
   - Phase 1: 4 Context agents in ONE message
   - Phase 3: 4 Implementation agents in ONE message
   - Phase 4: 2 Validators in ONE message

2. **WAIT FOR COMPLETION**: Never start next phase until ALL agents in current phase complete

3. **AGENT TYPES**: Use `scout` for context, `builder` for implementation, `reviewer` for validation — and set the model to the selected `{tier}`.

4. **STRUCTURED OUTPUT**: Require JSON structured output from all agents

5. **CONTEXT PASSING**: Always pass relevant context from earlier phases to later agents

## Tier Mapping

| Phase | Agent type | Role | Model |
|-------|-----------|------|-------|
| Context | `scout` | Read-only recon — files, patterns, architecture, history | `{tier}` |
| Implementation | `builder` | Code writing — implements changes, runs tests | `{tier}` |
| Validation | `reviewer` | Code review — finds bugs, security issues, style problems | `{tier}` |

## Usage Examples

```
/haiku investigate the auth module                       → haiku tier (default)
/haiku --model sonnet refactor the payment pipeline      → sonnet tier
/haiku --model opus design a distributed event system    → opus tier
```

## Begin Execution

Start now by spawning the 4 Context agents in parallel at the selected tier to gather context for the task.
