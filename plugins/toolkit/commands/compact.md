# Ultra-Minimal Session Compact

Generate a minimal session snapshot for fast context restoration.

## Instructions

1. **Introspect the conversation** to extract:
   - `original_request`: What the user originally asked for (1 sentence)
   - `current_task`: What you're actively working on right now (1 sentence)
   - `key_files`: Array of absolute file paths recently read/edited (max 5)
   - `continuation_prompt`: A detailed prompt that tells a fresh agent exactly how to continue (2-3 sentences, be specific about next steps)

2. **Write a single JSON file** to `.plans/session-state.json`:

```json
{
  "timestamp": "[ISO timestamp]",
  "original_request": "[what user asked]",
  "current_task": "[what you're doing now]",
  "key_files": ["[file1]", "[file2]"],
  "continuation_prompt": "[Detailed instructions for continuing. Include: what's done, what's next, any blockers or gotchas discovered.]"
}
```

3. **Report completion** with the restore command.

## Quality Bar for continuation_prompt

The continuation_prompt is the most important field. It should enable a fresh agent to:
- Understand the goal immediately
- Know exactly what step to take next
- Avoid repeating completed work
- Be aware of any pitfalls discovered

**Example good prompt**: "User wants a REST API for todo items. Created GET /todos endpoint, tested working. Next: implement POST /todos with validation. Note: the db connection pool maxes at 10, discovered this causes timeouts under load."

**Example bad prompt**: "Working on API stuff."

## Output

After writing, say:

```
Session compacted to .plans/session-state.json

To restore after /clear:
/restore
```
