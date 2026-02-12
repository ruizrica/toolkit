# ABOUTME: SQLite database schema and connection management for agent-memory.
# ABOUTME: Creates tables for chunks, FTS5, sqlite-vec, files, embedding cache, and meta.

import sqlite3
from pathlib import Path

_vec_available = None


def has_sqlite_vec() -> bool:
    """Check if sqlite-vec extension is available."""
    global _vec_available
    if _vec_available is None:
        try:
            import sqlite_vec  # noqa: F401
            _vec_available = True
        except ImportError:
            _vec_available = False
    return _vec_available


def _load_vec(conn: sqlite3.Connection) -> None:
    """Load sqlite-vec extension into connection."""
    if has_sqlite_vec():
        import sqlite_vec
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)


def init_db(db_path: Path) -> sqlite3.Connection:
    """Initialize the database: create tables and load extensions.

    Returns an open connection with WAL mode and foreign keys enabled.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    _load_vec(conn)

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS chunks (
            id        TEXT PRIMARY KEY,
            path      TEXT NOT NULL,
            source    TEXT NOT NULL,
            start_line INTEGER NOT NULL,
            end_line  INTEGER NOT NULL,
            hash      TEXT NOT NULL,
            model     TEXT NOT NULL DEFAULT '',
            text      TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS files (
            path  TEXT PRIMARY KEY,
            hash  TEXT NOT NULL,
            mtime REAL NOT NULL,
            size  INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS embedding_cache (
            hash      TEXT PRIMARY KEY,
            embedding BLOB NOT NULL
        );

        CREATE TABLE IF NOT EXISTS meta (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
            text,
            content='chunks',
            content_rowid='rowid',
            tokenize='porter unicode61'
        );
    """)

    # Create vec0 table if sqlite-vec is available
    if has_sqlite_vec():
        # vec0 tables don't support IF NOT EXISTS, so check first
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='chunks_vec'"
        )
        if cursor.fetchone() is None:
            from agent_memory.config import EMBEDDING_DIM
            conn.execute(
                f"CREATE VIRTUAL TABLE chunks_vec USING vec0("
                f"  embedding float[{EMBEDDING_DIM}] distance_metric=cosine"
                f")"
            )

    conn.commit()
    return conn


def meta_set(conn: sqlite3.Connection, key: str, value: str) -> None:
    """Set a key-value pair in the meta table."""
    conn.execute(
        "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
        (key, value),
    )
    conn.commit()


def meta_get(conn: sqlite3.Connection, key: str, default: str | None = None) -> str | None:
    """Get a value from the meta table, returning default if not found."""
    cursor = conn.execute("SELECT value FROM meta WHERE key = ?", (key,))
    row = cursor.fetchone()
    return row[0] if row else default
