# agent-memory

ABOUTME: Package README for agent-memory — local hybrid search CLI for Claude Code memory files.
ABOUTME: Covers installation, quick start, all commands, architecture, and development.

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

All commands support `--json` for machine-readable output where applicable.

## Architecture

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

### Key Components

- **FastEmbed** — Local embedding model (all-MiniLM-L6-v2, ~67MB). No API calls.
- **sqlite-vec** — Vector similarity search via SQLite extension.
- **FTS5** — Built-in SQLite full-text search with BM25 scoring.
- **Lazy imports** — Heavy deps (fastembed, sqlite-vec) load only when needed. `status` is instant.

### What Gets Indexed

| Location | Content |
|----------|---------|
| `~/.claude/agent-memory/daily-logs/` | Daily session logs |
| `~/.claude/agent-memory/sessions/` | Session snapshots |
| `~/.claude/projects/*/memory/MEMORY.md` | Project semantic memory |

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
│   ├── cli.py          # CLI entry point (argparse, lazy imports)
│   ├── config.py       # Paths, scan patterns
│   ├── db.py           # SQLite + sqlite-vec + FTS5 init
│   ├── embedder.py     # FastEmbed wrapper
│   ├── indexer.py       # File scanning, chunking, embedding
│   ├── search.py       # Hybrid, vector, keyword search
│   ├── crud.py         # Add/get/list operations
│   └── intelligence.py # ask/summarize (optional, needs Agent SDK)
└── tests/
    ├── test_cli.py
    ├── test_db.py
    ├── test_search.py
    ├── test_indexer.py
    ├── test_crud.py
    └── test_intelligence.py
```

## Requirements

- Python >= 3.10
- fastembed >= 0.4.0
- sqlite-vec >= 0.1.0
- Optional: claude-agent-sdk >= 0.1.30 (for `ask`/`summarize`)
