# ABOUTME: Indexing pipeline — scan markdown files, chunk, embed, and store in SQLite.
# ABOUTME: Supports change detection via file hash to skip unchanged files.

import glob
import hashlib
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from .chunker import Chunk, chunk_markdown
from .db import has_sqlite_vec
from .embedder import content_hash, embed_texts, serialize_f32


@dataclass
class IndexStats:
    """Statistics from an indexing run."""
    files_indexed: int = 0
    files_skipped: int = 0
    chunks_created: int = 0


def classify_source(path: str) -> str:
    """Classify a file path into a source type."""
    if "daily-logs" in path:
        return "daily"
    if "sessions" in path:
        return "session"
    if "MEMORY.md" in path:
        return "memory"
    return "other"


def discover_files(patterns: list[str]) -> list[Path]:
    """Expand glob patterns and return sorted list of matching files."""
    files = []
    for pattern in patterns:
        files.extend(Path(p) for p in glob.glob(pattern))
    return sorted(set(files))


def _file_hash(path: Path) -> str:
    """Return SHA-256 hex digest of file contents."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _file_changed(conn: sqlite3.Connection, path: Path, current_hash: str) -> bool:
    """Check if file has changed since last index."""
    cursor = conn.execute("SELECT hash FROM files WHERE path = ?", (str(path),))
    row = cursor.fetchone()
    if row is None:
        return True
    return row[0] != current_hash


def _update_file_record(conn: sqlite3.Connection, path: Path, file_hash: str) -> None:
    """Insert or update file record for change detection."""
    stat = path.stat()
    conn.execute(
        "INSERT OR REPLACE INTO files (path, hash, mtime, size) VALUES (?, ?, ?, ?)",
        (str(path), file_hash, stat.st_mtime, stat.st_size),
    )


def _delete_chunks_for_file(conn: sqlite3.Connection, path: str) -> None:
    """Delete all chunks (and related FTS/vec entries) for a given file path."""
    # Get rowids before deleting
    cursor = conn.execute("SELECT rowid FROM chunks WHERE path = ?", (path,))
    rowids = [row[0] for row in cursor.fetchall()]

    if rowids:
        placeholders = ",".join("?" for _ in rowids)
        # Delete from FTS
        conn.execute(
            f"DELETE FROM chunks_fts WHERE rowid IN ({placeholders})", rowids
        )
        # Delete from vec if available
        if has_sqlite_vec():
            conn.execute(
                f"DELETE FROM chunks_vec WHERE rowid IN ({placeholders})", rowids
            )
        # Delete from chunks
        conn.execute(f"DELETE FROM chunks WHERE path = ?", (path,))


def _store_chunks(
    conn: sqlite3.Connection,
    chunks: list[Chunk],
    vectors: list[list[float]],
    source: str,
    model: str,
) -> int:
    """Store chunks with their embeddings in all three tables."""
    count = 0
    for chunk, vector in zip(chunks, vectors):
        c_hash = content_hash(chunk.text)
        chunk_id = content_hash(f"{chunk.source_path}:{chunk.start_line}:{c_hash}")

        conn.execute(
            "INSERT OR REPLACE INTO chunks "
            "(id, path, source, start_line, end_line, hash, model, text) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (chunk_id, chunk.source_path, source, chunk.start_line,
             chunk.end_line, c_hash, model, chunk.text),
        )

        # Get the rowid of the just-inserted chunk
        cursor = conn.execute(
            "SELECT rowid FROM chunks WHERE id = ?", (chunk_id,)
        )
        rowid = cursor.fetchone()[0]

        # Insert into FTS
        conn.execute(
            "INSERT OR REPLACE INTO chunks_fts (rowid, text) VALUES (?, ?)",
            (rowid, chunk.text),
        )

        # Insert into vec if available
        if has_sqlite_vec():
            blob = serialize_f32(vector)
            conn.execute(
                "INSERT OR REPLACE INTO chunks_vec (rowid, embedding) VALUES (?, ?)",
                (rowid, blob),
            )

        count += 1
    return count


def index_all(conn: sqlite3.Connection, patterns: list[str]) -> IndexStats:
    """Full indexing pipeline: discover → chunk → embed → store.

    Skips files that haven't changed since last index.
    """
    stats = IndexStats()
    files = discover_files(patterns)

    for path in files:
        fhash = _file_hash(path)
        if not _file_changed(conn, path, fhash):
            stats.files_skipped += 1
            continue

        text = path.read_text(encoding="utf-8")
        chunks = chunk_markdown(text, source_path=str(path))

        if not chunks:
            stats.files_skipped += 1
            continue

        # Embed all chunks
        texts = [c.text for c in chunks]
        vectors = embed_texts(texts)

        source = classify_source(str(path))

        # Atomic: delete old, insert new
        _delete_chunks_for_file(conn, str(path))
        created = _store_chunks(conn, chunks, vectors, source, "")
        _update_file_record(conn, path, fhash)
        conn.commit()

        stats.files_indexed += 1
        stats.chunks_created += created

    return stats
