<p align="center">
  <img src="../../assets/restore.png" alt="Restore" width="120">
</p>

# /restore

Restore a compacted session and immediately continue working. This command reads the session state saved by `/compact`, loads daily log context for cross-session continuity, and resumes work without asking what to do next.

## Usage

```bash
/restore
```

## Arguments

This command takes no arguments. It automatically reads from `.plans/session-state.json`.

## How It Works

1. **Read** - Load session state from `.plans/session-state.json`
2. **Handle Missing** - If not found, check for backups in `~/.claude/session-states/`
3. **Daily Log Bootstrap** - Read today's and yesterday's daily logs from `~/.claude/agent-memory/daily-logs/` for cross-session context
4. **Parse** - Detect schema version and extract fields
5. **Restore Todos** - Recreate the task list if present
6. **Continue** - Immediately resume work based on continuation prompt

## Memory Bootstrap

On restore, the agent reads:
- `~/.claude/agent-memory/daily-logs/{today}.md` — what happened earlier today
- `~/.claude/agent-memory/daily-logs/{yesterday}.md` — what happened yesterday

This provides continuity across sessions. The agent internalizes this context silently — it won't dump the full log to you, but it knows what was done in prior sessions.

## Schema Support

The command supports two schema versions:

### V2 Format (Current)

```json
{
  "$schema": "session-state-v2",
  "continue": "continuation prompt",
  "task": "overall task",
  "todos": [{"t": "task description", "done": false}],
  "files": ["path/to/file.ts"]
}
```

### V1 Format (Legacy)

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

## Missing File Handling

If `.plans/session-state.json` is not found, the command:

1. Checks for backups in `~/.claude/session-states/`
2. Lists available backup files
3. Asks user to choose:
   - **Use latest backup** - Restore from most recent global backup
   - **Start fresh** - Begin without restoration
   - **Cancel** - Do nothing

## Output Format

```
Restoring session...

**Task:** Implement token refresh with RS256 validation
**Continue:** Run the failing test for JWT expiry validation and fix the edge case

---

[Agent reads first file and continues working]
```

## Key Behaviors

- **No Questions** - After successful restore, immediately continues working
- **Daily Logs** - Reads today's and yesterday's logs for cross-session context
- **Files First** - If `files` array exists, reads the first file
- **Todo Restoration** - Recreates the task list for tracking
- **Fast** - Minimal parsing, immediate action

## Workflow

```bash
# Save state before clearing
/compact

# Clear context
/clear

# Resume seamlessly
/restore
```

## Data Locations

| Location | Purpose |
|----------|---------|
| `.plans/session-state.json` | Project-specific state (primary) |
| `~/.claude/session-states/*.json` | Global backups (fallback) |
| `~/.claude/agent-memory/daily-logs/` | Cross-session context (bootstrap) |

## When to Use

- After running `/clear` to resume work
- When starting a new session on an existing task
- After restarting Claude Code
- When returning to a paused project

## See Also

- [/compact](compact.md) - Save session state with memory writes
- [/save](save.md) - Commit changes (different purpose)
