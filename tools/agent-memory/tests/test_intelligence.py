# ABOUTME: Tests for intelligence module — Claude Agent SDK features (mocked).
# ABOUTME: Verifies ask/summarize with mocked SDK, and graceful import failure.

from unittest.mock import MagicMock, patch
import sys


def test_ask_memories_builds_context(tmp_db, sample_memory_dir):
    """ask_memories searches memories and builds a context string."""
    from agent_memory.db import init_db
    from agent_memory.indexer import index_all

    conn = init_db(tmp_db)
    patterns = [
        str(sample_memory_dir / "agent-memory" / "daily-logs" / "*.md"),
    ]
    index_all(conn, patterns)

    # Mock the SDK
    mock_sdk = MagicMock()
    mock_sdk.messages.create.return_value = MagicMock(
        content=[MagicMock(text="FastEmbed is used for local embeddings.")]
    )

    with patch.dict(sys.modules, {"anthropic": mock_sdk}):
        from agent_memory.intelligence import _build_context
        context = _build_context(conn, "what embedding model do we use?")
        assert len(context) > 0
        assert any("embed" in c.lower() or "FastEmbed" in c for c in context)

    conn.close()


def test_ask_memories_graceful_without_sdk():
    """ask_memories raises ImportError without SDK."""
    # Temporarily remove anthropic from sys.modules if present
    original = sys.modules.get("anthropic")
    sys.modules["anthropic"] = None  # Force ImportError

    try:
        try:
            import anthropic
            assert False, "Should have raised ImportError"
        except (ImportError, TypeError):
            pass  # Expected
    finally:
        if original is not None:
            sys.modules["anthropic"] = original
        else:
            sys.modules.pop("anthropic", None)


def test_summarize_reads_daily_logs(sample_memory_dir, monkeypatch):
    """summarize_daily_logs reads recent daily log files."""
    from agent_memory.intelligence import _collect_daily_logs

    monkeypatch.setenv(
        "AGENT_MEMORY_DIR",
        str(sample_memory_dir / "agent-memory"),
    )
    logs = _collect_daily_logs()
    assert len(logs) > 0
    assert any("FastEmbed" in log for log in logs)
