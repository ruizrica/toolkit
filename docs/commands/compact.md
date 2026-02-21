<p align="center">
  <img src="../../assets/compact.png" alt="Compact" width="120">
</p>

# /compact

Memory-aware session compact. Saves your current session state, writes a daily log entry, and optionally updates MEMORY.md before using `/clear`.

## Usage

```bash
/compact
```

## Arguments

This command takes no arguments. It introspects the current conversation to extract relevant state.

## How It Works

1. **Introspect** - Analyze the conversation to extract summary, key decisions, files, continuation prompt, and any stable facts
2. **Daily Log** - Append a formatted entry to `~/.claude/agent-memory/daily-logs/YYYY-MM-DD.md`
3. **MEMORY.md** - If stable facts were discovered, update the project's MEMORY.md (optional)
4. **Session State** - Write `.context/session-state.json` (V2 schema)
5. **Report** - Confirm completion and provide restore instructions

## Daily Log Format

Each `/compact` appends an entry like:

```markdown
## 14:30 - my-project
**Summary:** Implemented OAuth flow and wrote unit tests for token refresh
**Key decisions:**
- Chose RS256 over HS256 for JWT signing
- Used middleware pattern for auth checks
**Files:** /src/auth/oauth.ts, /src/auth/tokens.ts, /tests/auth/oauth.test.ts
**Continue:** Run the failing test for JWT expiry validation and fix the UTC edge case
---
```

## Session State Format (V2)

```json
{
  "$schema": "session-state-v2",
  "project": "my-project",
  "cwd": "/path/to/project",
  "ts": "2026-01-30T14:30:00Z",
  "continue": "Run the failing test for JWT expiry...",
  "task": "Implement token refresh with RS256",
  "todos": [{"t": "Fix UTC edge case", "done": false}],
  "files": ["/src/auth/oauth.ts"],
  "files_read": ["/src/config.ts"]
}
```

## Output Locations

| File | Purpose |
|------|---------|
| `~/.claude/agent-memory/daily-logs/YYYY-MM-DD.md` | Daily log entry |
| `.context/session-state.json` | Session state for `/restore` |
| `~/.claude/projects/{key}/memory/MEMORY.md` | Stable facts (if updated) |

## When to Use

- Before running `/clear` to free up context
- When context is getting too long
- Before switching to a different task temporarily
- To create a checkpoint during complex work

## /compact-min

For a faster, minimal compact that skips memory writes:

```bash
/compact-min
```

This writes only `.context/session-state.json` — no daily log, no MEMORY.md update. Use when speed matters more than memory continuity.

## Workflow

```bash
# Before clearing context
/compact

# Clear context
/clear

# Resume seamlessly (includes daily log context)
/restore
```

## See Also

- [/restore](restore.md) - Restore session from snapshot (loads daily logs)
- [/save](save.md) - Commit and merge changes (different purpose)
