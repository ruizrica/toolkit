![memory](assets/memory.png)

Created by Ricardo Ruiz - 2026
ruizrica.io

Local hybrid search (vector + BM25) over Claude Code memory files. Zero API calls.

## Installation

```bash
pip3 install --break-system-packages -e tools/agent-memory
agent-memory install    # Download embedding model (~67MB)
```

## Quick Start

```bash
agent-memory index                        # Index all memory files
agent-memory search "authentication"      # Hybrid search (default)
agent-memory search "JWT" --keyword       # Exact keyword match
agent-memory search "error handling" --vector  # Semantic similarity
```

## Commands

| Command | Description |
|---------|-------------|
| `search <query>` | Hybrid search (0.7 vector + 0.3 BM25) |
| `search <query> --vector` | Vector-only (semantic similarity) |
| `search <query> --keyword` | BM25-only (exact term matching) |
| `index` | Reindex all memory files |
| `index --path <dir>` | Index a specific path |
| `status` | Show database stats (files, chunks, size) |
| `add <content>` | Add a memory (`--tags`, `--source`) |
| `get <id>` | Get a memory by chunk ID |
| `list` | List memories (`--source`, `--limit`) |
| `ask <question>` | Q&A over memories (requires `ANTHROPIC_API_KEY`) |
| `summarize` | Consolidate daily logs (requires `ANTHROPIC_API_KEY`) |
| `install` | Download embedding model (~67MB) |
| `code-index <path>` | Build code tree from a codebase |
| `code-nav <query>` | Navigate code tree to find relevant code |
| `code-tree` | Display indexed code tree structure |
| `code-refs <node-id>` | Show cross-references for a code node |
| `code-summarize` | Generate summaries for indexed code nodes |

All commands support `--json` for machine-readable output where applicable.

## Architecture

### Memory Search Pipeline

```
Memory files (*.md)
        │
        ▼  index
┌──────────────────┐
│     Indexer       │  Scan → Chunk → Embed (FastEmbed)
└────────┬─────────┘
         ▼
┌──────────────────┐
│  SQLite Database  │
│  ├─ sqlite-vec   │  Vector similarity search
│  ├─ FTS5         │  BM25 keyword search
│  └─ meta/files   │  File tracking & dedup
└────────┬─────────┘
         ▼  search
┌──────────────────┐
│  Hybrid Ranker   │  0.7 × vector + 0.3 × BM25
└──────────────────┘
```

### Code Navigation Pipeline

```
Source files (*.py, *.ts, *.js, ...)
        │
        ▼  code-index
┌──────────────────────┐
│    Code Indexer       │  Discover → Parse (tree-sitter) → Store
└────────┬─────────────┘
         ▼
┌──────────────────────┐
│  Code Tree (SQLite)  │
│  ├─ code_nodes       │  Classes, functions, imports
│  ├─ code_nodes_fts   │  FTS5 on names/signatures/docs
│  └─ code_refs        │  Cross-references
└────────┬─────────────┘
         ▼  code-nav
┌──────────────────────┐
│  Navigator           │  FTS beam search (width=3)
└──────────────────────┘
```

### Key Components

- **FastEmbed** — Local embedding model (all-MiniLM-L6-v2, ~67MB). No API calls.
- **sqlite-vec** — Vector similarity search via SQLite extension.
- **FTS5** — Built-in SQLite full-text search with BM25 scoring.
- **tree-sitter** — Accurate AST parsing for 165+ languages via tree-sitter-language-pack.
- **Lazy imports** — Heavy deps (fastembed, sqlite-vec, tree-sitter) load only when needed. `status` is instant.

### What Gets Indexed

| Location | Content |
|----------|---------|
| `<cwd>/.agent-memory/daily-logs/` | Daily session logs |
| `<cwd>/.agent-memory/sessions/` | Session snapshots |
| `<cwd>/.agent-memory/projects/*/memory/MEMORY.md` | Project semantic memory |

You can override discovery and database locations with:
- `AGENT_MEMORY_DIR` for the scan root.
- `AGENT_MEMORY_DB` for the SQLite DB file path.

## Development

```bash
# Install dev dependencies
pip3 install --break-system-packages -e "tools/agent-memory[dev]"

# Run tests
cd tools/agent-memory
python3 -m pytest tests/ -q

# Run specific test module
python3 -m pytest tests/test_search.py -v
```

### Project Structure

```
tools/agent-memory/
├── pyproject.toml
├── src/agent_memory/
│   ├── __init__.py
│   ├── cli.py           # CLI entry point (argparse, lazy imports)
│   ├── config.py        # Paths, scan patterns
│   ├── db.py            # SQLite + sqlite-vec + FTS5 init
│   ├── embedder.py      # FastEmbed wrapper
│   ├── indexer.py       # Memory file scanning, chunking, embedding
│   ├── search.py        # Hybrid, vector, keyword search
│   ├── crud.py          # Add/get/list operations
│   ├── intelligence.py  # ask/summarize (optional, needs Agent SDK)
│   ├── parser.py        # Tree-sitter code structure extraction
│   ├── tree.py          # Code tree storage/retrieval in SQLite
│   ├── code_indexer.py  # Code discovery, parsing, tree storage
│   ├── navigator.py     # FTS-based beam search tree descent
│   └── summarizer.py    # Bottom-up code summary generation
└── tests/
    ├── test_cli.py, test_cli_code.py
    ├── test_db.py, test_config.py
    ├── test_search.py, test_indexer.py
    ├── test_crud.py, test_intelligence.py
    ├── test_parser.py, test_tree.py
    ├── test_code_indexer.py, test_navigator.py
    └── test_summarizer.py
```

## Code Navigation

Tree-based code navigation indexes any codebase into a hierarchical tree of classes, functions, and imports using tree-sitter AST parsing. Unlike flat search, this preserves the structure (repo → files → classes → methods) and lets agents navigate rather than just search.

```bash
# Index a codebase
agent-memory code-index ./src

# Navigate to find relevant code
agent-memory code-nav "hybrid search"
# → Navigates tree to find search.py:search_hybrid with full trace

# View the indexed tree
agent-memory code-tree --json

# Generate summaries for better navigation
agent-memory code-summarize

# Show cross-references for a node
agent-memory code-refs 42
```

### Supported Languages

Python, TypeScript, JavaScript (TSX/JSX), Rust, Go, Java, Ruby, C/C++, C#, Swift, Kotlin, Lua, Bash — and all other tree-sitter-language-pack supported languages (165+).

### How Navigation Works

1. **Index**: tree-sitter parses source files into ASTs, extracting classes, functions, imports
2. **Store**: Nodes stored in SQLite with parent-child relationships and FTS5 index
3. **Navigate**: FTS-based beam search (width=3) descends the tree, scoring nodes at each level
4. **Trace**: Returns the full navigation path for debuggability

## Requirements

- Python >= 3.10
- fastembed >= 0.4.0
- sqlite-vec >= 0.1.0
- tree-sitter >= 0.24.0
- tree-sitter-language-pack >= 0.7.0
- Optional: claude-agent-sdk >= 0.1.30 (for `ask`/`summarize`)
