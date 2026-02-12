# ABOUTME: FastEmbed wrapper for local text embedding with lazy loading.
# ABOUTME: Provides embed_texts, embed_query, serialization, and content hashing.

import hashlib
import struct

from .config import EMBEDDING_MODEL

# Lazy-loaded singleton
_model = None


def _get_model():
    """Load the FastEmbed model on first use."""
    global _model
    if _model is None:
        from fastembed import TextEmbedding
        _model = TextEmbedding(model_name=EMBEDDING_MODEL)
    return _model


def content_hash(text: str) -> str:
    """Return SHA-256 hex digest of text for cache keying."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def serialize_f32(vector: list[float]) -> bytes:
    """Pack a float vector into compact binary for sqlite-vec storage."""
    return struct.pack(f"{len(vector)}f", *vector)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Batch embed texts, returning list of float vectors."""
    if not texts:
        return []
    model = _get_model()
    embeddings = list(model.embed(texts))
    return [emb.tolist() for emb in embeddings]


def embed_query(text: str) -> list[float]:
    """Embed a single query text, returning a float vector."""
    model = _get_model()
    embeddings = list(model.query_embed(text))
    return embeddings[0].tolist()
