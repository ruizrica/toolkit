<p align="center">
  <img src="../../assets/compact.png" alt="Compact" width="120">
</p>

# /compact

Generate a minimal session snapshot for fast context restoration. This command saves your current session state before using `/clear`, enabling seamless continuation afterward.

## Usage

```bash
/compact
```

## Arguments

This command takes no arguments. It introspects the current conversation to extract relevant state.

## How It Works

1. **Introspect** - Analyze the conversation to extract key information
2. **Extract** - Capture original request, current task, key files, and continuation prompt
3. **Write** - Save to `.plans/session-state.json`
4. **Report** - Confirm completion and provide restore instructions

## Output Format

The command creates a JSON file with this structure:

```json
{
  "timestamp": "2026-01-30T10:30:00Z",
  "original_request": "Implement user authentication with OAuth",
  "current_task": "Writing unit tests for the token refresh logic",
  "key_files": [
    "/src/auth/oauth.ts",
    "/src/auth/tokens.ts",
    "/tests/auth/oauth.test.ts"
  ],
  "continuation_prompt": "User wants OAuth authentication. Created OAuth flow in src/auth/oauth.ts, tested working. Next: implement token refresh with RS256 validation. Note: discovered that the token expiry check needs UTC normalization."
}
```

## Field Descriptions

| Field | Description |
|-------|-------------|
| `timestamp` | ISO timestamp of when the snapshot was created |
| `original_request` | What the user originally asked for (1 sentence) |
| `current_task` | What you're actively working on right now (1 sentence) |
| `key_files` | Array of absolute file paths recently read/edited (max 5) |
| `continuation_prompt` | Detailed instructions for continuing (2-3 sentences) |

## Quality Bar for continuation_prompt

The continuation prompt is the most important field. It should enable a fresh agent to:

- Understand the goal immediately
- Know exactly what step to take next
- Avoid repeating completed work
- Be aware of any pitfalls discovered

**Good Example:**
```
User wants a REST API for todo items. Created GET /todos endpoint, tested working.
Next: implement POST /todos with validation. Note: the db connection pool maxes at 10,
discovered this causes timeouts under load.
```

**Bad Example:**
```
Working on API stuff.
```

## Workflow

```bash
# Before clearing context
/compact

# Clear context
/clear

# Resume seamlessly
/restore
```

## Output Location

The session state is saved to:
```
.plans/session-state.json
```

This is relative to your project root.

## When to Use

- Before running `/clear` to free up context
- When context is getting too long
- Before switching to a different task temporarily
- To create a checkpoint during complex work

## See Also

- [/restore](restore.md) - Restore session from snapshot
- [/save](save.md) - Commit and merge changes (different purpose)
