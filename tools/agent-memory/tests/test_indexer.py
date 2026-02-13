# ABOUTME: Tests for indexer module — file discovery, change detection, and indexing pipeline.
# ABOUTME: Verifies scan → chunk → embed → store workflow with change detection.

from pathlib import Path


def test_classify_source():
    """classify_source returns correct source type based on path."""
    from agent_memory.indexer import classify_source

    assert classify_source("/home/.agent-memory/daily-logs/2026.md") == "daily"
    assert classify_source("/home/.agent-memory/sessions/snap.md") == "session"
    assert classify_source("/home/.claude/projects/foo/memory/MEMORY.md") == "memory"
    assert classify_source("/some/other/file.md") == "other"


def test_discover_files(sample_memory_dir):
    """discover_files finds markdown files matching scan patterns."""
    from agent_memory.indexer import discover_files

    patterns = [
        str(sample_memory_dir / "projects" / "*" / "memory" / "MEMORY.md"),
        str(sample_memory_dir / "agent-memory" / "daily-logs" / "*.md"),
        str(sample_memory_dir / "agent-memory" / "sessions" / "*.md"),
    ]
    files = discover_files(patterns)
    assert len(files) == 3
    paths = {f.name for f in files}
    assert "2026-02-11.md" in paths
    assert "MEMORY.md" in paths


def test_index_all_creates_chunks(tmp_db, sample_memory_dir):
    """index_all indexes files and creates chunks in the database."""
    from agent_memory.db import init_db
    from agent_memory.indexer import index_all

    conn = init_db(tmp_db)
    patterns = [
        str(sample_memory_dir / "projects" / "*" / "memory" / "MEMORY.md"),
        str(sample_memory_dir / "agent-memory" / "daily-logs" / "*.md"),
        str(sample_memory_dir / "agent-memory" / "sessions" / "*.md"),
    ]
    stats = index_all(conn, patterns)
    assert stats.files_indexed > 0
    assert stats.chunks_created > 0

    # Verify chunks exist in DB
    cursor = conn.execute("SELECT COUNT(*) FROM chunks")
    assert cursor.fetchone()[0] > 0
    conn.close()


def test_index_all_records_files(tmp_db, sample_memory_dir):
    """index_all records file metadata for change detection."""
    from agent_memory.db import init_db
    from agent_memory.indexer import index_all

    conn = init_db(tmp_db)
    patterns = [
        str(sample_memory_dir / "agent-memory" / "daily-logs" / "*.md"),
    ]
    index_all(conn, patterns)

    cursor = conn.execute("SELECT COUNT(*) FROM files")
    assert cursor.fetchone()[0] == 1
    conn.close()


def test_index_all_skips_unchanged(tmp_db, sample_memory_dir):
    """Running index_all twice on unchanged files skips re-indexing."""
    from agent_memory.db import init_db
    from agent_memory.indexer import index_all

    conn = init_db(tmp_db)
    patterns = [
        str(sample_memory_dir / "agent-memory" / "daily-logs" / "*.md"),
    ]
    stats1 = index_all(conn, patterns)
    stats2 = index_all(conn, patterns)

    assert stats1.files_indexed == 1
    assert stats2.files_skipped == 1
    assert stats2.files_indexed == 0
    conn.close()


def test_index_all_reindexes_changed(tmp_db, sample_memory_dir):
    """Modified file is re-indexed on second run."""
    from agent_memory.db import init_db
    from agent_memory.indexer import index_all

    conn = init_db(tmp_db)
    daily = sample_memory_dir / "agent-memory" / "daily-logs" / "2026-02-11.md"
    patterns = [str(sample_memory_dir / "agent-memory" / "daily-logs" / "*.md")]

    index_all(conn, patterns)

    # Modify the file
    daily.write_text("# 2026-02-11\n\nCompletely new content about refactoring.\n")

    stats2 = index_all(conn, patterns)
    assert stats2.files_indexed == 1
    assert stats2.files_skipped == 0
    conn.close()


def test_index_all_populates_fts(tmp_db, sample_memory_dir):
    """index_all populates the FTS5 table for keyword search."""
    from agent_memory.db import init_db
    from agent_memory.indexer import index_all

    conn = init_db(tmp_db)
    patterns = [
        str(sample_memory_dir / "agent-memory" / "daily-logs" / "*.md"),
    ]
    index_all(conn, patterns)

    cursor = conn.execute(
        "SELECT COUNT(*) FROM chunks_fts WHERE chunks_fts MATCH 'FastEmbed'"
    )
    assert cursor.fetchone()[0] > 0
    conn.close()


def test_index_all_populates_vec(tmp_db, sample_memory_dir):
    """index_all populates the vec0 table for vector search."""
    from agent_memory.db import init_db, has_sqlite_vec
    from agent_memory.indexer import index_all

    conn = init_db(tmp_db)
    if not has_sqlite_vec():
        conn.close()
        return

    patterns = [
        str(sample_memory_dir / "agent-memory" / "daily-logs" / "*.md"),
    ]
    index_all(conn, patterns)

    cursor = conn.execute("SELECT COUNT(*) FROM chunks_vec")
    assert cursor.fetchone()[0] > 0
    conn.close()


def test_index_stats_fields(tmp_db, sample_memory_dir):
    """IndexStats has expected fields."""
    from agent_memory.db import init_db
    from agent_memory.indexer import index_all

    conn = init_db(tmp_db)
    patterns = [
        str(sample_memory_dir / "agent-memory" / "daily-logs" / "*.md"),
    ]
    stats = index_all(conn, patterns)
    assert hasattr(stats, "files_indexed")
    assert hasattr(stats, "files_skipped")
    assert hasattr(stats, "chunks_created")
    conn.close()
