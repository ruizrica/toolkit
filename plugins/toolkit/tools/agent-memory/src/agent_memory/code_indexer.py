# ABOUTME: Code indexing pipeline — discover, parse, and store code structure in SQLite.
# ABOUTME: Supports change detection via file hash to skip unchanged files.

import hashlib
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from .parser import CodeNode, detect_language, parse_file
from .tree import store_nodes

# Directories to always skip during discovery
_SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    ".tox", ".mypy_cache", ".pytest_cache", "dist", "build",
    ".next", ".nuxt", "coverage", ".cache", ".eggs",
    "vendor", "target",
}

# File extensions to index (must match parser.detect_language support)
_CODE_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".rs", ".go",
    ".java", ".rb", ".c", ".cpp", ".h", ".hpp",
    ".cs", ".swift", ".kt", ".lua", ".sh", ".bash",
}


@dataclass
class CodeIndexStats:
    """Statistics from a code indexing run."""
    files_indexed: int = 0
    files_skipped: int = 0
    nodes_created: int = 0


def discover_code_files(root_path: str) -> list[Path]:
    """Find all code files under root_path recursively.

    Skips common non-source directories (node_modules, .git, etc.)
    and non-code files.
    """
    root = Path(root_path)
    if not root.exists():
        raise ValueError(f"Code index root does not exist: {root_path}")
    if not root.is_dir():
        raise ValueError(f"Code index root must be a directory: {root_path}")

    files: list[Path] = []

    def _walk(directory: Path) -> None:
        try:
            entries = sorted(directory.iterdir())
        except PermissionError:
            return
        for entry in entries:
            if entry.is_dir():
                if entry.name not in _SKIP_DIRS and not entry.name.startswith("."):
                    _walk(entry)
            elif entry.is_file() and entry.suffix in _CODE_EXTENSIONS:
                files.append(entry)

    _walk(root)
    return files


def _file_hash(path: Path) -> str:
    """Return SHA-256 hex digest of file contents."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _file_changed(conn: sqlite3.Connection, path: Path, current_hash: str) -> bool:
    """Check if file has changed since last index."""
    cursor = conn.execute("SELECT hash FROM code_files WHERE path = ?", (str(path),))
    row = cursor.fetchone()
    if row is None:
        return True
    return row[0] != current_hash


def _update_file_record(
    conn: sqlite3.Connection, path: Path, file_hash: str, repo: str
) -> None:
    """Insert or update file record for change detection."""
    stat = path.stat()
    conn.execute(
        "INSERT OR REPLACE INTO code_files (path, repo, hash, mtime, size) "
        "VALUES (?, ?, ?, ?, ?)",
        (str(path), repo, file_hash, stat.st_mtime, stat.st_size),
    )


def _count_nodes(nodes: list[CodeNode]) -> int:
    """Count total nodes including children recursively."""
    count = 0
    for node in nodes:
        count += 1
        count += _count_nodes(node.children)
    return count


def index_codebase(
    conn: sqlite3.Connection,
    root_path: str,
) -> CodeIndexStats:
    """Full code indexing pipeline: discover → parse → store.

    Skips files that haven't changed since last index.
    """
    stats = CodeIndexStats()
    repo_path = str(Path(root_path).resolve())
    files = discover_code_files(root_path)

    for path in files:
        fhash = _file_hash(path)
        if not _file_changed(conn, path, fhash):
            stats.files_skipped += 1
            continue

        try:
            source = path.read_bytes()
        except (OSError, UnicodeDecodeError):
            stats.files_skipped += 1
            continue

        language = detect_language(str(path))
        if language is None:
            stats.files_skipped += 1
            continue

        nodes = parse_file(source, str(path), language)
        if not nodes:
            # File parsed but had no extractable nodes — still record it
            _update_file_record(conn, path, fhash, repo_path)
            stats.files_indexed += 1
            continue

        # Store the tree
        store_nodes(conn, nodes, repo_path=repo_path)
        _update_file_record(conn, path, fhash, repo_path)
        conn.commit()

        node_count = _count_nodes(nodes)
        stats.files_indexed += 1
        stats.nodes_created += node_count

    return stats
