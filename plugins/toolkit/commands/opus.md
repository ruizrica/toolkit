---
description: "Spawn a team of Opus agents managed by Opus for any task"
argument-hint: "[task description - research, analyze, implement, etc.]"
allowed-tools: ["Task", "Read", "Glob", "Grep", "Bash", "Write", "Edit"]
context: fork
agent: general-purpose
---

# Opus Team Command

You are an Opus orchestrator managing a team of 10 Opus agents to accomplish the user's task.

## User's Task

$ARGUMENTS

## Team Structure (11 agents total)

- **You (Opus)** - Orchestrator: parse task, assign work, synthesize results
- **4 Context Opus** - Gather context before implementation begins
- **4 Implementation Opus** - Execute the main work in parallel
- **2 Validator Opus** - Verify and cross-check results

## Execution Protocol

### Phase 1: Context Gathering

Spawn 4 Context Opus agents IN PARALLEL (single message, 4 Task tool calls) to gather context:

```
Context 1 - Code Explorer:
- Find relevant files and patterns
- Locate similar implementations
- Identify code conventions

Context 2 - Architecture Scout:
- Map dependencies and imports
- Identify entry points
- Understand module structure

Context 3 - History Investigator:
- Check git history for related changes
- Find recent modifications
- Identify file ownership patterns

Context 4 - Test Analyst:
- Find existing test patterns
- Identify coverage gaps
- Note quality requirements
```

Each Context Opus MUST return structured findings as JSON:
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

After ALL 4 Context Opus complete:
1. Analyze their combined findings
2. Classify the task type (research, implementation, analysis)
3. Create 4 specific subtasks informed by the gathered context
4. Each subtask should be independent and parallelizable

### Phase 3: Implementation

Spawn 4 Implementation Opus agents IN PARALLEL (single message, 4 Task tool calls).

Assign roles dynamically based on task type:

**For Research Tasks:**
- Deep Dive Reader - Thorough file analysis
- Documentation Analyzer - Docs, comments, README
- Pattern Finder - Similar code patterns
- Edge Case Hunter - Find gotchas, edge cases

**For Implementation Tasks:**
- Core Implementer - Main logic
- Test Writer - Unit/integration tests
- API Handler - Endpoints/interfaces
- Integration Specialist - Wire components together

**For Analysis Tasks:**
- Code Quality Reviewer - Issues, smells
- Performance Investigator - Bottlenecks
- Security Auditor - Vulnerabilities
- Test Coverage Analyzer - Gaps in testing

Each Implementation Opus prompt MUST include:
1. The specific subtask to accomplish
2. Relevant context from Phase 1 findings
3. Expected output format
4. Success criteria

Each Implementation Opus MUST return structured results:
```json
{
  "agent": "Implementation [N]",
  "role": "[role name]",
  "task": "[assigned subtask]",
  "results": {
    "completed": true/false,
    "output": "[main output]",
    "files_touched": ["file1", "file2"],
    "key_findings": ["finding1", "finding2"]
  },
  "issues": ["issue1", "issue2"]
}
```

### Phase 4: Validation

After ALL 4 Implementation Opus complete, spawn 2 Validator Opus agents IN PARALLEL:

```
Validator 1 - Completeness Checker:
- Verify all subtasks were addressed
- Check for gaps in coverage
- Ensure nothing was missed

Validator 2 - Quality Checker:
- Cross-check consistency across outputs
- Verify accuracy of findings
- Check for contradictions
```

Provide validators with:
1. The original user task
2. All Implementation Opus outputs
3. Specific validation criteria

Each Validator Opus MUST return:
```json
{
  "agent": "Validator [N]",
  "role": "[role name]",
  "validation": {
    "passed": true/false,
    "issues_found": ["issue1", "issue2"],
    "gaps": ["gap1", "gap2"],
    "recommendations": ["rec1", "rec2"]
  }
}
```

### Phase 5: Synthesis

After ALL validators complete:
1. Synthesize all findings from all 10 Opus agents
2. Address any issues raised by validators
3. Present a cohesive final output to the user
4. Include:
   - Summary of what was accomplished
   - Key findings organized by relevance
   - Any issues or concerns that need attention
   - Recommendations for next steps

## Critical Rules

1. **PARALLEL LAUNCH**: Always launch agents in groups using SINGLE messages with MULTIPLE Task tool calls:
   - Phase 1: 4 Context Opus in ONE message
   - Phase 3: 4 Implementation Opus in ONE message
   - Phase 4: 2 Validators in ONE message

2. **WAIT FOR COMPLETION**: Never start next phase until ALL agents in current phase complete

3. **USE OPUS MODEL**: All spawned agents MUST use `model: "opus"`

4. **STRUCTURED OUTPUT**: Require JSON structured output from all agents

5. **CONTEXT PASSING**: Always pass relevant context from earlier phases to later agents

## Example Task Tool Calls

For Phase 1 (Context Gathering), send ONE message with 4 Task calls:

```
Task 1: { subagent_type: "Explore", model: "opus", prompt: "You are Context Agent 1 - Code Explorer. Task: [user task]. Find relevant files, patterns, similar implementations. Return JSON: {agent, role, findings, recommendations}" }

Task 2: { subagent_type: "Explore", model: "opus", prompt: "You are Context Agent 2 - Architecture Scout. Task: [user task]. Map dependencies, entry points, module structure. Return JSON: {agent, role, findings, recommendations}" }

Task 3: { subagent_type: "Explore", model: "opus", prompt: "You are Context Agent 3 - History Investigator. Task: [user task]. Check git history, recent changes, ownership. Return JSON: {agent, role, findings, recommendations}" }

Task 4: { subagent_type: "Explore", model: "opus", prompt: "You are Context Agent 4 - Test Analyst. Task: [user task]. Find test patterns, coverage gaps, quality requirements. Return JSON: {agent, role, findings, recommendations}" }
```

## Begin Execution

Start now by spawning the 4 Context Opus agents in parallel to gather context for the task.
