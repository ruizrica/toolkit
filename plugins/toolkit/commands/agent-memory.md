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
/agent-memory code-index <path>  Index codebase for tree navigation
/agent-memory code-nav <query>   Navigate code tree to find code
/agent-memory code-tree          Display indexed code tree
/agent-memory code-refs <id>     Show cross-references for a node
/agent-memory code-summarize     Generate code node summaries
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

### Code Navigation

```bash
# Index a codebase (tree-sitter AST parsing, 165+ languages)
agent-memory code-index ./src

# Navigate to find relevant code
agent-memory code-nav "hybrid search" --json

# View the tree structure
agent-memory code-tree --json

# Generate summaries for better navigation
agent-memory code-summarize
```

Always use `--json` flag when processing results programmatically.

### First-Time Setup

If `agent-memory` is not installed:
```bash
pip3 install -e ~/.toolkit/tools/agent-memory
agent-memory install  # Download embedding model (~67MB)
agent-memory index    # Initial indexing
```
