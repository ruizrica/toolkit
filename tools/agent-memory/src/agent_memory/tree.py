# ABOUTME: Tree storage and retrieval for code nodes in SQLite.
# ABOUTME: Insert, query children, walk paths, and resolve cross-references.

import sqlite3
from typing import Any

from .parser import CodeNode


def _node_to_dict(row: tuple, columns: list[str]) -> dict[str, Any]:
    """Convert a database row to a dictionary."""
    return dict(zip(columns, row))


_NODE_COLUMNS = [
    "id", "repo_path", "file_path", "node_type", "name", "qualified_name",
    "parent_id", "start_line", "end_line", "signature", "docstring",
    "body_hash", "summary", "depth",
]


def _insert_node(
    conn: sqlite3.Connection,
    node: CodeNode,
    repo_path: str,
    parent_id: int | None,
    depth: int,
) -> int:
    """Insert a single CodeNode and return its row ID."""
    cursor = conn.execute(
        "INSERT INTO code_nodes "
        "(repo_path, file_path, node_type, name, qualified_name, "
        "parent_id, start_line, end_line, signature, docstring, "
        "body_hash, summary, depth) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            repo_path, node.file_path, node.node_type, node.name,
            node.qualified_name, parent_id, node.start_line, node.end_line,
            node.signature, node.docstring, node.body_hash, "", depth,
        ),
    )
    node_id = cursor.lastrowid

    # Insert into FTS
    conn.execute(
        "INSERT INTO code_nodes_fts (rowid, name, qualified_name, summary, "
        "signature, docstring) VALUES (?, ?, ?, ?, ?, ?)",
        (node_id, node.name, node.qualified_name, "", node.signature,
         node.docstring),
    )

    return node_id


def _insert_tree(
    conn: sqlite3.Connection,
    node: CodeNode,
    repo_path: str,
    parent_id: int | None,
    depth: int,
) -> None:
    """Recursively insert a CodeNode tree."""
    node_id = _insert_node(conn, node, repo_path, parent_id, depth)
    for child in node.children:
        _insert_tree(conn, child, repo_path, node_id, depth + 1)


def store_nodes(
    conn: sqlite3.Connection,
    nodes: list[CodeNode],
    repo_path: str,
) -> None:
    """Store a list of top-level CodeNode trees into the database.

    Clears previous entries for the same file paths before inserting,
    making this operation idempotent for re-indexing.
    """
    # Collect all file paths from the nodes
    file_paths = set()
    def _collect_paths(n: CodeNode) -> None:
        file_paths.add(n.file_path)
        for c in n.children:
            _collect_paths(c)

    for node in nodes:
        _collect_paths(node)

    # Delete existing nodes (and FTS entries) for these files
    for fp in file_paths:
        # Get IDs to delete from FTS
        cursor = conn.execute(
            "SELECT id FROM code_nodes WHERE file_path = ? AND repo_path = ?",
            (fp, repo_path),
        )
        ids = [row[0] for row in cursor.fetchall()]
        if ids:
            placeholders = ",".join("?" for _ in ids)
            conn.execute(
                f"DELETE FROM code_nodes_fts WHERE rowid IN ({placeholders})",
                ids,
            )
            conn.execute(
                f"DELETE FROM code_refs WHERE source_id IN ({placeholders})",
                ids,
            )
            conn.execute(
                f"DELETE FROM code_nodes WHERE file_path = ? AND repo_path = ?",
                (fp, repo_path),
            )

    # Insert new trees
    for node in nodes:
        _insert_tree(conn, node, repo_path, None, 0)

    conn.commit()


def get_node(conn: sqlite3.Connection, node_id: int) -> dict[str, Any] | None:
    """Get a single node by its ID."""
    cursor = conn.execute(
        f"SELECT {', '.join(_NODE_COLUMNS)} FROM code_nodes WHERE id = ?",
        (node_id,),
    )
    row = cursor.fetchone()
    if row is None:
        return None
    return _node_to_dict(row, _NODE_COLUMNS)


def get_children(conn: sqlite3.Connection, parent_id: int) -> list[dict[str, Any]]:
    """Get all direct children of a node."""
    cursor = conn.execute(
        f"SELECT {', '.join(_NODE_COLUMNS)} FROM code_nodes WHERE parent_id = ? "
        "ORDER BY start_line",
        (parent_id,),
    )
    return [_node_to_dict(row, _NODE_COLUMNS) for row in cursor.fetchall()]


def get_roots(
    conn: sqlite3.Connection,
    repo_path: str | None = None,
) -> list[dict[str, Any]]:
    """Get all top-level nodes (no parent).

    Optionally filter by repo_path.
    """
    if repo_path:
        cursor = conn.execute(
            f"SELECT {', '.join(_NODE_COLUMNS)} FROM code_nodes "
            "WHERE parent_id IS NULL AND repo_path = ? "
            "ORDER BY file_path, start_line",
            (repo_path,),
        )
    else:
        cursor = conn.execute(
            f"SELECT {', '.join(_NODE_COLUMNS)} FROM code_nodes "
            "WHERE parent_id IS NULL ORDER BY file_path, start_line",
        )
    return [_node_to_dict(row, _NODE_COLUMNS) for row in cursor.fetchall()]


def get_path_to_root(conn: sqlite3.Connection, node_id: int) -> list[dict[str, Any]]:
    """Walk up from a node to the root, returning the path (node first, root last)."""
    path = []
    current_id = node_id
    while current_id is not None:
        node = get_node(conn, current_id)
        if node is None:
            break
        path.append(node)
        current_id = node["parent_id"]
    return path


def store_refs(conn: sqlite3.Connection, refs: list[dict]) -> None:
    """Store cross-reference records.

    Each ref dict should have: source_id, target_name, ref_type, line.
    target_id is optional (resolved later via resolve_refs).
    """
    for ref in refs:
        conn.execute(
            "INSERT INTO code_refs (source_id, target_id, target_name, ref_type, line) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                ref["source_id"],
                ref.get("target_id"),
                ref["target_name"],
                ref["ref_type"],
                ref.get("line", 0),
            ),
        )
    conn.commit()


def resolve_refs(
    conn: sqlite3.Connection,
    source_id: int,
) -> list[dict[str, Any]]:
    """Get cross-references from a node, resolving target names to IDs where possible."""
    cursor = conn.execute(
        "SELECT cr.id, cr.source_id, cr.target_id, cr.target_name, cr.ref_type, cr.line "
        "FROM code_refs cr WHERE cr.source_id = ?",
        (source_id,),
    )
    results = []
    for row in cursor.fetchall():
        ref = {
            "id": row[0],
            "source_id": row[1],
            "target_id": row[2],
            "target_name": row[3],
            "ref_type": row[4],
            "line": row[5],
        }
        # Try to resolve target_id if not already set
        if ref["target_id"] is None:
            target_cursor = conn.execute(
                "SELECT id FROM code_nodes WHERE name = ? OR qualified_name = ? LIMIT 1",
                (ref["target_name"], ref["target_name"]),
            )
            target_row = target_cursor.fetchone()
            if target_row:
                ref["target_id"] = target_row[0]
                # Update in DB for future lookups
                conn.execute(
                    "UPDATE code_refs SET target_id = ? WHERE id = ?",
                    (ref["target_id"], ref["id"]),
                )
        results.append(ref)
    if results:
        conn.commit()
    return results
