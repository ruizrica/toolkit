<p align="center">
  <img src="../../assets/team.png" alt="Team" width="120">
</p>

# /team

Coordinate a multi-agent team to implement features, code, or solutions in parallel. This command automatically analyzes tasks, decomposes them into parallel work streams, and spawns multiple specialized agents simultaneously.

## Usage

```bash
/team [what to implement - feature/app/system/etc]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| task description | Yes | What you want to implement (feature, app, system, etc.) |

## How It Works

1. **Analyze** - Parses the task and breaks it into parallel work streams
2. **Decompose** - Creates 3-6 parallel sub-tasks based on the request
3. **Assign** - Selects appropriate agent types for each sub-task
4. **Execute** - Spawns multiple agents in parallel using a single response
5. **Synthesize** - Collects results and combines them into a cohesive output

## Available Agents

The `/team` command can spawn any of these specialized agents:

**Investigation & Research:**
- **gemini-agent** - Large codebase analysis, research, documentation, web search
- **cursor-agent** - Code review, refactoring analysis, test planning

**Implementation:**
- **codex-agent** - Complex algorithms, advanced features, sophisticated logic
- **qwen-agent** - Performance optimization, data structures, complex refactoring
- **opencode-agent** - API development, standard CRUD, cost-effective bulk generation
- **groq-agent** - Rapid prototyping, boilerplate, simple utilities

## Example

```bash
/team Implement user authentication with OAuth support
```

This might spawn:
- gemini-agent to research OAuth best practices
- cursor-agent to analyze existing auth code
- codex-agent to design the auth architecture
- qwen-agent to implement the core OAuth flow

## Key Behaviors

- **Parallel Execution** - Spawns all agents in a single message for maximum parallelism
- **No Confirmation** - Acts immediately without waiting for user confirmation
- **Automatic Selection** - Chooses the right agents based on task requirements
- **Result Synthesis** - Combines all agent outputs into a unified response

## When to Use

- Implementing complex features that benefit from parallel work
- Tasks that combine research, design, and implementation
- Projects requiring multiple perspectives or specialties
- Large changes that can be decomposed into independent parts

## See Also

- [/haiku](haiku.md) - Structured team with Opus orchestration
- [Agents Overview](../agents/README.md) - All available agents
