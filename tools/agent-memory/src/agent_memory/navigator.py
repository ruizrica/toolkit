# ABOUTME: FTS-based beam search navigator for code trees.
# ABOUTME: Descends the tree by scoring children via FTS, returning navigation traces.

import sqlite3
from dataclasses import dataclass, field
from typing import Any


@dataclass
class NavigationStep:
    """One step in the navigation trace."""
    depth: int
    candidates: list[str]
    selected: list[str]


@dataclass
class NavigationResult:
    """Result of a tree navigation query."""
    nodes: list[dict[str, Any]]
    steps: list[NavigationStep]


def _fts_score_nodes(
    conn: sqlite3.Connection,
    query: str,
    node_ids: list[int],
    limit: int,
) -> list[tuple[int, float]]:
    """Score a set of nodes using FTS5 match ranking.

    Returns (node_id, score) pairs sorted by score descending.
    """
    if not node_ids:
        return []

    # Use FTS to find matches, then filter to our candidate set
    placeholders = ",".join("?" for _ in node_ids)
    try:
        cursor = conn.execute(
            f"SELECT cn.id, f.rank "
            f"FROM code_nodes_fts f "
            f"JOIN code_nodes cn ON cn.id = f.rowid "
            f"WHERE code_nodes_fts MATCH ? "
            f"AND cn.id IN ({placeholders}) "
            f"ORDER BY f.rank "
            f"LIMIT ?",
            [query] + node_ids + [limit],
        )
        results = []
        for row in cursor.fetchall():
            score = 1.0 / (1.0 + abs(row[1]))
            results.append((row[0], score))
        return results
    except Exception:
        return []


def _get_all_node_ids(conn: sqlite3.Connection, repo_path: str | None = None) -> list[int]:
    """Get all node IDs, optionally filtered by repo."""
    if repo_path:
        cursor = conn.execute(
            "SELECT id FROM code_nodes WHERE repo_path = ?", (repo_path,)
        )
    else:
        cursor = conn.execute("SELECT id FROM code_nodes")
    return [row[0] for row in cursor.fetchall()]


def _get_node(conn: sqlite3.Connection, node_id: int) -> dict[str, Any] | None:
    """Get node dict by ID."""
    from .tree import get_node
    return get_node(conn, node_id)


def _get_children_ids(conn: sqlite3.Connection, node_id: int) -> list[int]:
    """Get child node IDs."""
    cursor = conn.execute(
        "SELECT id FROM code_nodes WHERE parent_id = ?", (node_id,)
    )
    return [row[0] for row in cursor.fetchall()]


def navigate(
    conn: sqlite3.Connection,
    query: str,
    repo_path: str | None = None,
    beam_width: int = 3,
    max_depth: int = 5,
) -> NavigationResult:
    """Navigate the code tree using FTS-based beam search.

    Starts from all nodes, scores them against the query using FTS5,
    then expands the top-scoring nodes' children iteratively.

    Returns a NavigationResult with matching nodes and the full trace.
    """
    steps: list[NavigationStep] = []

    # Start: score all nodes against the query
    all_ids = _get_all_node_ids(conn, repo_path)
    if not all_ids:
        return NavigationResult(nodes=[], steps=[])

    # Score all nodes via FTS
    scored = _fts_score_nodes(conn, query, all_ids, limit=beam_width * 10)
    if not scored:
        return NavigationResult(nodes=[], steps=[])

    # Take the top beam_width matches
    top_ids = [nid for nid, _ in scored[:beam_width]]

    # Get candidate names for trace
    candidate_names = []
    for nid, _ in scored[:beam_width * 2]:
        node = _get_node(conn, nid)
        if node:
            candidate_names.append(node["name"])

    selected_names = []
    for nid in top_ids:
        node = _get_node(conn, nid)
        if node:
            selected_names.append(node["name"])

    steps.append(NavigationStep(
        depth=0,
        candidates=candidate_names,
        selected=selected_names,
    ))

    # Beam search descent: expand children of selected nodes
    current_ids = top_ids
    for depth in range(1, max_depth + 1):
        # Collect all children of current beam
        child_ids = []
        for nid in current_ids:
            child_ids.extend(_get_children_ids(conn, nid))

        if not child_ids:
            break

        # Score children
        child_scored = _fts_score_nodes(conn, query, child_ids, limit=beam_width)
        if not child_scored:
            break

        # Select top beam_width children
        new_ids = [nid for nid, _ in child_scored[:beam_width]]

        child_candidate_names = []
        for nid, _ in child_scored:
            node = _get_node(conn, nid)
            if node:
                child_candidate_names.append(node["name"])

        child_selected_names = []
        for nid in new_ids:
            node = _get_node(conn, nid)
            if node:
                child_selected_names.append(node["name"])

        steps.append(NavigationStep(
            depth=depth,
            candidates=child_candidate_names,
            selected=child_selected_names,
        ))

        current_ids = current_ids + new_ids

    # Collect all unique result nodes
    seen = set()
    result_nodes = []
    for nid in current_ids:
        if nid in seen:
            continue
        seen.add(nid)
        node = _get_node(conn, nid)
        if node:
            result_nodes.append(node)

    return NavigationResult(nodes=result_nodes, steps=steps)


def format_navigation_result(result: NavigationResult) -> str:
    """Format a NavigationResult as human-readable text."""
    if not result.nodes:
        return "No matching code found."

    lines = []

    # Show navigation trace
    if result.steps:
        lines.append("Navigation trace:")
        for step in result.steps:
            lines.append(
                f"  depth {step.depth}: "
                f"scored [{', '.join(step.candidates[:5])}] "
                f"-> selected [{', '.join(step.selected)}]"
            )
        lines.append("")

    # Show matched nodes
    lines.append(f"Found {len(result.nodes)} node(s):")
    for node in result.nodes:
        node_type = node.get("node_type", "?")
        name = node.get("qualified_name") or node.get("name", "?")
        file_path = node.get("file_path", "?")
        start = node.get("start_line", "?")
        end = node.get("end_line", "?")
        sig = node.get("signature", "")

        lines.append(f"  [{node_type}] {name}")
        lines.append(f"    {file_path}:{start}-{end}")
        if sig:
            lines.append(f"    {sig}")
        doc = node.get("docstring", "")
        if doc:
            lines.append(f"    \"{doc}\"")
        lines.append("")

    return "\n".join(lines)
