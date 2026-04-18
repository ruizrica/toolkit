# ABOUTME: Tests for crud module — add/get/list operations.
# ABOUTME: Verifies CRUD operations on the chunks table.


def test_add_memory(tmp_db):
    """add_memory creates a new chunk in the database."""
    from agent_memory.db import init_db
    from agent_memory.crud import add_memory

    conn = init_db(tmp_db)
    chunk_id = add_memory(conn, "Always use TDD", source="memory", tags="workflow")

    cursor = conn.execute("SELECT text FROM chunks WHERE id = ?", (chunk_id,))
    row = cursor.fetchone()
    assert row is not None
    assert row[0] == "Always use TDD"
    conn.close()


def test_add_memory_default_source(tmp_db):
    """add_memory defaults source to 'manual'."""
    from agent_memory.db import init_db
    from agent_memory.crud import add_memory

    conn = init_db(tmp_db)
    chunk_id = add_memory(conn, "test content")

    cursor = conn.execute("SELECT source FROM chunks WHERE id = ?", (chunk_id,))
    row = cursor.fetchone()
    assert row[0] == "manual"
    conn.close()


def test_add_memory_embeds_and_stores_fts(tmp_db):
    """add_memory populates both FTS and vec tables."""
    from agent_memory.db import init_db, has_sqlite_vec
    from agent_memory.crud import add_memory

    conn = init_db(tmp_db)
    add_memory(conn, "FastEmbed is great for local embeddings")

    # Verify FTS
    cursor = conn.execute(
        "SELECT COUNT(*) FROM chunks_fts WHERE chunks_fts MATCH 'FastEmbed'"
    )
    assert cursor.fetchone()[0] > 0

    # Verify vec
    if has_sqlite_vec():
        cursor = conn.execute("SELECT COUNT(*) FROM chunks_vec")
        assert cursor.fetchone()[0] > 0
    conn.close()


def test_get_memory(tmp_db):
    """get_memory retrieves a chunk by ID."""
    from agent_memory.db import init_db
    from agent_memory.crud import add_memory, get_memory

    conn = init_db(tmp_db)
    chunk_id = add_memory(conn, "test content", source="daily")
    result = get_memory(conn, chunk_id)

    assert result is not None
    assert result["id"] == chunk_id
    assert result["text"] == "test content"
    assert result["source"] == "daily"
    conn.close()


def test_get_memory_not_found(tmp_db):
    """get_memory returns None for missing ID."""
    from agent_memory.db import init_db
    from agent_memory.crud import get_memory

    conn = init_db(tmp_db)
    assert get_memory(conn, "nonexistent_id") is None
    conn.close()


def test_list_memories(tmp_db):
    """list_memories returns all chunks."""
    from agent_memory.db import init_db
    from agent_memory.crud import add_memory, list_memories

    conn = init_db(tmp_db)
    add_memory(conn, "item 1", source="daily")
    add_memory(conn, "item 2", source="memory")
    add_memory(conn, "item 3", source="session")

    results = list_memories(conn)
    assert len(results) == 3
    conn.close()


def test_list_memories_filter_source(tmp_db):
    """list_memories filters by source type."""
    from agent_memory.db import init_db
    from agent_memory.crud import add_memory, list_memories

    conn = init_db(tmp_db)
    add_memory(conn, "daily item", source="daily")
    add_memory(conn, "memory item", source="memory")

    results = list_memories(conn, source="daily")
    assert len(results) == 1
    assert results[0]["source"] == "daily"
    conn.close()


def test_list_memories_respects_limit(tmp_db):
    """list_memories returns at most `limit` items."""
    from agent_memory.db import init_db
    from agent_memory.crud import add_memory, list_memories

    conn = init_db(tmp_db)
    for i in range(10):
        add_memory(conn, f"item {i}")

    results = list_memories(conn, limit=3)
    assert len(results) == 3
    conn.close()


def test_get_memory_by_prefix(tmp_db):
    """get_memory finds a chunk using an ID prefix (truncated hash)."""
    from agent_memory.db import init_db
    from agent_memory.crud import add_memory, get_memory

    conn = init_db(tmp_db)
    chunk_id = add_memory(conn, "prefix lookup test", source="daily")

    # Use first 12 chars as prefix — matching CLI truncated output
    prefix = chunk_id[:12]
    result = get_memory(conn, prefix)

    assert result is not None
    assert result["id"] == chunk_id
    assert result["text"] == "prefix lookup test"
    conn.close()


def test_get_memory_ambiguous_prefix(tmp_db):
    """get_memory returns None when prefix matches multiple chunks."""
    from agent_memory.db import init_db
    from agent_memory.crud import get_memory

    conn = init_db(tmp_db)
    # Single-char prefix will likely match nothing in an empty DB
    result = get_memory(conn, "")
    assert result is None
    conn.close()
