---
description: "Memory-aware session compact with daily log and session snapshot"
allowed-tools: ["Read", "Write", "Edit", "Bash"]
---

# Memory-Aware Session Compact

Generate a session snapshot and write to the agent memory system before clearing context.

## Instructions

### Step 1: Introspect Session

Analyze the conversation to extract:
- `summary`: 2-3 sentence summary of what was accomplished
- `key_decisions`: Important architectural or design decisions made (array of strings, max 5)
- `current_task`: What you're actively working on right now (1 sentence)
- `key_files`: Array of absolute file paths recently read/edited (max 10)
- `continuation_prompt`: Detailed prompt telling a fresh agent exactly how to continue (2-3 sentences)
- `stable_facts`: Any stable patterns, conventions, or facts discovered that apply beyond this session (array of strings, may be empty)

### Step 2: Append Daily Log Entry

Append a formatted entry to `~/.claude/agent-memory/daily-logs/YYYY-MM-DD.md`:

```markdown
## HH:MM - {project_name}
**Summary:** {summary}
**Key decisions:** {key_decisions as bullet list}
**Files:** {key_files, comma-separated}
**Continue:** {continuation_prompt}
---
```

Create the file and directories if they don't exist. Use Bash to get the date:
```bash
date +%Y-%m-%d
```

### Step 3: Update MEMORY.md (Optional)

If `stable_facts` is non-empty, read `~/.claude/projects/{project-key}/memory/MEMORY.md`.

For each stable fact, check if it's already captured. If not, append it under an appropriate heading.

**Skip this step** if no new stable facts were discovered. Do NOT pad MEMORY.md with session-specific information.

**MEMORY.md guidelines:**
- Keep under 200 lines total
- Only stable patterns confirmed across interactions
- Organize by topic, not chronologically

### Step 4
IMPORTANT: For Step 3, you must use the EXACT file path `.context/session-state.json`. Do not save it anywhere else.
Write `.context/session-state.json` using V2 schema:

```json
{
  "$schema": "session-state-v2",
  "project": "{project_name}",
  "cwd": "{cwd}",
  "ts": "{ISO timestamp}",
  "continue": "{continuation_prompt}",
  "task": "{current_task}",
  "todos": [{"t": "task description", "done": false}],
  "files": ["{edited files}"],
  "files_read": ["{read files}"]
}
```

Include current todo list state if any todos exist.

### Step 5: Report Completion

Output:

```
Session compacted.

Daily log: ~/.claude/agent-memory/daily-logs/{YYYY-MM-DD}.md
Session state: .context/session-state.json
{if MEMORY.md updated: "MEMORY.md updated with N new facts"}

To restore after /clear:
/restore
```

## Quality Bar

The daily log entry is meant for your future self. Write it as if briefing a colleague who needs to understand what happened in this session and why decisions were made.

The continuation_prompt in session-state.json should enable a fresh agent to:
- Understand the goal immediately
- Know exactly what step to take next
- Avoid repeating completed work
- Be aware of any pitfalls discovered

## See Also

- `/compact-min` - Ultra-minimal compact (no memory writes, faster)
- `/restore` - Restore session from snapshot
