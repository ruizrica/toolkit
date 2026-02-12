# /agent-memory

ABOUTME: Documentation for the /agent-memory command — hybrid search over agent memory files.
ABOUTME: Covers usage, arguments, architecture, search modes, examples, and setup.

Search and manage the local agent memory system using hybrid search. Fully local — zero API calls for core features.

## Usage

```bash
/agent-memory <subcommand> [args]
```

## Subcommands

| Subcommand | Description |
|------------|-------------|
| `search <query>` | Search memories (hybrid by default) |
| `index` | Reindex all memory files |
| `status` | Show database status |
| `add <content>` | Add a memory manually |
| `get <id>` | Get a memory by chunk ID |
| `list` | List stored memories |
| `ask <question>` | Q&A over memories (requires `ANTHROPIC_API_KEY`) |
| `summarize` | Consolidate daily logs (requires `ANTHROPIC_API_KEY`) |
| `install` | Download embedding model (~67MB) |

## Arguments

### search

| Argument | Required | Description |
|----------|----------|-------------|
| `query` | Yes | Search query text |
| `--vector` | No | Vector-only search (semantic similarity) |
| `--keyword` | No | BM25-only search (exact term matching) |
| `--limit N` | No | Max results (default: 5) |
| `--json` | No | JSON output |

### index

| Argument | Required | Description |
|----------|----------|-------------|
| `--path` | No | Specific path to index (default: all memory dirs) |

### add

| Argument | Required | Description |
|----------|----------|-------------|
| `content` | Yes | Memory content text |
| `--tags` | No | Comma-separated tags |
| `--source` | No | Source type (default: manual) |

### list

| Argument | Required | Description |
|----------|----------|-------------|
| `--source` | No | Filter by source type |
| `--limit N` | No | Max results (default: 20) |
| `--json` | No | JSON output |

## Architecture

```
~/.claude/agent-memory/          ← Memory files (daily logs, sessions)
~/.claude/projects/*/memory/     ← Project MEMORY.md files

        │  agent-memory index
        ▼
┌─────────────────────────────────────────┐
│            Indexer                       │
│  Scan → Chunk → Embed → Store           │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│          SQLite Database                │
│  ┌───────────┐ ┌──────────┐ ┌────────┐ │
│  │sqlite-vec │ │  FTS5    │ │  meta  │ │
│  │(vectors)  │ │(BM25)    │ │(files) │ │
│  └───────────┘ └──────────┘ └────────┘ │
└────────────────┬────────────────────────┘
                 │
        agent-memory search
                 │
                 ▼
┌─────────────────────────────────────────┐
│         Hybrid Search                   │
│  0.7 × vector_score + 0.3 × bm25_score │
└─────────────────────────────────────────┘
```

### Components

| Component | Purpose |
|-----------|---------|
| **FastEmbed** | Local embedding model (all-MiniLM-L6-v2, ~67MB) |
| **sqlite-vec** | Vector similarity search via SQLite extension |
| **FTS5** | Built-in SQLite full-text search (BM25 scoring) |

## Search Modes

| Mode | Flag | Best For |
|------|------|----------|
| **Hybrid** (default) | _(none)_ | Most queries — combines semantic + keyword |
| **Vector** | `--vector` | Conceptual/semantic queries ("authentication patterns") |
| **Keyword** | `--keyword` | Exact term matching ("JWT", "pyproject.toml") |

## Examples

```bash
# Search with default hybrid mode
/agent-memory search "TDD workflow"

# Semantic search for conceptual matches
/agent-memory search "how we handle errors" --vector

# Exact keyword matching
/agent-memory search "pyproject.toml" --keyword

# JSON output for programmatic use
/agent-memory search "deployment" --limit 10 --json

# Reindex after adding new memory files
/agent-memory index

# Check what's indexed
/agent-memory status

# Add a key decision as a memory
/agent-memory add "Always use --break-system-packages for Homebrew Python" --tags "pip,install" --source daily

# Q&A over memories (requires ANTHROPIC_API_KEY)
/agent-memory ask "What testing patterns do we use?"
```

## First-Time Setup

```bash
pip3 install --break-system-packages -e ~/.toolkit/tools/agent-memory
agent-memory install    # Download embedding model (~67MB)
agent-memory index      # Initial indexing
```

The toolkit installer (`install.sh`) handles this automatically.

## When to Use

- **Searching past context** — Find relevant memories before starting a task
- **Before `/restore`** — Search for specific topics across all daily logs and sessions
- **Cross-session recall** — "What did we decide about X?" instead of scrolling
- **Adding structured memories** — Store key decisions/patterns for retrieval

## When NOT to Use

- For reading a specific known file — use `Read` tool directly
- For writing to MEMORY.md — edit the file directly
- For session state management — use `/compact` and `/restore`

## See Also

- [agent-memory skill](../skills/agent-memory.md) — Skill reference file for Claude
- [/compact](compact.md) — Session compact with daily log writes
- [/restore](restore.md) — Restore session with daily log bootstrap
