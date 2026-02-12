# ABOUTME: CRUD operations for agent-memory — add, get, list memories.
# ABOUTME: Handles embedding and storage in chunks, FTS, and vec tables.

import sqlite3

from .db import has_sqlite_vec
from .embedder import content_hash, embed_texts, serialize_f32


def add_memory(
    conn: sqlite3.Connection,
    text: str,
    source: str = "manual",
    tags: str = "",
) -> str:
    """Add a new memory chunk to the database.

    Embeds the text and stores it in chunks, FTS, and vec tables.
    Returns the chunk ID.
    """
    c_hash = content_hash(text)
    chunk_id = content_hash(f"manual:{c_hash}:{tags}")

    conn.execute(
        "INSERT OR REPLACE INTO chunks "
        "(id, path, source, start_line, end_line, hash, model, text) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (chunk_id, f"manual:{tags}" if tags else "manual", source,
         0, 0, c_hash, "", text),
    )

    # Get rowid
    cursor = conn.execute("SELECT rowid FROM chunks WHERE id = ?", (chunk_id,))
    rowid = cursor.fetchone()[0]

    # FTS
    conn.execute(
        "INSERT OR REPLACE INTO chunks_fts (rowid, text) VALUES (?, ?)",
        (rowid, text),
    )

    # Vec
    if has_sqlite_vec():
        vectors = embed_texts([text])
        if vectors:
            blob = serialize_f32(vectors[0])
            conn.execute(
                "INSERT OR REPLACE INTO chunks_vec (rowid, embedding) VALUES (?, ?)",
                (rowid, blob),
            )

    conn.commit()
    return chunk_id


def get_memory(conn: sqlite3.Connection, chunk_id: str) -> dict | None:
    """Retrieve a memory chunk by its ID. Returns None if not found."""
    cursor = conn.execute(
        "SELECT id, text, path, source, start_line, end_line, created_at "
        "FROM chunks WHERE id = ?",
        (chunk_id,),
    )
    row = cursor.fetchone()
    if row is None:
        return None
    return {
        "id": row[0],
        "text": row[1],
        "path": row[2],
        "source": row[3],
        "start_line": row[4],
        "end_line": row[5],
        "created_at": row[6],
    }


def list_memories(
    conn: sqlite3.Connection,
    source: str | None = None,
    limit: int = 20,
) -> list[dict]:
    """List memory chunks, optionally filtered by source type."""
    if source:
        cursor = conn.execute(
            "SELECT id, text, path, source, start_line, end_line, created_at "
            "FROM chunks WHERE source = ? ORDER BY created_at DESC LIMIT ?",
            (source, limit),
        )
    else:
        cursor = conn.execute(
            "SELECT id, text, path, source, start_line, end_line, created_at "
            "FROM chunks ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )

    return [
        {
            "id": row[0],
            "text": row[1],
            "path": row[2],
            "source": row[3],
            "start_line": row[4],
            "end_line": row[5],
            "created_at": row[6],
        }
        for row in cursor.fetchall()
    ]
