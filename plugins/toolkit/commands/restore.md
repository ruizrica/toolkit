---
description: "Restore session context from .context/session-state.json and daily logs"
allowed-tools: ["Read", "Bash"]
---

# Restore Command

Restore context from saved session state and daily logs.

## When to Use

- After a manual `/clear` or `/new` session
- When starting work on a project you've worked on before
- When you need to recall what happened in previous sessions

**Note:** If you used `/cycle`, context is automatically restored — you don't need `/restore`.
If pi's auto-compaction ran, the memory-cycle extension automatically injected restoration context.

## Execution

### Step 1: Read Session State

Read `.context/session-state.json` from the current project root.

### Step 2: Read Daily Logs

Read recent daily logs for cross-session context:

```bash
# Today's and yesterday's dates
date +%Y-%m-%d
date -v-1d +%Y-%m-%d 2>/dev/null || date -d yesterday +%Y-%m-%d
```

Read `~/.claude/agent-memory/daily-logs/{today}.md` and `~/.claude/agent-memory/daily-logs/{yesterday}.md` if they exist.

### Step 3: Parse Session State

The session state uses V2 schema:

```json
{
  "$schema": "session-state-v2",
  "project": "project-name",
  "cwd": "/path/to/project",
  "ts": "ISO timestamp",
  "continue": "continuation prompt",
  "task": "current task",
  "files": ["edited files"],
  "files_read": ["read files"]
}
```

### Step 4: Output and Continue

```
Restoring session...

**Task:** [task from session state]
**Continue:** [continuation prompt]
**Files:** [key files]

---
```

### Step 5: Immediately Continue

**DO NOT ask the user what to do next.**

Based on the `continue` field:
- Read the first file in `files` array if present
- Continue the work described in the continuation prompt
- Use daily log context to understand broader history

## Critical Rules

1. **FAST**: Minimal parsing, immediate action
2. **DAILY LOGS**: Read today's and yesterday's logs for cross-session context
3. **NO QUESTIONS**: After successful restore, immediately continue working
4. **FILES FIRST**: If `files` array exists, read the first one
