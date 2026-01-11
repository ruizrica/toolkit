---
description: Coordinate multi-agent team to implement features, code, or solutions in parallel
argument-hint: [what to implement - feature/app/system/etc]
allowed-tools: Task
context: fork
agent: general-purpose
---

**CRITICAL INSTRUCTION: You MUST immediately spawn agents after analyzing the task. Do NOT just describe what you'll do - actually invoke the Task tool multiple times in parallel.**

## Implementation Request
Task: $ARGUMENTS

## Your Action Plan (Execute Immediately):

1. **ANALYZE** the task and break it into parallel work streams
2. **IMMEDIATELY SPAWN AGENTS** using multiple Task tool invocations in a SINGLE response
3. **USE ALL RELEVANT AGENTS** - Don't hold back, spawn as many as needed

## Available Agent Types:

**Investigation & Research:**
- **gemini-agent** - Large codebase analysis, research, documentation, web search
- **cursor-agent** - Code review, refactoring analysis, test planning

**Implementation:**
- **codex-agent** - Complex algorithms, advanced features, sophisticated logic
- **qwen-agent** - Performance optimization, data structures, complex refactoring
- **opencode-agent** - API development, standard CRUD, cost-effective bulk generation
- **groq-agent** - Rapid prototyping, boilerplate, simple utilities

## Example Multi-Agent Spawn Pattern:

When you receive a complex task, your FIRST response should spawn agents like this:

```
I'll spawn a multi-agent team to tackle this in parallel:

<tool_invocations>
  <invoke Task with gemini-agent>
    prompt: Investigate X and return findings...
  </invoke>
  <invoke Task with cursor-agent>
    prompt: Analyze Y and provide recommendations...
  </invoke>
  <invoke Task with codex-agent>
    prompt: Design Z architecture...
  </invoke>
  <invoke Task with qwen-agent>
    prompt: Implement W optimization...
  </invoke>
</tool_invocations>
```

## EXECUTION INSTRUCTIONS:

**RIGHT NOW you must:**
1. Parse the task: $ARGUMENTS
2. Decompose into 3-6 parallel sub-tasks
3. Select appropriate agent types for each
4. **INVOKE multiple Task tools IN PARALLEL in your NEXT response**
5. Wait for results and synthesize them

**DO NOT:**
- Just describe what you plan to do
- Say "Let me initiate..." without actually invoking tools
- Spawn agents one at a time
- Wait for user confirmation

**REMEMBER:** The user asked for /team because they want MULTIPLE AGENTS WORKING IN PARALLEL. Give them what they asked for!
