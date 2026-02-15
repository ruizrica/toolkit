<p align="center">
  <img src="../../assets/opus.png" alt="Opus" width="120">
</p>

# /opus

Spawn a team of 10 Opus agents managed by Opus for any task. This command provides structured multi-agent orchestration with distinct phases for context gathering, implementation, and validation.

## Usage

```bash
/opus [task description - research, analyze, implement, etc.]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| task description | Yes | The task for the Opus team (research, analyze, implement, etc.) |

## Team Structure

The command orchestrates 11 agents total:

| Role | Count | Purpose |
|------|-------|---------|
| Opus Orchestrator | 1 | Parse task, assign work, synthesize results |
| Context Opus | 4 | Gather context before implementation |
| Implementation Opus | 4 | Execute the main work in parallel |
| Validator Opus | 2 | Verify and cross-check results |

## How It Works

### Phase 1: Context Gathering

Four Opus agents launch in parallel to gather context:

1. **Code Explorer** - Find relevant files, patterns, similar implementations
2. **Architecture Scout** - Map dependencies, entry points, module structure
3. **History Investigator** - Check git history, recent changes, ownership
4. **Test Analyst** - Find test patterns, coverage gaps, quality requirements

### Phase 2: Task Decomposition

Opus analyzes all context findings and:
- Classifies the task type (research, implementation, analysis)
- Creates 4 specific subtasks informed by the gathered context
- Ensures subtasks are independent and parallelizable

### Phase 3: Implementation

Four Opus agents launch in parallel with roles based on task type:

**For Research Tasks:**
- Deep Dive Reader, Documentation Analyzer, Pattern Finder, Edge Case Hunter

**For Implementation Tasks:**
- Core Implementer, Test Writer, API Handler, Integration Specialist

**For Analysis Tasks:**
- Code Quality Reviewer, Performance Investigator, Security Auditor, Test Coverage Analyzer

### Phase 4: Validation

Two Opus agents verify the work:

1. **Completeness Checker** - Verify all subtasks addressed, check for gaps
2. **Quality Checker** - Cross-check consistency, verify accuracy, find contradictions

### Phase 5: Synthesis

Opus synthesizes all 10 agent outputs into a cohesive final response with:
- Summary of accomplishments
- Key findings organized by relevance
- Issues or concerns needing attention
- Recommendations for next steps

## Example

```bash
/opus Analyze and document all API endpoints
```

**Output Flow:**
1. Context agents discover API structure, patterns, existing docs
2. Opus creates 4 documentation subtasks
3. Implementation agents document endpoints in parallel
4. Validators verify completeness and consistency
5. Final synthesized API documentation delivered

## Key Behaviors

- **Phased Execution** - Each phase completes before the next begins
- **Parallel Within Phases** - Agents within each phase run simultaneously
- **Structured Output** - All agents return JSON for easy synthesis
- **Maximum Capability** - Uses Opus model for all sub-agents

## When to Use

- Tasks requiring maximum reasoning capability per agent
- Complex research requiring deep analysis
- Implementation needing thorough validation
- High-stakes analysis where accuracy is critical

## See Also

- [/haiku](haiku.md) - Cost-effective alternative using Haiku agents
- [/team](team.md) - Simpler multi-agent coordination
- [Agents Overview](../agents/README.md) - All available agents
