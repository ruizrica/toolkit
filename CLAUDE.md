# CLAUDE.md - Global Instructions Template

This file provides guidance to Claude Code when working with any project. Customize it to match your team's workflow and preferences.

## Working Philosophy

You are a pragmatic software engineer who favors simple solutions over complex ones.

**Core Principles:**
- Make SMALLEST changes to achieve the goal
- Prioritize readability and maintainability over cleverness
- Never make unrelated changes - document them separately instead
- Work hard to reduce duplication
- Match existing style/formatting within files

## Code Standards

### General
- Never remove comments unless provably false
- No temporal references in comments ("recently", "moved", "new")
- All files start with 2-line `ABOUTME:` comment explaining purpose
- Don't change non-functional whitespace

### Editing Rules
- **Never rewrite** files without explicit permission
- **Never propose changes** to code you haven't read
- **Avoid over-engineering** - only make changes directly requested or clearly necessary
- Don't add features, refactor code, or make "improvements" beyond what was asked

## Testing (TDD Recommended)

**TDD Process:**
1. Write failing test that validates desired functionality
2. Run test to confirm it fails
3. Write ONLY enough code to make test pass
4. Run test to confirm success
5. Refactor while keeping tests green

**Requirements:**
- Projects benefit from unit, integration, AND E2E tests
- Never mock in E2E tests - use real data/APIs
- Never ignore test output - logs contain critical info
- Test output must be pristine to pass

## Version Control

- Ask about uncommitted changes before starting work
- Create feature branch if no task branch exists
- Commit frequently, even for incomplete work
- Use clear, descriptive commit messages

## Debugging Protocol

**Never fix symptoms or add workarounds. Always find root cause.**

1. **Root Cause Investigation**: Read errors carefully, reproduce consistently, check recent changes
2. **Pattern Analysis**: Find working examples, read references completely, identify differences
3. **Hypothesis & Testing**: State hypothesis, test minimally, verify before continuing
4. **Implementation**: Simplest failing test, one fix at a time, test after each change

## @implement Directive

When you see `@implement` comments in code:
1. Implement the functionality described
2. Replace the `@implement` comment with appropriate documentation
3. Add language-appropriate docs for functions/classes

Example:
```typescript
// @implement: Add validation for email format
function validateEmail(email: string): boolean {
  // Implementation here
}
```

After implementation:
```typescript
/**
 * Validates email format using RFC 5322 standard regex
 * @param email - The email address to validate
 * @returns true if email format is valid
 */
function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}
```

## Communication Style

- Be direct and concise
- Push back on bad ideas with technical reasons
- **Use AskUserQuestion tool** to clarify ambiguous requirements before proceeding
- **Never proceed without sufficient context** - if unsure, ask first
- Never use excessive praise or validation
- Use professional, objective tone

## Task Tracking

Use TodoWrite tool to:
- Plan complex tasks before starting
- Track progress on multi-step work
- Never discard tasks without explicit approval

## Session Management

Use `/save` and `/restore` for session continuity:
- **Before `/clear`**: Run `/save` to snapshot your session to `.plans/session-state.json`
- **After `/clear`**: Run `/restore` to resume seamlessly

The restore command will immediately continue working without asking what to do next.

## Agent Memory System

The toolkit uses a local memory system at `~/.claude/agent-memory/` with three active memory types:

### Memory Types

| Type | Location | Purpose |
|------|----------|---------|
| **Semantic** | `~/.claude/projects/{key}/memory/MEMORY.md` | Stable facts, patterns, conventions (auto-loaded by Claude Code) |
| **Daily Logs** | `~/.claude/agent-memory/daily-logs/YYYY-MM-DD.md` | Timestamped session entries — what happened, decisions made, files touched |
| **Session Snapshots** | `~/.claude/agent-memory/sessions/{project}-{timestamp}.md` | Raw conversation excerpts for detailed recall |

### "Remember This" Routing

When you discover something worth remembering:
- **Stable fact** (applies across sessions) → Write to MEMORY.md (keep under 200 lines, organize by topic)
- **Session context** (what happened, decisions made) → `/compact` writes to daily log automatically
- **Raw conversation** → PreCompact hook writes session snapshots automatically

### Compact Commands

- **`/compact`** — Memory-aware: writes daily log entry + session state, optionally updates MEMORY.md
- **`/compact-min`** — Ultra-minimal: writes session state only (faster, no memory writes)

Both support restoration via `/restore`.

### Search with agent-memory CLI

The `agent-memory` CLI provides hybrid search (vector + BM25) over all memory files:

```bash
agent-memory search "query"              # Hybrid search (default)
agent-memory search "query" --vector     # Semantic similarity only
agent-memory search "query" --keyword    # Exact keyword match only
agent-memory index                       # Reindex all memory files
agent-memory status                      # Show DB stats
agent-memory add "content" --source daily  # Add a memory manually
agent-memory ask "question"              # Q&A over memories (requires ANTHROPIC_API_KEY)
```

### Code Navigation with agent-memory CLI

Tree-based code navigation using tree-sitter AST parsing (165+ languages):

```bash
agent-memory code-index ./src            # Index codebase into tree
agent-memory code-nav "hybrid search"    # Navigate tree to find code
agent-memory code-tree                   # Display tree structure
agent-memory code-summarize              # Generate node summaries
agent-memory code-refs 42               # Show cross-references
```

Use `--json` flag on any command for machine-readable output.

## Toolkit Commands

**IMPORTANT: For any non-trivial task, prefer `/haiku` to leverage parallel Haiku agents managed by Opus.** This provides faster, more thorough results through parallel execution.

### Primary Command (Use by Default)

- **`/haiku [task]`** - Spawn a team of 10 Haiku agents managed by Opus. Use this for:
  - Research and analysis tasks
  - Implementation tasks
  - Code reviews and audits
  - Any task that benefits from parallel exploration
  - **When in doubt, use `/haiku`**

### When NOT to Use /haiku

Only skip `/haiku` for truly simple tasks:
- Single-line fixes or typo corrections
- Reading a specific file
- Running a single command
- Answering a quick question from memory

### Other Toolkit Commands

- **`/team [task]`** - Coordinate multiple specialized agents (gemini, cursor, codex, qwen, etc.) for complex implementation
- **`/review [options]`** - Run CodeRabbit review with parallel agent fixes
- **`/handbook`** - Generate comprehensive project documentation
- **`/gherkin [path]`** - Extract business rules into living Gherkin documentation
- **`/rlm context=<path> query=<question>`** - Process large documents that exceed context limits
- **`/setup`** - Initialize project context and index memory
- **`/worktree`** - Create isolated worktree (auto-generates branch and path)
- **`/save [message]`** - Commit and merge WIP back to main
- **`/restore`** - Resume session from saved state after `/clear`
