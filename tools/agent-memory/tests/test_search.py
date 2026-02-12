# ABOUTME: Tests for search module — BM25, vector, and hybrid search.
# ABOUTME: Verifies score normalization, fusion logic, and result quality.


def _index_sample(conn, sample_memory_dir):
    """Helper to index sample files for search tests."""
    from agent_memory.indexer import index_all

    patterns = [
        str(sample_memory_dir / "projects" / "*" / "memory" / "MEMORY.md"),
        str(sample_memory_dir / "agent-memory" / "daily-logs" / "*.md"),
        str(sample_memory_dir / "agent-memory" / "sessions" / "*.md"),
    ]
    index_all(conn, patterns)


def test_search_result_fields():
    """SearchResult has expected fields."""
    from agent_memory.search import SearchResult

    r = SearchResult(
        chunk_id="abc", text="hello", path="/test.md",
        source="daily", score=0.8, start_line=1, end_line=5,
    )
    assert r.chunk_id == "abc"
    assert r.score == 0.8


def test_keyword_search(tmp_db, sample_memory_dir):
    """Keyword (BM25) search finds matching text."""
    from agent_memory.db import init_db
    from agent_memory.search import search_keyword

    conn = init_db(tmp_db)
    _index_sample(conn, sample_memory_dir)

    results = search_keyword(conn, "FastEmbed")
    assert len(results) > 0
    assert any("FastEmbed" in r.text for r in results)
    conn.close()


def test_keyword_search_no_match(tmp_db, sample_memory_dir):
    """Keyword search returns empty for non-matching query."""
    from agent_memory.db import init_db
    from agent_memory.search import search_keyword

    conn = init_db(tmp_db)
    _index_sample(conn, sample_memory_dir)

    results = search_keyword(conn, "xyznonexistent12345")
    assert len(results) == 0
    conn.close()


def test_vector_search(tmp_db, sample_memory_dir):
    """Vector search finds semantically similar text."""
    from agent_memory.db import init_db, has_sqlite_vec
    from agent_memory.search import search_vector

    conn = init_db(tmp_db)
    if not has_sqlite_vec():
        conn.close()
        return

    _index_sample(conn, sample_memory_dir)

    results = search_vector(conn, "embedding model for text")
    assert len(results) > 0
    # Should find the chunk about FastEmbed embeddings
    assert any("embed" in r.text.lower() or "FastEmbed" in r.text for r in results)
    conn.close()


def test_hybrid_search(tmp_db, sample_memory_dir):
    """Hybrid search combines vector and keyword results."""
    from agent_memory.db import init_db, has_sqlite_vec
    from agent_memory.search import search_hybrid

    conn = init_db(tmp_db)
    if not has_sqlite_vec():
        conn.close()
        return

    _index_sample(conn, sample_memory_dir)

    results = search_hybrid(conn, "FastEmbed embeddings")
    assert len(results) > 0
    # Scores should be between 0 and 1
    for r in results:
        assert 0 <= r.score <= 1.0
    conn.close()


def test_hybrid_search_respects_limit(tmp_db, sample_memory_dir):
    """Hybrid search returns at most `limit` results."""
    from agent_memory.db import init_db, has_sqlite_vec
    from agent_memory.search import search_hybrid

    conn = init_db(tmp_db)
    if not has_sqlite_vec():
        conn.close()
        return

    _index_sample(conn, sample_memory_dir)

    results = search_hybrid(conn, "test", limit=1)
    assert len(results) <= 1
    conn.close()


def test_search_scores_sorted_descending(tmp_db, sample_memory_dir):
    """Search results are sorted by score descending."""
    from agent_memory.db import init_db, has_sqlite_vec
    from agent_memory.search import search_hybrid

    conn = init_db(tmp_db)
    if not has_sqlite_vec():
        conn.close()
        return

    _index_sample(conn, sample_memory_dir)

    results = search_hybrid(conn, "TDD testing")
    if len(results) >= 2:
        for i in range(len(results) - 1):
            assert results[i].score >= results[i + 1].score
    conn.close()
