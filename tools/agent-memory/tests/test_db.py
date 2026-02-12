# ABOUTME: Tests for db module — SQLite schema creation and helper functions.
# ABOUTME: Verifies table creation, sqlite-vec loading, and meta CRUD.

def test_init_db_creates_tables(tmp_db):
    """init_db creates all required tables."""
    from agent_memory.db import init_db

    conn = init_db(tmp_db)
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    tables = {row[0] for row in cursor.fetchall()}
    conn.close()

    assert "chunks" in tables
    assert "files" in tables
    assert "embedding_cache" in tables
    assert "meta" in tables


def test_init_db_creates_fts(tmp_db):
    """init_db creates FTS5 virtual table."""
    from agent_memory.db import init_db

    conn = init_db(tmp_db)
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='chunks_fts'"
    )
    assert cursor.fetchone() is not None
    conn.close()


def test_init_db_creates_vec_table(tmp_db):
    """init_db creates vec0 virtual table if sqlite-vec is available."""
    from agent_memory.db import init_db, has_sqlite_vec

    conn = init_db(tmp_db)
    if has_sqlite_vec():
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='chunks_vec'"
        )
        assert cursor.fetchone() is not None
    conn.close()


def test_init_db_is_idempotent(tmp_db):
    """Calling init_db twice doesn't error."""
    from agent_memory.db import init_db

    conn1 = init_db(tmp_db)
    conn1.close()
    conn2 = init_db(tmp_db)
    conn2.close()


def test_meta_set_and_get(tmp_db):
    """meta_set / meta_get roundtrip works."""
    from agent_memory.db import init_db, meta_set, meta_get

    conn = init_db(tmp_db)
    meta_set(conn, "test_key", "test_value")
    assert meta_get(conn, "test_key") == "test_value"
    conn.close()


def test_meta_get_default(tmp_db):
    """meta_get returns default for missing keys."""
    from agent_memory.db import init_db, meta_get

    conn = init_db(tmp_db)
    assert meta_get(conn, "nonexistent") is None
    assert meta_get(conn, "nonexistent", "fallback") == "fallback"
    conn.close()


def test_meta_set_overwrites(tmp_db):
    """meta_set overwrites existing value."""
    from agent_memory.db import init_db, meta_set, meta_get

    conn = init_db(tmp_db)
    meta_set(conn, "key", "v1")
    meta_set(conn, "key", "v2")
    assert meta_get(conn, "key") == "v2"
    conn.close()


def test_chunks_table_schema(tmp_db):
    """chunks table has expected columns."""
    from agent_memory.db import init_db

    conn = init_db(tmp_db)
    cursor = conn.execute("PRAGMA table_info(chunks)")
    columns = {row[1] for row in cursor.fetchall()}
    conn.close()

    expected = {
        "id", "path", "source", "start_line", "end_line",
        "hash", "model", "text", "created_at", "updated_at",
    }
    assert expected.issubset(columns)


def test_files_table_schema(tmp_db):
    """files table has expected columns."""
    from agent_memory.db import init_db

    conn = init_db(tmp_db)
    cursor = conn.execute("PRAGMA table_info(files)")
    columns = {row[1] for row in cursor.fetchall()}
    conn.close()

    expected = {"path", "hash", "mtime", "size"}
    assert expected.issubset(columns)
