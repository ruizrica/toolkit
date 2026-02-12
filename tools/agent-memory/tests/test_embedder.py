# ABOUTME: Tests for embedder module — FastEmbed wrapper with caching.
# ABOUTME: Verifies lazy loading, embedding dimensions, serialization, and content hashing.

import struct


def test_content_hash_deterministic():
    """Same text produces same hash."""
    from agent_memory.embedder import content_hash

    h1 = content_hash("hello world")
    h2 = content_hash("hello world")
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 hex


def test_content_hash_different_texts():
    """Different texts produce different hashes."""
    from agent_memory.embedder import content_hash

    h1 = content_hash("hello")
    h2 = content_hash("world")
    assert h1 != h2


def test_serialize_f32_roundtrip():
    """serialize_f32 produces correct binary format."""
    from agent_memory.embedder import serialize_f32

    vec = [1.0, 2.0, 3.0]
    blob = serialize_f32(vec)
    assert isinstance(blob, bytes)
    assert len(blob) == 3 * 4  # 3 floats * 4 bytes each

    # Roundtrip
    unpacked = struct.unpack(f"{len(vec)}f", blob)
    for a, b in zip(vec, unpacked):
        assert abs(a - b) < 1e-6


def test_embed_texts_returns_correct_shape():
    """embed_texts returns list of vectors with correct dimension."""
    from agent_memory.embedder import embed_texts
    from agent_memory.config import EMBEDDING_DIM

    texts = ["hello world", "test embedding"]
    vectors = embed_texts(texts)
    assert len(vectors) == 2
    assert len(vectors[0]) == EMBEDDING_DIM
    assert len(vectors[1]) == EMBEDDING_DIM


def test_embed_query_returns_correct_dim():
    """embed_query returns single vector with correct dimension."""
    from agent_memory.embedder import embed_query
    from agent_memory.config import EMBEDDING_DIM

    vec = embed_query("test query")
    assert len(vec) == EMBEDDING_DIM


def test_embed_texts_deterministic():
    """Same text produces same embedding."""
    from agent_memory.embedder import embed_texts

    v1 = embed_texts(["hello"])[0]
    v2 = embed_texts(["hello"])[0]
    # Should be identical (deterministic model)
    for a, b in zip(v1, v2):
        assert abs(a - b) < 1e-6


def test_embed_texts_empty_list():
    """Empty input returns empty list."""
    from agent_memory.embedder import embed_texts

    assert embed_texts([]) == []
