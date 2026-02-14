# Agent Toolkit — Project Memory

## Persistent memory

Use **agent-memory** in this repo as the persistent memory system. Run from project root so `.agent-memory/` and its DB are used.

- **Memory search:** `agent-memory search "query"` (hybrid), `--vector` or `--keyword`
- **Code navigation:** `agent-memory code-index .`, `agent-memory code-nav "query"`, `agent-memory code-tree`, `agent-memory code-refs <id>`
- **Setup/refresh:** `agent-memory index`, `agent-memory code-index .`, `agent-memory install` (embedding model)
- **Add fact:** `agent-memory add "content" --source daily --tags "tag1,tag2"`

Stable facts go here (MEMORY.md). Session context goes to daily logs; `/compact` writes them. Index after changes: `agent-memory index`.
