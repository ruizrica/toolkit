# agent-memory

ABOUTME: Documentation for the agent-memory skill — local hybrid search over memory files.
ABOUTME: Covers installation, usage, when to use, and architecture.

## What is it?

A local hybrid search system that indexes your markdown memory files (`~/.claude/agent-memory/`) into SQLite and provides **combined vector + BM25 search** with zero API calls.

## Installation

```bash
pip3 install --break-system-packages -e ~/.toolkit/tools/agent-memory
agent-memory install    # Download embedding model (~67MB)
agent-memory index      # Initial indexing
```

The toolkit installer handles this automatically.

## When to Use

| Use agent-memory | Use Read tool | Use /restore |
|-----------------|---------------|--------------|
| Searching across all memories | Reading a specific known file | Resuming a session |
| "What did we decide about X?" | Checking a specific MEMORY.md | Loading session state |
| Finding patterns across logs | Reading today's daily log | Bootstrapping context |
| Cross-session topic recall | Viewing a single document | Continuing work |

## Quick Examples

```bash
# Hybrid search (default — best for most queries)
agent-memory search "authentication patterns"

# Vector-only (semantic similarity)
agent-memory search "how errors are handled" --vector

# Keyword-only (exact term matching)
agent-memory search "pyproject.toml" --keyword

# JSON output for parsing
agent-memory search "TDD" --limit 10 --json

# Reindex after new memory files appear
agent-memory index

# Check database stats
agent-memory status

# Add a memory manually
agent-memory add "Use --break-system-packages for PEP 668" --source daily --tags "pip,install"

# Q&A over memories (requires ANTHROPIC_API_KEY)
agent-memory ask "What testing patterns do we follow?"
```

## Skill File Location

Installed to `~/.claude/skills/agent-memory.md` — Claude reads this to understand when and how to use the tool.

## Architecture

| Component | Role |
|-----------|------|
| **FastEmbed** | Local embeddings via all-MiniLM-L6-v2 (~67MB) |
| **sqlite-vec** | Vector similarity search (SQLite extension) |
| **FTS5** | BM25 keyword search (built-in SQLite) |
| **Hybrid scoring** | 0.7 * vector + 0.3 * BM25 |

All data stored in `~/.claude/agent-memory/memory.db`. No network calls for search.

## See Also

- [/agent-memory command](../commands/agent-memory.md) — Full command documentation
- [just-bash](just-bash.md) — Another toolkit skill
