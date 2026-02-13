# ABOUTME: Hybrid search engine combining vector similarity and BM25 keyword search.
# ABOUTME: Supports vector-only, keyword-only, and hybrid (0.7/0.3) search modes.

import sqlite3
from dataclasses import dataclass

from .config import (
    BM25_WEIGHT,
    CANDIDATE_MULTIPLIER,
    DEFAULT_LIMIT,
    MIN_SCORE,
    VECTOR_WEIGHT,
)
from .db import has_sqlite_vec
from .embedder import embed_query, serialize_f32


@dataclass
class SearchResult:
    """A single search result with score and metadata."""
    chunk_id: str
    text: str
    path: str
    source: str
    score: float
    start_line: int
    end_line: int


def _row_to_result(row: tuple, score: float) -> SearchResult:
    """Convert a DB row + score to a SearchResult."""
    return SearchResult(
        chunk_id=row[0],
        text=row[1],
        path=row[2],
        source=row[3],
        score=score,
        start_line=row[4],
        end_line=row[5],
    )


def _sanitize_fts_query(query: str) -> str:
    """Escape a user query for safe use with FTS5 MATCH.

    Wraps each whitespace-delimited token in double quotes so that
    hyphens, plus signs, and other FTS5 operators are treated as
    literal characters rather than query syntax.
    """
    tokens = query.split()
    if not tokens:
        return '""'
    # Quote each token individually; FTS5 treats adjacent quoted
    # strings as implicit AND.
    return " ".join(f'"{t}"' for t in tokens)


def _fetch_chunk_by_rowid(conn: sqlite3.Connection, rowid: int) -> tuple | None:
    """Fetch chunk data by rowid."""
    cursor = conn.execute(
        "SELECT id, text, path, source, start_line, end_line "
        "FROM chunks WHERE rowid = ?",
        (rowid,),
    )
    return cursor.fetchone()


def search_keyword(
    conn: sqlite3.Connection,
    query: str,
    limit: int = DEFAULT_LIMIT,
) -> list[SearchResult]:
    """BM25 keyword search using FTS5.

    Returns results sorted by relevance score (descending).
    """
    safe_query = _sanitize_fts_query(query)
    n_candidates = limit * CANDIDATE_MULTIPLIER
    cursor = conn.execute(
        "SELECT rowid, rank FROM chunks_fts WHERE chunks_fts MATCH ? "
        "ORDER BY rank LIMIT ?",
        (safe_query, n_candidates),
    )
    rows = cursor.fetchall()

    results = []
    for rowid, rank in rows:
        score = 1.0 / (1.0 + abs(rank))
        chunk = _fetch_chunk_by_rowid(conn, rowid)
        if chunk:
            results.append(_row_to_result(chunk, score))

    results.sort(key=lambda r: r.score, reverse=True)
    return results[:limit]


def search_vector(
    conn: sqlite3.Connection,
    query: str,
    limit: int = DEFAULT_LIMIT,
) -> list[SearchResult]:
    """Vector similarity search using sqlite-vec.

    Returns results sorted by cosine similarity (descending).
    """
    if not has_sqlite_vec():
        return []

    query_vec = embed_query(query)
    query_blob = serialize_f32(query_vec)
    n_candidates = limit * CANDIDATE_MULTIPLIER

    cursor = conn.execute(
        "SELECT rowid, distance FROM chunks_vec "
        "WHERE embedding MATCH ? ORDER BY distance LIMIT ?",
        (query_blob, n_candidates),
    )
    rows = cursor.fetchall()

    results = []
    for rowid, distance in rows:
        score = 1.0 - distance  # cosine distance → similarity
        chunk = _fetch_chunk_by_rowid(conn, rowid)
        if chunk:
            results.append(_row_to_result(chunk, score))

    results.sort(key=lambda r: r.score, reverse=True)
    return results[:limit]


def search_hybrid(
    conn: sqlite3.Connection,
    query: str,
    limit: int = DEFAULT_LIMIT,
    vector_weight: float = VECTOR_WEIGHT,
    bm25_weight: float = BM25_WEIGHT,
    min_score: float = MIN_SCORE,
) -> list[SearchResult]:
    """Hybrid search combining vector and BM25 scores.

    Score = vector_weight * vector_score + bm25_weight * bm25_score
    Filters results below min_score threshold.
    """
    n_candidates = limit * CANDIDATE_MULTIPLIER

    # Gather BM25 scores
    safe_query = _sanitize_fts_query(query)
    bm25_scores: dict[int, float] = {}
    try:
        cursor = conn.execute(
            "SELECT rowid, rank FROM chunks_fts WHERE chunks_fts MATCH ? "
            "ORDER BY rank LIMIT ?",
            (safe_query, n_candidates),
        )
        for rowid, rank in cursor.fetchall():
            bm25_scores[rowid] = 1.0 / (1.0 + abs(rank))
    except Exception:
        pass

    # Gather vector scores
    vec_scores: dict[int, float] = {}
    if has_sqlite_vec():
        query_vec = embed_query(query)
        query_blob = serialize_f32(query_vec)
        cursor = conn.execute(
            "SELECT rowid, distance FROM chunks_vec "
            "WHERE embedding MATCH ? ORDER BY distance LIMIT ?",
            (query_blob, n_candidates),
        )
        for rowid, distance in cursor.fetchall():
            vec_scores[rowid] = 1.0 - distance

    # Fuse scores
    all_rowids = set(bm25_scores.keys()) | set(vec_scores.keys())
    fused: list[tuple[int, float]] = []
    for rowid in all_rowids:
        v_score = vec_scores.get(rowid, 0.0)
        b_score = bm25_scores.get(rowid, 0.0)
        combined = vector_weight * v_score + bm25_weight * b_score
        if combined >= min_score:
            fused.append((rowid, combined))

    fused.sort(key=lambda x: x[1], reverse=True)

    results = []
    for rowid, score in fused[:limit]:
        chunk = _fetch_chunk_by_rowid(conn, rowid)
        if chunk:
            results.append(_row_to_result(chunk, score))

    return results
