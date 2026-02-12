# ABOUTME: Constants and path resolution for agent-memory.
# ABOUTME: No external dependencies — stdlib only.

import os
from pathlib import Path

# Embedding model configuration
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
EMBEDDING_DIM = 384

# Chunk sizing (chars, not tokens — approx 4 chars/token)
CHUNK_MAX_CHARS = 1600
CHUNK_OVERLAP_CHARS = 320

# Search weights and thresholds
VECTOR_WEIGHT = 0.7
BM25_WEIGHT = 0.3
CANDIDATE_MULTIPLIER = 4
MIN_SCORE = 0.35
DEFAULT_LIMIT = 5


def get_memory_dir() -> Path:
    """Return the root memory directory, respecting AGENT_MEMORY_DIR env var."""
    env = os.environ.get("AGENT_MEMORY_DIR")
    if env:
        return Path(env)
    return Path.home() / ".claude" / "agent-memory"


def get_db_path() -> Path:
    """Return the SQLite database path, respecting AGENT_MEMORY_DB env var."""
    env = os.environ.get("AGENT_MEMORY_DB")
    if env:
        return Path(env)
    return get_memory_dir() / "memory.db"


def get_scan_patterns() -> list[str]:
    """Return glob patterns for all memory file locations."""
    home = Path.home()
    return [
        str(home / ".claude" / "projects" / "*" / "memory" / "MEMORY.md"),
        str(home / ".claude" / "agent-memory" / "daily-logs" / "*.md"),
        str(home / ".claude" / "agent-memory" / "sessions" / "*.md"),
    ]
