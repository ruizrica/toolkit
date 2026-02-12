---
name: agent-memory
description: Search and manage agent memories with hybrid (vector + BM25) search
---

# /agent-memory

Search and manage the local agent memory system using hybrid search.

## Usage

```
/agent-memory search <query>     Search memories (hybrid by default)
/agent-memory index              Reindex all memory files
/agent-memory status             Show database status
/agent-memory add <content>      Add a memory manually
```

## Implementation

When the user runs `/agent-memory`, execute the appropriate `agent-memory` CLI command:

1. **Parse the subcommand** from the user's input
2. **Run the command** using Bash: `agent-memory <subcommand> [args]`
3. **Display results** to the user

### Examples

```bash
# User: /agent-memory search "authentication patterns"
agent-memory search "authentication patterns" --json

# User: /agent-memory index
agent-memory index

# User: /agent-memory status
agent-memory status --json

# User: /agent-memory add "Always validate JWT tokens server-side"
agent-memory add "Always validate JWT tokens server-side" --source memory --tags "security,auth"
```

### Search Modes

- Default (hybrid): `agent-memory search "query"` — best for most queries
- Vector only: `agent-memory search "query" --vector` — semantic similarity
- Keyword only: `agent-memory search "query" --keyword` — exact term matching

Always use `--json` flag when processing results programmatically.

### First-Time Setup

If `agent-memory` is not installed:
```bash
pip3 install -e ~/.toolkit/tools/agent-memory
agent-memory install  # Download embedding model (~67MB)
agent-memory index    # Initial indexing
```
