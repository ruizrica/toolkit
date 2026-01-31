---
description: "Restore session from .plans/session-state.json after /clear"
allowed-tools: ["Read", "Bash", "TodoWrite", "AskUserQuestion"]
---

# Restore Command

Restore a compacted session and immediately continue working.

## Execution

### Step 1: Read Session State

Read `.plans/session-state.json` from the current project root.

### Step 2: Handle Missing File

**If file not found**, check for backups:

```bash
ls -t ~/.claude/session-states/*.json 2>/dev/null | head -5
```

If backups exist, use AskUserQuestion:
```json
{
  "questions": [{
    "question": "No local session state. Found backups in ~/.claude/session-states/. What to do?",
    "header": "No session",
    "options": [
      {"label": "Use latest backup (Recommended)", "description": "Restore from most recent global backup"},
      {"label": "Start fresh", "description": "Begin without restoration"},
      {"label": "Cancel", "description": "Do nothing"}
    ],
    "multiSelect": false
  }]
}
```

### Step 3: Parse and Restore

The session state can be in two formats. Detect by checking for `$schema`:

**V2 Format (from PreCompact hook):**
```json
{
  "$schema": "session-state-v2",
  "continue": "continuation prompt",
  "task": "overall task",
  "todos": [{"t": "task", "done": false}],
  "files": ["path/to/file.ts"]
}
```

**V1 Format (legacy):**
```json
{
  "tier1_brief": {
    "continuation_prompt": "...",
    "status": "in_progress"
  },
  "tier2_context": {
    "todo_list": [{"task": "...", "status": "completed"}]
  }
}
```

### Step 4: Output and Continue

Output format:
```
Restoring session...

**Task:** [task or tier1_brief.continuation_prompt]
**Continue:** [continue or "Continue working"]

---
```

### Step 5: Restore Todos

Convert todos to TodoWrite format:

**V2:** `{"t": "task", "done": true}` → `{"content": "task", "status": "completed", "activeForm": "..."}`
**V1:** `{"task": "...", "status": "completed"}` → `{"content": "...", "status": "completed", "activeForm": "..."}`

Use TodoWrite to restore the task list.

### Step 6: Immediately Continue

**DO NOT ask the user what to do next.**

Based on `continue` (v2) or `tier1_brief.continuation_prompt` (v1):
- Read the first file in `files` array if present
- Continue the work described in the continuation prompt

## Example Flow

```
User: /restore

Agent:
Restoring session...

**Task:** Implement token refresh with RS256 validation
**Continue:** Run the failing test for JWT expiry validation and fix the edge case

---

[Agent reads src/auth/jwt.ts and continues working]
```

## Critical Rules

1. **FAST**: Minimal parsing, immediate action
2. **BOTH SCHEMAS**: Support v1 (tier-based) and v2 (flat) formats
3. **RESTORE TODOS**: Always restore the todo list
4. **NO QUESTIONS**: After successful restore, immediately continue working
5. **FILES FIRST**: If `files` array exists, read the first one

## Begin Execution

1. Read `.plans/session-state.json`
2. If missing, check backups and ask user
3. Detect schema version ($schema field)
4. Extract: continue prompt, task, todos, files
5. Output restoration summary
6. Restore todos via TodoWrite
7. Immediately continue working
