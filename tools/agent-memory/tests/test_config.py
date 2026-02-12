# ABOUTME: Tests for config module — path resolution and constants.
# ABOUTME: Verifies defaults, env overrides, and scan pattern generation.

from pathlib import Path


def test_default_memory_dir():
    """MEMORY_DIR defaults to ~/.claude/agent-memory/."""
    from agent_memory.config import get_memory_dir

    result = get_memory_dir()
    expected = Path.home() / ".claude" / "agent-memory"
    assert result == expected


def test_memory_dir_env_override(monkeypatch, tmp_path):
    """AGENT_MEMORY_DIR env var overrides default."""
    monkeypatch.setenv("AGENT_MEMORY_DIR", str(tmp_path))
    from agent_memory.config import get_memory_dir

    assert get_memory_dir() == tmp_path


def test_default_db_path():
    """DB lives inside MEMORY_DIR."""
    from agent_memory.config import get_db_path

    result = get_db_path()
    assert result.name == "memory.db"
    assert ".claude/agent-memory" in str(result)


def test_db_path_env_override(monkeypatch, tmp_path):
    """AGENT_MEMORY_DB env var overrides default."""
    custom_db = tmp_path / "custom.db"
    monkeypatch.setenv("AGENT_MEMORY_DB", str(custom_db))
    from agent_memory.config import get_db_path

    assert get_db_path() == custom_db


def test_embedding_constants():
    """Embedding config constants are set correctly."""
    from agent_memory.config import EMBEDDING_MODEL, EMBEDDING_DIM

    assert EMBEDDING_MODEL == "BAAI/bge-small-en-v1.5"
    assert EMBEDDING_DIM == 384


def test_chunk_constants():
    """Chunk size and overlap constants are set."""
    from agent_memory.config import CHUNK_MAX_CHARS, CHUNK_OVERLAP_CHARS

    assert CHUNK_MAX_CHARS == 1600
    assert CHUNK_OVERLAP_CHARS == 320


def test_search_constants():
    """Search weight and threshold constants are set."""
    from agent_memory.config import (
        VECTOR_WEIGHT,
        BM25_WEIGHT,
        MIN_SCORE,
        DEFAULT_LIMIT,
        CANDIDATE_MULTIPLIER,
    )

    assert VECTOR_WEIGHT == 0.7
    assert BM25_WEIGHT == 0.3
    assert MIN_SCORE == 0.35
    assert DEFAULT_LIMIT == 5
    assert CANDIDATE_MULTIPLIER == 4


def test_scan_patterns(monkeypatch, tmp_path):
    """Scan patterns resolve to correct glob patterns."""
    monkeypatch.setenv("HOME", str(tmp_path))
    from agent_memory.config import get_scan_patterns

    patterns = get_scan_patterns()
    assert len(patterns) == 3
    # Should contain patterns for MEMORY.md, daily-logs, sessions
    pattern_strs = [str(p) for p in patterns]
    assert any("MEMORY.md" in s for s in pattern_strs)
    assert any("daily-logs" in s for s in pattern_strs)
    assert any("sessions" in s for s in pattern_strs)
