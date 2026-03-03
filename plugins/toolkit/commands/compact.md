---
description: "Memory-aware session compact — triggers native pi compaction with memory persistence"
allowed-tools: ["Bash"]
---

# Memory-Aware Session Compact

Trigger pi's native compaction system which automatically:
1. Saves a daily log entry and session state (via the memory-cycle extension hook)
2. Summarizes old messages to reclaim context tokens
3. Injects restoration context so work continues seamlessly

## Instructions

**This command triggers pi's built-in compaction.** You do NOT need to manually write files or introspect the session — the `session_before_compact` hook in the memory-cycle extension handles all persistence automatically.

### What to do

1. Tell the user: "Triggering memory-aware compaction..."
2. Call the `cycle_memory` tool if available, OR simply inform the user to use `/cycle` for a full session reset
3. If the user wants a quick compact without session reset, they should use pi's built-in `/compact` directly (Ctrl+Shift+C or the pi command)

### When to use this

- Context is getting large (>70%)
- Before switching to a very different task
- When the agent suggests compaction is needed

### Difference from /cycle

- `/compact` — Summarizes old messages in-place, keeps the same session (pi's native behavior)
- `/cycle` — Full reset: compact → new session → restore memory (fresh start)

Both automatically save daily logs and session state via the memory-cycle extension.

## Output

```
Memory-aware compaction triggered.

Daily log and session state will be saved automatically.
Context will be summarized and reclaimed.

For a full session reset with fresh context: /cycle
```
